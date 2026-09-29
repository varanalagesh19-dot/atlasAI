from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

from database.db import init_db
from database.migrations import init_migrations
from config.logging_config import setup_logging
from routes.conversations import conversations_bp
from routes.chat import chat_bp
from routes.models import models_bp
from routes.health import health_bp

app = Flask(__name__)

# Setup logging
setup_logging(app)

# CORS configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database initialization
with app.app_context():
    init_db()
    init_migrations()
    app.logger.info("Database initialized | Migrations applied")

# Register blueprints
app.register_blueprint(conversations_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(models_bp)
app.register_blueprint(health_bp)

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    app.logger.warning(f"400 Bad Request: {error}")
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    app.logger.warning(f"404 Not Found: {error}")
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 Internal Error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    env = os.getenv('FLASK_ENV', 'development')
    app.logger.info(f"Starting atlas_core07 | Port: {port} | Env: {env}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=(env == 'development')
    )
