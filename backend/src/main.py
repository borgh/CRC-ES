"""
Aplicação principal do sistema CRC-ES
Sistema completo baseado nos scripts originais
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from src.config.database import init_database
from src.routes import register_blueprints

def create_app():
    """Factory da aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sua_chave_secreta_muito_forte_aqui')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'sua_chave_jwt_muito_forte_aqui')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens não expiram automaticamente
    
    # CORS - Permitir todas as origens para desenvolvimento
    CORS(app, origins="*", supports_credentials=True)
    
    # JWT
    jwt = JWTManager(app)
    
    # Inicializar banco de dados
    init_database(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Rota de health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check da API"""
        return jsonify({
            'success': True,
            'message': 'Sistema CRC-ES funcionando',
            'version': '1.0.0',
            'status': 'healthy'
        }), 200
    
    # Rota raiz
    @app.route('/', methods=['GET'])
    def index():
        """Página inicial da API"""
        return jsonify({
            'message': 'Sistema CRC-ES - API Backend',
            'version': '1.0.0',
            'description': 'Sistema completo baseado nos scripts originais',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'campaigns': '/api/campaigns',
                'templates': '/api/templates',
                'contacts': '/api/contacts',
                'config': '/api/config',
                'audit': '/api/audit'
            }
        }), 200
    
    # Handler de erro JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token expirado'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Token inválido'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Token de acesso necessário'
        }), 401
    
    return app

def main():
    """Função principal"""
    print("🚀 Iniciando Sistema CRC-ES...")
    print("📊 Sistema completo baseado nos scripts originais")
    
    app = create_app()
    
    # Configurações do servidor
    host = '0.0.0.0'  # Permitir acesso externo
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"✅ Sistema iniciado com sucesso!")
    print(f"🌐 Acesse: http://localhost:{port}")
    print(f"🔑 Login padrão: admin / admin123")
    print(f"📋 API Health: http://localhost:{port}/api/health")
    print(f"📚 Endpoints disponíveis:")
    print(f"   - Autenticação: /api/auth")
    print(f"   - Campanhas: /api/campaigns")
    print(f"   - Templates: /api/templates")
    print(f"   - Contatos: /api/contacts")
    print(f"   - Configurações: /api/config")
    print(f"   - Auditoria: /api/audit")
    
    # Iniciar servidor
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()

