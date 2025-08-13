"""
Rotas da API do sistema CRC-ES
"""
from .auth import auth_bp
from .campaigns import campaigns_bp
from .templates import templates_bp
from .contacts import contacts_bp
from .config import config_bp
from .audit import audit_bp

def register_blueprints(app):
    """Registra todos os blueprints"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
    app.register_blueprint(templates_bp, url_prefix='/api/templates')
    app.register_blueprint(contacts_bp, url_prefix='/api/contacts')
    app.register_blueprint(config_bp, url_prefix='/api/config')
    app.register_blueprint(audit_bp, url_prefix='/api/audit')

__all__ = ['register_blueprints']

