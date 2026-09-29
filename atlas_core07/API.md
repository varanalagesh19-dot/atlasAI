# atlas_core07 - API Reference

Complete API documentation for atlas_core07 backend.

## Base URL

```
http://localhost:5000/api
```

## Endpoints

### Health Check

**GET** `/health`

```bash
curl http://localhost:5000/api/health
```

**Response:**
```json
{
  "status": "ok",
  "message": "atlas_core07 backend is running"
}
```

---

### Conversations

#### List All

**GET** `/conversations`

```bash
curl http://localhost:5000/api/conversations
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "My Chat",
    "created_at": "2026-01-15T10:30:00",
    "updated_at": "2026-01-15T10:35:00",
    "model": "atlas_smart",
    "pinned": false,
    "messages": []
  }
]
```

#### Create

**POST** `/conversations`

```bash
curl -X POST http://localhost:5000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "New Chat", "model": "atlas_smart"}'
```

**Response:** `201 Created`

#### Get Specific

**GET** `/conversations/{id}`

**Response:** Conversation with messages

#### Update

**PUT** `/conversations/{id}`

```bash
curl -X PUT http://localhost:5000/api/conversations/{id} \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

#### Delete

**DELETE** `/conversations/{id}`

#### Search

**GET** `/conversations/search?q=query`

---

### Messages

#### Add Message

**POST** `/conversations/{id}/messages`

```bash
curl -X POST http://localhost:5000/api/conversations/{id}/messages \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "Hello"}'
```

---

### Chat (AI Response)

**POST** `/chat`

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "model": "atlas_smart",
    "temperature": 0.7,
    "max_tokens": 2000
  }'
```

**Response:**
```json
{
  "content": "Hello! How can I help?",
  "model": "atlas_smart",
  "provider": "MockProvider"
}
```

---

### Models

**GET** `/models`

Get available AI models.

**Response:**
```json
{
  "models": [
    {"id": "atlas_smart", "name": "atlas Smart"},
    {"id": "atlas_fast", "name": "atlas Fast"}
  ],
  "provider": "MockProvider"
}
```

---

## Python Example

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Create conversation
conv = requests.post(f"{BASE_URL}/conversations", 
                    json={"title": "My Chat"}).json()
conv_id = conv['id']

# Add message and get response
messages = [{"role": "user", "content": "Hello"}]
response = requests.post(f"{BASE_URL}/chat",
                        json={"messages": messages}).json()

print(response['content'])
```

---

## JavaScript Example

```javascript
const BASE_URL = 'http://localhost:5000/api'

async function createChat() {
  const response = await fetch(`${BASE_URL}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'My Chat' })
  })
  return await response.json()
}

async function sendMessage(convId, content) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: [{ role: 'user', content }]
    })
  })
  return await response.json()
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

---

**For more details, see README.md and ADVANCED_FEATURES.md**
