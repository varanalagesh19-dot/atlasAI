# atlas_core07 - AI Chatbot Platform

**Advanced AI Conversation Engine Built with React & Python**

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Node](https://img.shields.io/badge/Node-16+-green)

---

## 🚀 What is atlas_core07?

atlas_core07 is a **professional-grade AI chatbot platform** that enables intelligent conversations through:

- 🤖 **Multi-Provider AI Support** - OpenAI, Google Gemini, Anthropic Claude, Mock (demo)
- 💬 **Smart Chat Interface** - Rich message rendering, markdown support, syntax highlighting
- 🎨 **Premium Design** - Dark mode, responsive, accessibility-first
- 📱 **Mobile Ready** - Works on all devices seamlessly
- 🔒 **Secure & Private** - Local storage fallback, environment-based secrets
- 🧪 **Production Ready** - Unit tests, CI/CD, logging, error tracking
- 📚 **Well Documented** - 120+ pages of guides and references
- 🐳 **Container Ready** - Docker support for easy deployment

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites
- **Python 3.8+** - [Download](https://python.org)
- **Node.js 16+** - [Download](https://nodejs.org)

### Installation

```bash
# 1. Start Backend
cd atlas_core07/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

# 2. Start Frontend (in new terminal)
cd atlas_core07/frontend
npm install
npm run dev

# 3. Open Browser
Visit: http://localhost:5173
```

✅ **atlas_core07 is running!**

---

## 📚 Documentation

| Guide | Purpose | Time |
|-------|---------|------|
| [Quick Start](QUICKSTART.md) | 5-minute setup | 5 min |
| [Installation Guide](INSTALLATION_GUIDE.md) | Detailed setup for all platforms | 30 min |
| [API Reference](API.md) | Complete API documentation | 20 min |
| [Deployment Guide](DEPLOYMENT.md) | Deploy to production | 45 min |
| [Advanced Features](ADVANCED_FEATURES.md) | Customization & advanced topics | 45 min |
| [Architecture](PROJECT_STRUCTURE.md) | Code organization & design | 20 min |

---

## ✨ Key Features

### Chat Interface
- ✅ Create conversations
- ✅ Send/receive messages
- ✅ Edit messages
- ✅ Regenerate responses
- ✅ Rich markdown rendering
- ✅ Code syntax highlighting
- ✅ Copy to clipboard
- ✅ Like/dislike feedback

### Conversation Management
- ✅ Search conversations
- ✅ Rename conversations
- ✅ Pin/unpin chats
- ✅ Delete conversations
- ✅ Auto-group by date
- ✅ Persistent storage

### AI Integration
- ✅ OpenAI (GPT-3.5, GPT-4)
- ✅ Google Gemini
- ✅ Anthropic Claude
- ✅ Mock provider (demo)
- ✅ Model selection
- ✅ Temperature control
- ✅ Token limit control
- ✅ Custom providers (extensible)

### UI/UX
- ✅ Dark mode
- ✅ Light mode
- ✅ System theme
- ✅ Mobile responsive
- ✅ Accessibility (WCAG AA)
- ✅ Settings page
- ✅ Landing page
- ✅ Toast notifications
- ✅ Modal dialogs
- ✅ Error boundaries

### Developer Features
- ✅ REST API (9 endpoints)
- ✅ Unit tests (pytest)
- ✅ CI/CD pipeline
- ✅ Docker support
- ✅ Logging system
- ✅ Database migrations
- ✅ CORS configured
- ✅ Input validation

---

## 🏗️ Architecture

### Three-Tier Design

```
┌─────────────────────────┐
│   React + Vite          │
│   (Frontend)            │
└────────────┬────────────┘
             │ HTTP/REST API
┌────────────▼────────────┐
│   Flask + SQLite        │
│   (Backend)             │
└────────────┬────────────┘
             │ SQL Queries
┌────────────▼────────────┐
│   SQLite Database       │
│   (Persistence)         │
└─────────────────────────┘
```

### Technology Stack

**Frontend**
- React 18
- Vite (build tool)
- Lucide React (icons)
- React Markdown
- Syntax Highlighter

**Backend**
- Python 3.11
- Flask
- SQLite
- Gunicorn (production)

**DevOps**
- Docker & Docker Compose
- Nginx
- GitHub Actions
- Pytest

---

## 🔧 Configuration

### No Configuration Needed (Demo Mode)
Works immediately with demo responses.

### With OpenAI API Key

Create `backend/.env`:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

### With Google Gemini
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
```

### With Anthropic Claude
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
```

See [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) for detailed configuration.

---

## 📁 Project Structure

```
atlas_core07/
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Full pages
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API services
│   │   ├── utils/           # Utilities
│   │   ├── styles/          # Design tokens
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app.py              # Flask app
│   ├── ai/                 # AI providers
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   ├── database/           # Database & migrations
│   ├── config/             # Configuration
│   ├── tests/              # Unit tests
│   ├── requirements.txt
│   └── .env.example
│
├── docker-compose.yml
├── Dockerfile.frontend
├── Dockerfile.backend
├── nginx.conf
│
└── Documentation/
    ├── README.md
    ├── QUICKSTART.md
    ├── INSTALLATION_GUIDE.md
    ├── DEPLOYMENT.md
    ├── ADVANCED_FEATURES.md
    ├── API.md
    └── PROJECT_STRUCTURE.md
```

---

## 🚀 Deployment

### Docker (Recommended)
```bash
docker-compose up -d
```
Access at: http://localhost

### Production VPS
```bash
# Follow DEPLOYMENT.md for step-by-step guide
```

### Cloud Platforms
- Vercel (Frontend)
- Cloud Run / Render (Backend)
- Railway
- Fly.io

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides.

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Total Files | 75+ |
| Lines of Code | 5000+ |
| Documentation | 120+ pages |
| API Endpoints | 9 |
| Components | 10+ |
| AI Providers | 4 |
| Test Coverage | Unit tests ready |

---

## 🧪 Testing

### Run Unit Tests
```bash
cd backend
pytest tests/ -v
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Tests
```bash
pytest tests/test_conversations.py -v
```

---

## 📝 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/conversations` | List all conversations |
| POST | `/api/conversations` | Create conversation |
| GET | `/api/conversations/:id` | Get conversation |
| PUT | `/api/conversations/:id` | Update conversation |
| DELETE | `/api/conversations/:id` | Delete conversation |
| GET | `/api/conversations/search` | Search conversations |
| POST | `/api/conversations/:id/messages` | Add message |
| POST | `/api/chat` | Generate AI response |
| GET | `/api/models` | List AI models |

See [API.md](API.md) for complete reference with examples.

---

## 🎨 Customization

### Change Colors
Edit `frontend/src/styles/globals.css`:
```css
:root {
  --color-accent: #0066CC;  /* Change this */
  --color-primary: #1a1a1a;
  /* ... other colors */
}
```

### Change Welcome Message
Edit `frontend/src/App.jsx`:
```jsx
const welcomeMessage = "Your custom message";
```

### Add Custom AI Provider
1. Create `backend/ai/your_provider.py`
2. Implement `AIProvider` interface
3. Update `services/ai_service.py`

See [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) for details.

---

## 🔒 Security

- ✅ No API keys in frontend
- ✅ Environment-based secrets
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CORS configured
- ✅ Error handling
- ✅ HTTPS ready

---

## 📈 Performance

- ✅ Code splitting
- ✅ Lazy loading
- ✅ Gzip compression
- ✅ Database indexing
- ✅ Caching ready
- ✅ Responsive images
- ✅ Optimized bundles

---

## 🤝 Contributing

This is your personal project! Extend it however you like:

1. Add authentication
2. Implement file uploads
3. Add voice support
4. Create mobile app
5. Build browser extension
6. Add team features

---

## 📞 Support

### Documentation
- Quick Start: [QUICKSTART.md](QUICKSTART.md)
- Setup: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- Advanced: [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)
- API: [API.md](API.md)
- Deploy: [DEPLOYMENT.md](DEPLOYMENT.md)

### Troubleshooting
1. Check backend terminal for errors
2. Check browser console (F12)
3. Read logs: `backend/logs/app.log`
4. See INSTALLATION_GUIDE.md troubleshooting section

---

## 📄 License

This is your personal project. Use it however you want!

---

## 🎯 Roadmap

- [ ] User authentication
- [ ] Conversation sharing
- [ ] File upload support
- [ ] Voice input/output
- [ ] Image generation
- [ ] Custom plugins
- [ ] Team collaboration
- [ ] Analytics dashboard
- [ ] Mobile app
- [ ] Browser extension

---

## 🎉 Getting Started

### Now:
1. Read [QUICKSTART.md](QUICKSTART.md) (5 min)
2. Follow installation above
3. Open http://localhost:5173
4. Start chatting!

### Next:
1. Add AI provider API key
2. Explore all features
3. Customize colors/design
4. Read [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)

### Later:
1. Deploy to production
2. Add custom features
3. Monitor with logging
4. Scale infrastructure

---

**atlas_core07: Your AI conversation engine. Built for you.** 🚀

**Version**: 1.0.0  
**Status**: Production Ready ✅  
**Built**: 2026-01-15

---

## Quick Links

- 🚀 [Quick Start Guide](QUICKSTART.md) - Get running in 5 minutes
- 📖 [Full Documentation](INSTALLATION_GUIDE.md) - Comprehensive setup guide
- 🔌 [API Reference](API.md) - All endpoints documented
- 🚢 [Deployment Guide](DEPLOYMENT.md) - Deploy to production
- ⚙️ [Advanced Features](ADVANCED_FEATURES.md) - Customization & advanced topics
- 🏗️ [Architecture Guide](PROJECT_STRUCTURE.md) - Understanding the codebase

**Choose your starting point above and begin building!** ✨
