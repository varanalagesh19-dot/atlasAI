# atlas_core07 - Quick Start Guide (5 Minutes)

Get atlas_core07 running in 5 minutes with zero configuration.

## Prerequisites

- **Python 3.8+** - [Download](https://python.org)
- **Node.js 16+** - [Download](https://nodejs.org)

## Installation

### 1. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

You should see:
```
Running on http://127.0.0.1:5000
```

### 2. Start Frontend (New Terminal)

```bash
cd frontend
npm install
npm run dev
```

You should see:
```
Local: http://localhost:5173
```

### 3. Open Browser

Visit: **http://localhost:5173**

## ✅ You're Done!

atlas_core07 is now running with **demo mode**. Create a conversation and start chatting!

## Next Steps

### Add Real AI (Optional)

1. Get API key:
   - **OpenAI**: https://platform.openai.com/api-keys
   - **Gemini**: https://aistudio.google.com/app/apikey
   - **Claude**: https://console.anthropic.com/

2. Create `backend/.env`:
   ```env
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-your-key
   ```

3. Restart backend: `python app.py`

### Customize

- **Colors**: Edit `frontend/src/styles/globals.css`
- **Welcome**: Edit `frontend/src/App.jsx`
- **API**: See `API.md`

## Help

- **Installation issues**: See `INSTALLATION_GUIDE.md`
- **Configuration**: See `README.md`
- **API Reference**: See `API.md`
- **Advanced**: See `ADVANCED_FEATURES.md`

---

**That's it! You're ready to build with atlas_core07.** 🚀
