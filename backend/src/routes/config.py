"""
Rotas de configuração do sistema
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.config import SystemConfig
from ..models.audit import AuditLog, ActionType
from ..services.auth_service import AuthService
from ..config.database import db_config, test_connection
from ..services.email_service import EmailService
from ..services.whatsapp_service import WhatsAppService

config_bp = Blueprint('config', __name__)

@config_bp.route('/', methods=['GET'])
@jwt_required()
def get_configs():
    """Obtém todas as configurações"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        configs = SystemConfig.query.all()
        
        # Agrupar por categoria
        grouped_configs = {}
        for config in configs:
            category = config.category or 'general'
            if category not in grouped_configs:
                grouped_configs[category] = []
            grouped_configs[category].append(config.to_dict())
        
        return jsonify({
            'success': True,
            'data': grouped_configs
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@config_bp.route('/<key>', methods=['GET'])
@jwt_required()
def get_config(key):
    """Obtém configuração específica"""
    try:
        config = SystemConfig.query.filter_by(key=key).first()
        
        if not config:
            return jsonify({
                'success': False,
                'message': 'Configuração não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': config.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@config_bp.route('/<key>', methods=['PUT'])
@jwt_required()
def update_config(key):
    """Atualiza configuração"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        data = request.get_json()
        value = data.get('value')
        description = data.get('description')
        category = data.get('category', 'general')
        
        if value is None:
            return jsonify({
                'success': False,
                'message': 'Valor é obrigatório'
            }), 400
        
        config = SystemConfig.set_value(
            key=key,
            value=value,
            description=description,
            category=category,
            user_id=current_user_id
        )
        
        # Log da alteração
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.CONFIG_CHANGE,
            resource_type='config',
            resource_id=key,
            description=f"Configuração alterada: {key}",
            details={'old_value': '***', 'new_value': value if not config.is_encrypted else '***'},
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Configuração atualizada com sucesso',
            'data': config.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@config_bp.route('/database', methods=['GET'])
@jwt_required()
def get_database_config():
    """Obtém configurações do banco de dados"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        db_configs = {
            'server': SystemConfig.get_value('db_server', db_config.DEFAULT_SERVER),
            'database': SystemConfig.get_value('db_database', db_config.DEFAULT_DATABASE),
            'username': SystemConfig.get_value('db_username', db_config.DEFAULT_USERNAME),
            'password': '***',  # Não expor senha
            'driver': SystemConfig.get_value('db_driver', db_config.DEFAULT_DRIVER)
        }
        
        return jsonify({
            'success': True,
            'data': db_configs
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@config_bp.route('/database', methods=['PUT'])
@jwt_required()
def update_database_config():
    """Atualiza configurações do banco de dados"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        data = request.get_json()
        
        # Atualizar configurações
        configs_to_update = [
            ('db_server', data.get('server'), 'Servidor SQL Server'),
            ('db_database', data.get('database'), 'Nome do Banco de Dados'),
            ('db_username', data.get('username'), 'Usuário do Banco'),
            ('db_driver', data.get('driver'), 'Driver do Banco')
        ]
        
        if data.get('password'):
            configs_to_update.append(('db_password', data.get('password'), 'Senha do Banco'))
        
        for key, value, description in configs_to_update:
            if value:
                SystemConfig.set_value(
                    key=key,
                    value=value,
                    description=description,
                    category='database',
                    user_id=current_user_id
                )
        
        # Log da alteração
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.CONFIG_CHANGE,
            resource_type='database_config',
            description="Configurações de banco de dados atualizadas",
            details=data,
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Configurações de banco atualizadas com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@config_bp.route('/database/test', methods=['POST'])
@jwt_required()
def test_database_connection():
    """Testa conexão com banco de dados"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        success, message = test_connection()
        
        # Log do teste
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.CONFIG_CHANGE,
            resource_type='database_test',
            description="Teste de conexão com banco de dados",
            details={'success': success, 'message': message},
            success=success
        )
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@config_bp.route('/email/test', methods=['POST'])
@jwt_required()
def test_email_connection():
    """Testa conexão de email"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        email_service = EmailService()
        success, message = email_service.test_connection()
        
        # Log do teste
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.CONFIG_CHANGE,
            resource_type='email_test',
            description="Teste de conexão de email",
            details={'success': success, 'message': message},
            success=success
        )
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@config_bp.route('/whatsapp/test', methods=['POST'])
@jwt_required()
def test_whatsapp_connection():
    """Testa conexão WhatsApp"""
    try:
        current_user_id = get_jwt_identity()
        current_user_data = AuthService.get_current_user(current_user_id)
        
        if not current_user_data or not current_user_data.get('is_admin'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        whatsapp_service = WhatsAppService()
        success, message = whatsapp_service.test_connection()
        
        # Log do teste
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.CONFIG_CHANGE,
            resource_type='whatsapp_test',
            description="Teste de conexão WhatsApp",
            details={'success': success, 'message': message},
            success=success
        )
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

