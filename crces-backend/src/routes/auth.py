from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
import secrets
import json

from src.models.user import db, User, Role
from src.models.audit import AuditLog

auth_bp = Blueprint('auth', __name__)

# Lista de tokens revogados (em produção, usar Redis)
revoked_tokens = set()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login com suporte a MFA"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        username = data.get('username')
        password = data.get('password')
        mfa_token = data.get('mfa_token')
        
        if not username or not password:
            return jsonify({'message': 'Username e password são obrigatórios'}), 400
        
        # Busca usuário
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            # Log tentativa de login com usuário inexistente
            AuditLog.log_action(
                username=username,
                action_type='LOGIN_FAILED',
                resource_type='User',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                endpoint=request.endpoint,
                method=request.method,
                success=False,
                error_message='Usuário não encontrado'
            )
            return jsonify({'message': 'Credenciais inválidas'}), 401
        
        # Verifica se a conta está ativa
        if not user.is_active:
            AuditLog.log_action(
                user_id=user.id,
                username=user.username,
                action_type='LOGIN_FAILED',
                resource_type='User',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                endpoint=request.endpoint,
                method=request.method,
                success=False,
                error_message='Conta inativa'
            )
            return jsonify({'message': 'Conta inativa'}), 401
        
        # Verifica se a conta está bloqueada
        if user.is_locked():
            AuditLog.log_action(
                user_id=user.id,
                username=user.username,
                action_type='LOGIN_FAILED',
                resource_type='User',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                endpoint=request.endpoint,
                method=request.method,
                success=False,
                error_message='Conta bloqueada'
            )
            return jsonify({'message': 'Conta temporariamente bloqueada'}), 423
        
        # Verifica senha
        if not user.check_password(password):
            user.failed_login_attempts += 1
            
            # Bloqueia conta após 5 tentativas falhadas
            if user.failed_login_attempts >= 5:
                user.lock_account(30)  # Bloqueia por 30 minutos
                db.session.commit()
                
                AuditLog.log_action(
                    user_id=user.id,
                    username=user.username,
                    action_type='ACCOUNT_LOCKED',
                    resource_type='User',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    endpoint=request.endpoint,
                    method=request.method,
                    success=False,
                    error_message='Conta bloqueada por múltiplas tentativas falhadas'
                )
                return jsonify({'message': 'Conta bloqueada por múltiplas tentativas falhadas'}), 423
            
            db.session.commit()
            
            AuditLog.log_action(
                user_id=user.id,
                username=user.username,
                action_type='LOGIN_FAILED',
                resource_type='User',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                endpoint=request.endpoint,
                method=request.method,
                success=False,
                error_message='Senha incorreta'
            )
            return jsonify({'message': 'Credenciais inválidas'}), 401
        
        # Se MFA está habilitado, verifica token
        if user.mfa_enabled:
            if not mfa_token:
                return jsonify({
                    'message': 'Token MFA necessário',
                    'mfa_required': True
                }), 200
            
            if not user.verify_mfa_token(mfa_token):
                user.failed_login_attempts += 1
                db.session.commit()
                
                AuditLog.log_action(
                    user_id=user.id,
                    username=user.username,
                    action_type='LOGIN_FAILED',
                    resource_type='User',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    endpoint=request.endpoint,
                    method=request.method,
                    success=False,
                    error_message='Token MFA inválido'
                )
                return jsonify({'message': 'Token MFA inválido'}), 401
        
        # Login bem-sucedido
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Cria tokens JWT
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'username': user.username,
                'roles': [role.name for role in user.roles]
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        # Log login bem-sucedido
        AuditLog.log_action(
            user_id=user.id,
            username=user.username,
            action_type='LOGIN_SUCCESS',
            resource_type='User',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'mfa_enabled': user.mfa_enabled
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no login: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Endpoint para renovar token de acesso"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuário inválido'}), 401
        
        # Cria novo token de acesso
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'username': user.username,
                'roles': [role.name for role in user.roles]
            }
        )
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no refresh: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Endpoint de logout"""
    try:
        current_user_id = get_jwt_identity()
        jti = get_jwt()['jti']  # JWT ID
        
        # Adiciona token à lista de revogados
        revoked_tokens.add(jti)
        
        user = User.query.get(current_user_id)
        
        # Log logout
        AuditLog.log_action(
            user_id=current_user_id,
            username=user.username if user else None,
            action_type='LOGOUT',
            resource_type='User',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no logout: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/setup-mfa', methods=['POST'])
@jwt_required()
def setup_mfa():
    """Endpoint para configurar MFA"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Gera novo secret MFA
        secret = user.generate_mfa_secret()
        qr_code = user.get_mfa_qr_code()
        
        db.session.commit()
        
        # Log configuração MFA
        AuditLog.log_action(
            user_id=current_user_id,
            username=user.username,
            action_type='MFA_SETUP_INITIATED',
            resource_type='User',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'MFA configurado. Use o QR code para configurar seu app autenticador',
            'secret': secret,
            'qr_code': qr_code
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro na configuração MFA: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/verify-mfa', methods=['POST'])
@jwt_required()
def verify_mfa():
    """Endpoint para verificar e ativar MFA"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'message': 'Token MFA é obrigatório'}), 400
        
        # Verifica token
        if not user.verify_mfa_token(token):
            AuditLog.log_action(
                user_id=current_user_id,
                username=user.username,
                action_type='MFA_VERIFICATION_FAILED',
                resource_type='User',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                endpoint=request.endpoint,
                method=request.method,
                success=False,
                error_message='Token MFA inválido'
            )
            return jsonify({'message': 'Token MFA inválido'}), 400
        
        # Ativa MFA
        user.mfa_enabled = True
        
        # Gera códigos de backup
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        user.backup_codes = json.dumps(backup_codes)
        
        db.session.commit()
        
        # Log ativação MFA
        AuditLog.log_action(
            user_id=current_user_id,
            username=user.username,
            action_type='MFA_ENABLED',
            resource_type='User',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'MFA ativado com sucesso',
            'backup_codes': backup_codes
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro na verificação MFA: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/disable-mfa', methods=['POST'])
@jwt_required()
def disable_mfa():
    """Endpoint para desativar MFA"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'message': 'Senha é obrigatória para desativar MFA'}), 400
        
        # Verifica senha
        if not user.check_password(password):
            AuditLog.log_action(
                user_id=current_user_id,
                username=user.username,
                action_type='MFA_DISABLE_FAILED',
                resource_type='User',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                endpoint=request.endpoint,
                method=request.method,
                success=False,
                error_message='Senha incorreta'
            )
            return jsonify({'message': 'Senha incorreta'}), 401
        
        # Desativa MFA
        user.mfa_enabled = False
        user.mfa_secret = None
        user.backup_codes = None
        
        db.session.commit()
        
        # Log desativação MFA
        AuditLog.log_action(
            user_id=current_user_id,
            username=user.username,
            action_type='MFA_DISABLED',
            resource_type='User',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({'message': 'MFA desativado com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro na desativação MFA: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Endpoint para obter informações do usuário atual"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter usuário atual: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

