import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carrega variáveis de ambiente
load_dotenv()

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

# Importa todos os modelos
from src.models.user import db, User, Role, Permission
from src.models.campaign import Campaign, CampaignMessage
from src.models.template import EmailTemplate, WhatsAppTemplate
from src.models.audit import AuditLog, SystemHealth

# Importa blueprints
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.campaign import campaign_bp
from src.routes.template import template_bp
from src.routes.audit import audit_bp
from src.routes.messaging import messaging_bp

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Configurações de upload
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    
    # Configurações do banco de dados
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback para SQLite em desenvolvimento
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Inicializa extensões
    CORS(app, origins="*", supports_credentials=True)
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)
    
    # Inicializa banco de dados
    db.init_app(app)
    
    # Registra blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(campaign_bp, url_prefix='/api/campaigns')
    app.register_blueprint(template_bp, url_prefix='/api/templates')
    app.register_blueprint(audit_bp, url_prefix='/api/audit')
    app.register_blueprint(messaging_bp, url_prefix='/api/messaging')
    
    # Handlers de JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token expirado'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Token inválido'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'message': 'Token de autorização necessário'}), 401
    
    # Middleware para logging de auditoria
    @app.before_request
    def log_request():
        # Pula logging para arquivos estáticos e health check
        if request.endpoint in ['static', 'serve', 'health']:
            return
        
        # Armazena informações da requisição para uso posterior
        request.audit_info = {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'endpoint': request.endpoint,
            'method': request.method
        }
    
    # Rota de health check
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': SystemHealth().created_at.isoformat(),
            'version': '1.0.0'
        })
    
    # Rota para servir arquivos estáticos (frontend)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
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
                return jsonify({'message': 'API do Sistema CRC-ES', 'version': '1.0.0'}), 200
    
    # Cria tabelas (dados iniciais devem ser criados separadamente)
    with app.app_context():
        db.create_all()
    
    return app

def create_initial_data():
    """Cria dados iniciais do sistema"""
    
    # Cria permissões básicas
    permissions = [
        ('view_dashboard', 'Visualizar dashboard'),
        ('manage_users', 'Gerenciar usuários'),
        ('create_campaigns', 'Criar campanhas'),
        ('send_emails', 'Enviar emails'),
        ('send_whatsapp', 'Enviar WhatsApp'),
        ('manage_templates', 'Gerenciar templates'),
        ('view_reports', 'Visualizar relatórios'),
        ('view_audit_logs', 'Visualizar logs de auditoria'),
        ('system_admin', 'Administração do sistema')
    ]
    
    for perm_name, perm_desc in permissions:
        if not Permission.query.filter_by(name=perm_name).first():
            permission = Permission(name=perm_name, description=perm_desc)
            db.session.add(permission)
    
    db.session.commit()
    
    # Cria roles básicos
    roles_config = {
        'admin': {
            'description': 'Administrador do sistema',
            'permissions': [p[0] for p in permissions]  # Todas as permissões
        },
        'operator_senior': {
            'description': 'Operador sênior',
            'permissions': ['view_dashboard', 'create_campaigns', 'send_emails', 
                          'send_whatsapp', 'manage_templates', 'view_reports']
        },
        'operator_junior': {
            'description': 'Operador júnior',
            'permissions': ['view_dashboard', 'create_campaigns', 'send_emails', 'send_whatsapp']
        },
        'viewer': {
            'description': 'Visualizador',
            'permissions': ['view_dashboard', 'view_reports']
        }
    }
    
    for role_name, role_config in roles_config.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=role_config['description'])
            db.session.add(role)
            db.session.flush()  # Para obter o ID
        
        # Adiciona permissões ao role
        for perm_name in role_config['permissions']:
            permission = Permission.query.filter_by(name=perm_name).first()
            if permission and permission not in role.permissions:
                role.permissions.append(permission)
    
    db.session.commit()
    
    # Cria usuário admin padrão se não existir
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@crc-es.org.br',
            is_active=True,
            is_verified=True
        )
        admin_user.set_password('admin123')  # Senha padrão - deve ser alterada
        
        # Adiciona role de admin
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin_user.roles.append(admin_role)
        
        db.session.add(admin_user)
        db.session.commit()
        
        # Log da criação do usuário admin
        AuditLog.log_action(
            username='system',
            action_type='CREATE',
            resource_type='User',
            resource_id=str(admin_user.id),
            new_values={'username': 'admin', 'email': 'admin@crc-es.org.br'},
            additional_data={'note': 'Usuário admin criado automaticamente'}
        )

# Cria a aplicação
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

