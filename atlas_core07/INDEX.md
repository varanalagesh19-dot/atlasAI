# atlas_core07 - Getting Started Guide

Welcome to **atlas_core07** - an advanced AI chatbot platform!

## ⚡ Quick Start (Choose One)

### Option A: Automatic Setup (Recommended)
```bash
chmod +x SETUP.sh
./SETUP.sh
```

### Option B: Manual 5-Minute Start

**Terminal 1:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Terminal 2:**
```bash
cd frontend
npm install
npm run dev
```

**Browser:** Open http://localhost:5173

---

## 📚 Documentation Map

| Document | Purpose | Time |
|----------|---------|------|
| **This File** | You are here | - |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute start | 5 min |
| [README.md](README.md) | Full overview | 15 min |
| [INSTALLATION.md](INSTALLATION.md) | Detailed setup | 20 min |
| [API.md](API.md) | API reference | 15 min |
| [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) | Customization | 20 min |

## 🎯 What You Can Do

### Right Now (No Setup)
- ✅ Create conversations
- ✅ Send messages
- ✅ Get demo AI responses
- ✅ Toggle dark mode
- ✅ Try on mobile

### After Setup (5 min)
- ✅ Real AI responses (add API key)
- ✅ Switch AI providers
- ✅ Customize colors
- ✅ Deploy to Docker

### Advanced
- ✅ Add custom AI provider
- ✅ Deploy to production
- ✅ Add authentication
- ✅ Extend features

---

## 🚀 Getting atlas_core07 Running

### Step 1: Check Prerequisites
- Python 3.8+: `python --version`
- Node.js 16+: `node --version`

### Step 2: Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
✅ You should see: `Running on http://127.0.0.1:5000`

### Step 3: Start Frontend
```bash
cd frontend
npm install
npm run dev
```
✅ You should see: `Local: http://localhost:5173`

### Step 4: Open Browser
Visit: **http://localhost:5173**

✅ **atlas_core07 is running!**

---

## 🤖 Add Real AI (Optional)

### Get an API Key
- **OpenAI**: https://platform.openai.com/api-keys
- **Gemini**: https://aistudio.google.com/app/apikey
- **Claude**: https://console.anthropic.com/

### Configure
Create `backend/.env`:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

### Restart Backend
```bash
python app.py
```

---

## 🎨 Customize atlas_core07

### Change Colors
Edit `frontend/src/styles/globals.css`:
```css
--color-accent: #your-color;
```

### Change Welcome Message
Edit `frontend/src/App.jsx` in the `welcome` section

### Deploy with Docker
```bash
docker-compose up -d
```

---

## 📁 Project Structure

```
atlas_core07/
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main component
│   │   ├── styles/          # CSS & design tokens
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app.py               # Flask app
│   ├── ai/                  # AI providers
│   ├── routes/              # API endpoints
│   ├── database/            # Database & migrations
│   ├── services/            # Business logic
│   └── requirements.txt
│
├── docker-compose.yml       # Docker config
├── Dockerfile.frontend      # Frontend container
├── Dockerfile.backend       # Backend container
├── nginx.conf              # Web server config
│
└── Documentation/
    ├── README.md           # Full documentation
    ├── QUICKSTART.md       # 5-min start
    ├── INSTALLATION.md     # Setup guide
    ├── API.md              # API reference
    └── ADVANCED_FEATURES.md # Customization
```

---

## 🆘 Help & Troubleshooting

### "Module not found" error
```bash
cd backend
pip install -r requirements.txt
```

### Port already in use
Edit `backend/.env`:
```env
FLASK_PORT=5001
```

### Blank messages on send
1. Check browser console (F12)
2. Check backend terminal output
3. Verify `VITE_API_URL` in `frontend/.env`

### More Help
See [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| **Files** | 70+ |
| **Code** | 5000+ lines |
| **Docs** | 100+ pages |
| **APIs** | 9 endpoints |
| **Providers** | 4 (mock, OpenAI, Gemini, Claude) |

---

## 🎓 Learning Path

### Week 1: Getting Started
- [ ] Run SETUP.sh or manual setup
- [ ] Explore the UI
- [ ] Create conversations
- [ ] Try demo mode

### Week 2: Configuration
- [ ] Get OpenAI API key
- [ ] Configure in backend/.env
- [ ] Chat with real AI
- [ ] Customize colors

### Week 3: Advanced
- [ ] Read ADVANCED_FEATURES.md
- [ ] Deploy with Docker
- [ ] Add custom features
- [ ] Deploy to production

---

## ✨ Key Features

- 🤖 **Multiple AI Providers** - OpenAI, Gemini, Claude, or use demo mode
- 💬 **Rich Chat Interface** - Markdown, syntax highlighting, message editing
- 🎨 **Premium Design** - Dark mode, responsive, accessibility-first
- 📱 **Mobile Ready** - Works on all devices
- 🔒 **Secure** - Environment-based API keys
- 🚀 **Production Ready** - Tests, logging, error handling
- 📚 **Well Documented** - 100+ pages of guides

---

## 🔗 Quick Links

| Link | Purpose |
|------|---------|
| [QUICKSTART.md](QUICKSTART.md) | Start in 5 minutes |
| [README.md](README.md) | Full documentation |
| [INSTALLATION.md](INSTALLATION.md) | Detailed setup |
| [API.md](API.md) | API endpoints |
| [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) | Customization |

---

## 🎉 You're Ready!

**Choose your starting path:**

1. **Just want to run it?**
   → Follow Quick Start above

2. **Need detailed setup?**
   → Read [INSTALLATION.md](INSTALLATION.md)

3. **Want to understand it?**
   → Read [README.md](README.md)

4. **Need API docs?**
   → See [API.md](API.md)

5. **Want to customize?**
   → Check [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)

---

## 🚀 Next Steps

### Now
```bash
chmod +x SETUP.sh
./SETUP.sh
# OR follow manual start above
```

### Then
- Explore the UI
- Create a conversation
- Send a message

### Later
- Add AI provider key
- Customize colors
- Deploy to production

---

**atlas_core07 - Your AI companion is ready to help!** ✨

**Version**: 1.0.0  
**Status**: Production Ready ✅  
**Questions?** Read the docs in this folder!
