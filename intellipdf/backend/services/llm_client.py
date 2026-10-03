"""LLM client with a free-tier fallback chain.

Order of preference (configurable with ``DEFAULT_LLM``):

1. **Groq** - ``llama-3.1-70b-versatile`` (free tier, needs ``GROQ_API_KEY``)
2. **Google Gemini** - ``gemini-1.5-flash`` (free tier, needs ``GEMINI_API_KEY``)
3. **Ollama** - local ``llama3`` at ``http://localhost:11434`` (free, offline)

If every provider is unavailable, :meth:`LLMClient.generate` returns
``ok=False`` and the calling service falls back to a deterministic
*extractive* answer built from the retrieved chunks, so the product always
produces a source-grounded response.
"""

from __future__ import annotations

import json
import logging
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any

import requests

from backend.config import (
    DEFAULT_LLM,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SECONDS,
    OLLAMA_MODEL,
    OLLAMA_URL,
)

LOGGER = logging.getLogger(__name__)

GROQ = "groq"
GEMINI = "gemini"
OLLAMA = "ollama"
OFFLINE = "offline-extractive"

#: How long an Ollama reachability probe stays cached (seconds).
OLLAMA_PROBE_TTL = 30.0
#: Probe timeout - a closed port must not stall a request.
OLLAMA_PROBE_TIMEOUT = 1.0

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)
_ARRAY_RE = re.compile(r"(\[.*\]|\{.*\})", re.DOTALL)

#: Cached result of the last Ollama probe: (timestamp, reachable).
_ollama_probe: tuple[float, bool] | None = None


@dataclass
class LLMResponse:
    """Result of a generation attempt."""

    text: str
    provider: str
    model: str
    ok: bool = True
    error: str | None = None
    attempts: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:  # pragma: no cover - trivial
        return self.ok and bool(self.text.strip())


# ── Providers ────────────────────────────────────────────────────────────


def try_groq(prompt: str, system: str, max_tokens: int, temperature: float) -> LLMResponse:
    """Generate with Groq (free tier). Raises on failure."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY, timeout=LLM_TIMEOUT_SECONDS)
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    text = (completion.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("Groq returned an empty completion")
    return LLMResponse(text=text, provider=GROQ, model=GROQ_MODEL)


def try_gemini(prompt: str, system: str, max_tokens: int, temperature: float) -> LLMResponse:
    """Generate with Google Gemini (free tier). Raises on failure."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL, system_instruction=system
    )
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        },
    )
    text = (getattr(response, "text", "") or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty completion")
    return LLMResponse(text=text, provider=GEMINI, model=GEMINI_MODEL)


def try_ollama(prompt: str, system: str, max_tokens: int, temperature: float) -> LLMResponse:
    """Generate with a local Ollama model. Raises on failure."""
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system}\n\n{prompt}",
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    http = requests.post(url, json=payload, timeout=LLM_TIMEOUT_SECONDS)
    http.raise_for_status()
    body = http.json()
    text = (body.get("response") or "").strip()
    if not text:
        raise RuntimeError("Ollama returned an empty response")
    return LLMResponse(text=text, provider=OLLAMA, model=OLLAMA_MODEL)


#: Ordered fallback chain, honouring ``DEFAULT_LLM`` as the preferred provider.
def _build_chain() -> list[str]:
    order = [GROQ, GEMINI, OLLAMA]
    if DEFAULT_LLM in order:
        order.remove(DEFAULT_LLM)
        order.insert(0, DEFAULT_LLM)
    return order


class LLMClient:
    """Tries each provider in order and returns the first success."""

    def __init__(self) -> None:
        self.chain = _build_chain()
        self.last_provider: str | None = None
        self._lock = threading.Lock()

    def generate(
        self,
        prompt: str,
        system: str = "You are a helpful assistant.",
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> LLMResponse:
        """Generate text, walking the fallback chain.

        Args:
            prompt: The user-style prompt (context + question + rules).
            system: System role message.
            max_tokens: Completion cap (default from config).
            temperature: Sampling temperature (default from config).

        Returns:
            An :class:`LLMResponse`; ``ok`` is ``False`` when every provider
            failed, with ``error`` describing the last failure.
        """
        tokens = max_tokens or LLM_MAX_TOKENS
        temp = LLM_TEMPERATURE if temperature is None else temperature
        handlers = {GROQ: try_groq, GEMINI: try_gemini, OLLAMA: try_ollama}

        attempts: list[str] = []
        for provider in self.chain:
            # Skip a local Ollama server that is not installed instead of
            # burning the connect timeout on every single request.
            if provider == OLLAMA and not ollama_available():
                attempts.append(f"{OLLAMA} -> not running (skipped)")
                continue
            handler = handlers[provider]
            try:
                response = handler(prompt, system, tokens, temp)
                response.attempts = attempts
                with self._lock:
                    self.last_provider = provider
                LOGGER.info("LLM answered via %s (%s)", provider, response.model)
                return response
            except Exception as exc:  # noqa: BLE001 - try the next provider
                message = f"{type(exc).__name__}: {exc}"
                attempts.append(f"{provider} -> {message}")
                LOGGER.warning("Provider %s failed: %s", provider, message)

        LOGGER.warning("All LLM providers failed; caller must use extractive mode.")
        return LLMResponse(
            text="",
            provider=OFFLINE,
            model="none",
            ok=False,
            error="; ".join(attempts) or "no provider available",
            attempts=attempts,
        )

    def health(self) -> dict[str, Any]:
        """Return per-provider availability for ``GET /health``."""
        status: dict[str, Any] = {
            GROQ: {"configured": bool(GROQ_API_KEY), "reachable": bool(GROQ_API_KEY)},
            GEMINI: {
                "configured": bool(GEMINI_API_KEY),
                "reachable": bool(GEMINI_API_KEY),
            },
            OLLAMA: {"configured": True, "reachable": ollama_available()},
            "chain": list(self.chain),
            "active": self.last_provider or "none",
        }
        status["any_available"] = any(
            bool(status[name]["reachable"]) for name in (GROQ, GEMINI, OLLAMA)
        )
        return status


def ollama_available(timeout: float = OLLAMA_PROBE_TIMEOUT) -> bool:
    """Return ``True`` when a local Ollama server answers (cached for 30 s).

    Some machines *time out* on a closed localhost port instead of refusing the
    connection, which would add seconds to every request, so the probe result
    is cached and the IPv4 loopback address is used directly.
    """
    global _ollama_probe
    now = time.monotonic()
    if _ollama_probe and now - _ollama_probe[0] < OLLAMA_PROBE_TTL:
        return _ollama_probe[1]
    url = OLLAMA_URL.replace("localhost", "127.0.0.1")
    reachable = False
    try:
        response = requests.get(f"{url}/api/tags", timeout=timeout)
        reachable = response.status_code == 200
    except Exception:  # noqa: BLE001 - offline is the normal case
        reachable = False
    _ollama_probe = (now, reachable)
    return reachable


# ── JSON helpers ─────────────────────────────────────────────────────────


def parse_json_block(raw: str) -> Any:
    """Parse JSON from an LLM reply, tolerating markdown fences and prose.

    Strategy: direct ``json.loads`` -> fenced block -> first balanced
    ``[...]``/``{...}`` in the text.  Returns ``None`` when nothing parses.
    """
    if not raw:
        return None
    text = raw.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fenced = _FENCE_RE.search(text)
    if fenced:
        try:
            return json.loads(fenced.group(1).strip())
        except json.JSONDecodeError:
            text = fenced.group(1).strip()

    match = _ARRAY_RE.search(text)
    if match:
        candidate = match.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        repaired = _repair_truncated_json(candidate)
        if repaired:
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                return None
    return None


def _repair_truncated_json(candidate: str) -> str | None:
    """Close an array/object that the model cut off mid-generation.

    Args:
        candidate: The raw ``[...]`` / ``{...}`` substring.

    Returns:
        A balanced JSON string, or ``None`` when the input is inside a string
        literal where repair would corrupt the data.
    """
    trimmed = candidate.rstrip().rstrip(",")
    if not trimmed:
        return None
    # Repairing mid-string (odd number of unescaped quotes) is unsafe.
    if trimmed.count('"') % 2 == 1:
        return None
    stack: list[str] = []
    in_string = False
    escaped = False
    for char in trimmed:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "[{":
            stack.append(char)
        elif char in "]}":
            if stack:
                stack.pop()
    if not stack:
        return None
    # Drop a dangling key like `"explanation":`
    tail = re.split(r'[",]', trimmed)[-1]
    if not tail.strip() or tail.strip().endswith(":"):
        trimmed = trimmed[: len(trimmed) - len(tail)]
    closers = {"[": "]", "{": "}"}
    return trimmed + "".join(closers[opener] for opener in reversed(stack))


def coerce_list(value: Any) -> list[Any]:
    """Return a list for ``value`` whether it is a list, a dict, or a scalar."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    return [value]


def as_list_of_text(value: Any, limit: int = 12) -> list[str]:
    """Normalise an LLM field into a clean ``list[str]``."""
    items: list[str] = []
    for entry in coerce_list(value):
        if isinstance(entry, str):
            text = entry.strip()
        elif isinstance(entry, dict):
            text = str(
                entry.get("point")
                or entry.get("missing")
                or entry.get("text")
                or entry.get("title")
                or ""
            ).strip()
        else:
            text = str(entry).strip()
        text = re.sub(r"^\s*[-*\d.)\]]+\s*", "", text)
        if text:
            items.append(text)
        if len(items) >= limit:
            break
    return items


#: Module-level singleton used by the routers and services.
llm_client = LLMClient()


def get_llm_client() -> LLMClient:
    """Return the process-wide LLM client singleton."""
    return llm_client