# atlas_core07 - Advanced Features & Customization

## AI Provider Configuration

### Supported Providers

1. **Mock** (Demo)
   ```env
   AI_PROVIDER=mock
   ```

2. **OpenAI**
   ```env
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   OPENAI_BASE_URL=https://api.openai.com/v1
   ```

3. **Google Gemini**
   ```env
   AI_PROVIDER=gemini
   GEMINI_API_KEY=...
   ```

4. **Anthropic Claude**
   ```env
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   ```

## Adding Custom AI Provider

1. Create `backend/ai/custom_provider.py`:

```python
from ai.base import AIProvider
import os

class CustomProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv('CUSTOM_API_KEY')
        # Initialize your provider
    
    def generate(self, messages, model=None, temperature=0.7, max_tokens=2000):
        # Implement API call
        return "response"
    
    def get_models(self):
        return [{'id': 'model-1', 'name': 'Custom Model'}]
    
    @property
    def is_available(self):
        return self.api_key is not None
```

2. Update `backend/services/ai_service.py`:

```python
# In _init_provider method:
if self.provider_name == 'custom':
    from ai.custom_provider import CustomProvider
    provider = CustomProvider()
    if provider.is_available:
        return provider
```

3. Use it:

```env
AI_PROVIDER=custom
CUSTOM_API_KEY=your-key
```

## Customizing UI

### Change Colors

Edit `frontend/src/styles/globals.css`:

```css
:root {
  --color-accent: #YOUR-COLOR;
  --color-text-primary: #...;
  /* ... other colors */
}
```

### Change Welcome Message

Edit `frontend/src/App.jsx`, modify the `welcome` section:

```jsx
<div className="welcome">
  <h2>Your Custom Title</h2>
  <p>Your custom message</p>
</div>
```

### Add Custom Styles

Create new CSS file in `frontend/src/styles/`:

```css
.custom-class {
  color: var(--color-accent);
}
```

## Database

### Reset Database

```bash
rm backend/atlas_core07.db
python -c "from database.db import init_db; init_db()"
```

### Query Database

```python
from database.db import get_db

db = get_db()
cursor = db.cursor()
cursor.execute("SELECT * FROM conversations")
rows = cursor.fetchall()
db.close()
```

## Deployment

### Docker

```bash
docker-compose up -d
```

### VPS (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-venv nodejs npm nginx

# Setup backend
cd atlas_core07/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
npm run build

# Configure Nginx and run
```

### Cloud Platforms

- **Vercel** (Frontend)
- **Render/Railway** (Backend)
- **Heroku** (Full Stack)

## Performance

- Code splitting in Vite (automatic)
- Database indexes created on initialization
- Logging system with rotation
- Error tracking ready

## Security

- API keys in environment variables only
- CORS configured
- Input validation on all endpoints
- SQL injection prevention (parameterized queries)

## Testing

```bash
cd backend
pytest tests/ -v
pytest --cov=. --cov-report=html
```

## Monitoring

Logs are stored in `backend/logs/`:
- `app.log` - All logs
- `errors.log` - Error logs only

## Extending

### Add New Route

1. Create `backend/routes/custom.py`:

```python
from flask import Blueprint, jsonify

custom_bp = Blueprint('custom', __name__, url_prefix='/api')

@custom_bp.route('/custom', methods=['GET'])
def custom_endpoint():
    return jsonify({'message': 'custom'})
```

2. Register in `backend/app.py`:

```python
from routes.custom import custom_bp
app.register_blueprint(custom_bp)
```

### Add New Component

1. Create `frontend/src/components/Custom.jsx`:

```jsx
export function Custom() {
  return <div>Custom Component</div>
}
```

2. Use in `App.jsx`

---

## Cost Analysis

| Provider | Cost | Free Tier |
|----------|------|-----------|
| Mock | $0 | ∞ |
| OpenAI | $0.002-0.06/1K tokens | None |
| Gemini | Freemium | 60 req/min |
| Claude | Similar to OpenAI | None |

---

**Everything is documented. Customize freely!** 🎨
