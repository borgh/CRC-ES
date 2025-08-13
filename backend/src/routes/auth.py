"""
Rotas de autenticação
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
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
        
        # Obter informações da requisição
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Autenticar
        result, message = AuthService.authenticate_user(
            username, password, ip_address, user_agent
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renova token de acesso"""
    try:
        current_user_id = get_jwt_identity()
        
        result, message = AuthService.refresh_token(current_user_id)
        
        if result:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout do usuário"""
    try:
        current_user_id = get_jwt_identity()
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        success, message = AuthService.logout_user(
            current_user_id, ip_address, user_agent
        )
        
        return jsonify({
            'success': success,
            'message': message
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtém dados do usuário atual"""
    try:
        current_user_id = get_jwt_identity()
        user_data = AuthService.get_current_user(current_user_id)
        
        if user_data:
            return jsonify({
                'success': True,
                'data': user_data
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

@auth_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Cria novo usuário (apenas admins)"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        is_admin = data.get('is_admin', False)
        
        if not all([username, email, password]):
            return jsonify({
                'success': False,
                'message': 'Todos os campos são obrigatórios'
            }), 400
        
        user, message = AuthService.create_user(
            username, email, password, is_admin, current_user_id
        )
        
        if user:
            return jsonify({
                'success': True,
                'message': message,
                'data': user.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Atualiza usuário"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        # Verificar permissões (admin ou próprio usuário)
        if not current_user_data:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 404
        
        if not current_user_data.get('is_admin') and current_user_id != user_id:
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        data = request.get_json()
        
        user, message = AuthService.update_user(user_id, data, current_user_id)
        
        if user:
            return jsonify({
                'success': True,
                'message': message,
                'data': user.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

