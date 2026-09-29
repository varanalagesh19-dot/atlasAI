# atlas_core07 - Complete Installation Guide

Detailed setup instructions for all platforms.

## System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10+, macOS 10.15+, Linux |
| **Python** | 3.8+ |
| **Node.js** | 16+ |
| **RAM** | 4GB minimum |
| **Disk** | 2GB free |

## Installation Methods

### Method 1: Automatic Setup (Recommended)

```bash
# Make script executable
chmod +x SETUP.sh

# Run setup
./SETUP.sh
```

This script will:
- ✅ Check Python and Node versions
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create config files

### Method 2: Manual Setup

#### Windows

```cmd
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend (new terminal)
cd frontend
npm install
```

#### macOS / Linux

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend (new terminal)
cd frontend
npm install
```

## Configuration

### Demo Mode (No API Key Needed)

Works immediately with demo responses.

### OpenAI Configuration

1. Get API key: https://platform.openai.com/api-keys

2. Create `backend/.env`:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

3. Restart backend

### Google Gemini

1. Get API key: https://aistudio.google.com/app/apikey

2. Update `backend/.env`:
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-key
```

### Anthropic Claude

1. Get API key: https://console.anthropic.com/

2. Update `backend/.env`:
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
```

## Running atlas_core07

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Open Browser
Visit: http://localhost:5173

## Troubleshooting

### "python: command not found"
- Install from python.org
- Use `python3` on Mac/Linux
- Add Python to PATH on Windows

### "npm: command not found"
- Install from nodejs.org
- Restart terminal after install

### Port 5000 already in use
- Edit `backend/.env`: `FLASK_PORT=5001`
- Update `frontend/.env`: `VITE_API_URL=http://localhost:5001/api`

### Blank messages on send
- Check browser console (F12)
- Check backend terminal for errors
- Verify API_URL in frontend .env

## Development Setup

### VS Code Extensions
- Python (ms-python.python)
- ES7+ React Snippets
- Prettier

### PyCharm
1. Open backend folder
2. Configure Python interpreter
3. Mark backend as sources root

## Testing

```bash
cd backend
pytest tests/ -v
```

## Next Steps

1. Read QUICKSTART.md (5 min)
2. Read README.md (overview)
3. Explore API.md (endpoints)
4. Read ADVANCED_FEATURES.md (customization)

---

**Need help? All documentation is in this folder.** 📚
