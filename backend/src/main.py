import os
import sys

# Configurações de ambiente (sem dotenv)
os.environ.setdefault('SECRET_KEY', 'crces-sistema-secreto-2025')
os.environ.setdefault('JWT_SECRET_KEY', 'jwt-crces-2025-secreto')
os.environ.setdefault('JWT_ACCESS_TOKEN_EXPIRES', '3600')
os.environ.setdefault('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.database import db, init_database
from src.routes.auth import auth_bp
from src.routes.campaigns import campaigns_bp
from src.routes.templates import templates_bp
from src.routes.messaging import messaging_bp
from src.routes.audit import audit_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'crces-sistema-secreto-2025')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-crces-2025-secreto')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

# Configuração do banco de dados
database_url = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de upload
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB

# Inicializar extensões
CORS(app, origins="*")
jwt = JWTManager(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
app.register_blueprint(templates_bp, url_prefix='/api/templates')
app.register_blueprint(messaging_bp, url_prefix='/api/messaging')
app.register_blueprint(audit_bp, url_prefix='/api/audit')

# Inicializar banco de dados
init_database(app)

# Criar diretório de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'boletos'), exist_ok=True)

@app.route('/api/health')
def health_check():
    """Endpoint de verificação de saúde"""
    return {'status': 'ok', 'message': 'Sistema CRC-ES funcionando'}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Servir arquivos estáticos do frontend"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    print("🚀 Iniciando Sistema CRC-ES...")
    print(f"📊 Banco de dados: {database_url}")
    print(f"📁 Diretório de uploads: {app.config['UPLOAD_FOLDER']}")
    print("🌐 Servidor rodando em http://0.0.0.0:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', 'True').lower() == 'true')
