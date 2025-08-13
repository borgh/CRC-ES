"""
Versão simplificada do backend para testes sem SQL Server
"""
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

def create_app():
    """Factory da aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = 'sua_chave_secreta_muito_forte_aqui'
    app.config['JWT_SECRET_KEY'] = 'sua_chave_jwt_muito_forte_aqui'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)
    
    # CORS - Permitir todas as origens para desenvolvimento
    CORS(app, origins="*", supports_credentials=True)
    
    # JWT
    jwt = JWTManager(app)
    
    # Dados simulados
    users = {
        'admin': {
            'id': 1,
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@crces.org.br',
            'is_admin': True,
            'is_active': True
        }
    }
    
    campaigns = []
    templates = [
        {
            'id': 1,
            'name': 'Anuidade 2024 - Email',
            'type': 'email',
            'subject': 'ANUIDADE DE 2024 - CRCES',
            'content': 'Prezado(a) {nome}, segue boleto da anuidade 2024...',
            'is_active': True
        },
        {
            'id': 2,
            'name': 'Anuidade 2024 - WhatsApp',
            'type': 'whatsapp',
            'content': 'Prezado {nome}, segue boleto da anuidade de 2024...',
            'is_active': True
        }
    ]
    
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
            'message': 'Sistema CRC-ES - API Backend (Modo Simplificado)',
            'version': '1.0.0',
            'description': 'Sistema completo baseado nos scripts originais',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'campaigns': '/api/campaigns',
                'templates': '/api/templates'
            }
        }), 200
    
    # Auth endpoints
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Login do usuário"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({
                    'success': False,
                    'message': 'Usuário e senha são obrigatórios'
                }), 400
            
            user = users.get(username)
            if not user or user['password'] != password:
                return jsonify({
                    'success': False,
                    'message': 'Usuário ou senha inválidos'
                }), 401
            
            # Criar token
            access_token = create_access_token(identity=user['id'])
            
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso',
                'data': {
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'is_admin': user['is_admin']
                    },
                    'access_token': access_token
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro interno: {e}'
            }), 500
    
    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required()
    def get_current_user():
        """Obtém dados do usuário atual"""
        try:
            current_user_id = get_jwt_identity()
            user = next((u for u in users.values() if u['id'] == current_user_id), None)
            
            if user:
                return jsonify({
                    'success': True,
                    'data': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'is_admin': user['is_admin']
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Usuário não encontrado'
                }), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro interno: {e}'
            }), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    @jwt_required()
    def logout():
        """Logout do usuário"""
        return jsonify({
            'success': True,
            'message': 'Logout realizado com sucesso'
        }), 200
    
    # Campaigns endpoints
    @app.route('/api/campaigns', methods=['GET'])
    @jwt_required()
    def get_campaigns():
        """Lista campanhas"""
        return jsonify({
            'success': True,
            'data': {
                'campaigns': campaigns,
                'total': len(campaigns),
                'pages': 1,
                'current_page': 1,
                'per_page': 10
            }
        }), 200
    
    @app.route('/api/campaigns', methods=['POST'])
    @jwt_required()
    def create_campaign():
        """Cria campanha"""
        try:
            data = request.get_json()
            
            campaign = {
                'id': len(campaigns) + 1,
                'name': data.get('name'),
                'description': data.get('description', ''),
                'type': data.get('type'),
                'status': 'draft',
                'email_template_id': data.get('email_template_id'),
                'whatsapp_template_id': data.get('whatsapp_template_id'),
                'created_at': '2024-01-01T00:00:00',
                'sent_count': 0,
                'delivered_count': 0,
                'failed_count': 0
            }
            
            campaigns.append(campaign)
            
            return jsonify({
                'success': True,
                'message': 'Campanha criada com sucesso',
                'data': campaign
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro interno: {e}'
            }), 500
    
    @app.route('/api/campaigns/<int:campaign_id>', methods=['PUT'])
    @jwt_required()
    def update_campaign(campaign_id):
        """Atualiza campanha"""
        try:
            data = request.get_json()
            
            campaign = next((c for c in campaigns if c['id'] == campaign_id), None)
            if not campaign:
                return jsonify({
                    'success': False,
                    'message': 'Campanha não encontrada'
                }), 404
            
            # Atualizar campos
            for key, value in data.items():
                if key in campaign:
                    campaign[key] = value
            
            return jsonify({
                'success': True,
                'message': 'Campanha atualizada com sucesso',
                'data': campaign
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro interno: {e}'
            }), 500
    
    @app.route('/api/campaigns/<int:campaign_id>', methods=['DELETE'])
    @jwt_required()
    def delete_campaign(campaign_id):
        """Exclui campanha"""
        try:
            global campaigns
            campaigns = [c for c in campaigns if c['id'] != campaign_id]
            
            return jsonify({
                'success': True,
                'message': 'Campanha excluída com sucesso'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro interno: {e}'
            }), 500
    
    @app.route('/api/campaigns/<int:campaign_id>/start', methods=['POST'])
    @jwt_required()
    def start_campaign(campaign_id):
        """Inicia campanha"""
        try:
            campaign = next((c for c in campaigns if c['id'] == campaign_id), None)
            if not campaign:
                return jsonify({
                    'success': False,
                    'message': 'Campanha não encontrada'
                }), 404
            
            campaign['status'] = 'completed'
            campaign['sent_count'] = 10
            campaign['delivered_count'] = 8
            campaign['failed_count'] = 2
            
            return jsonify({
                'success': True,
                'message': 'Campanha executada com sucesso',
                'data': campaign
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro interno: {e}'
            }), 500
    
    @app.route('/api/campaigns/stats', methods=['GET'])
    @jwt_required()
    def get_campaign_stats():
        """Estatísticas das campanhas"""
        total = len(campaigns)
        completed = len([c for c in campaigns if c['status'] == 'completed'])
        running = len([c for c in campaigns if c['status'] == 'running'])
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'draft': len([c for c in campaigns if c['status'] == 'draft']),
                'running': running,
                'completed': completed,
                'success_rate': 80.0 if completed > 0 else 0
            }
        }), 200
    
    # Templates endpoints
    @app.route('/api/templates', methods=['GET'])
    @jwt_required()
    def get_templates():
        """Lista templates"""
        return jsonify({
            'success': True,
            'data': {
                'templates': templates,
                'total': len(templates),
                'pages': 1,
                'current_page': 1,
                'per_page': 10
            }
        }), 200
    
    # Contacts endpoints
    @app.route('/api/contacts/stats', methods=['GET'])
    @jwt_required()
    def get_contacts_stats():
        """Estatísticas dos contatos"""
        return jsonify({
            'success': True,
            'data': {
                'total': 1250,
                'with_email': 980,
                'with_phone': 1100,
                'with_debts': 45,
                'active_phones': 1050
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
    print("🚀 Iniciando Sistema CRC-ES (Modo Simplificado)...")
    print("📊 Sistema completo baseado nos scripts originais")
    
    app = create_app()
    
    # Configurações do servidor
    host = '0.0.0.0'  # Permitir acesso externo
    port = int(os.getenv('PORT', 5000))
    debug = True
    
    print(f"✅ Sistema iniciado com sucesso!")
    print(f"🌐 Acesse: http://localhost:{port}")
    print(f"🔑 Login padrão: admin / admin123")
    print(f"📋 API Health: http://localhost:{port}/api/health")
    print(f"📚 Endpoints disponíveis:")
    print(f"   - Autenticação: /api/auth")
    print(f"   - Campanhas: /api/campaigns")
    print(f"   - Templates: /api/templates")
    
    # Iniciar servidor
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()

