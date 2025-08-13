"""
Serviço de autenticação e autorização
"""
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from ..models.user import User
from ..models.audit import AuditLog, ActionType
from ..config.database import db

class AuthService:
    """Serviço de autenticação"""
    
    @staticmethod
    def authenticate_user(username, password, ip_address=None, user_agent=None):
        """Autentica usuário"""
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                # Log tentativa de login inválida
                AuditLog.log_action(
                    user_id=None,
                    action=ActionType.LOGIN,
                    description=f"Tentativa de login com usuário inexistente: {username}",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    error_message="Usuário não encontrado"
                )
                return None, "Usuário ou senha inválidos"
            
            # Verificar se conta está bloqueada
            if user.locked_until and user.locked_until > datetime.utcnow():
                return None, "Conta temporariamente bloqueada"
            
            # Verificar se usuário está ativo
            if not user.is_active:
                return None, "Conta desativada"
            
            # Verificar senha
            if not user.check_password(password):
                # Incrementar tentativas de login
                user.login_attempts += 1
                
                # Bloquear após 5 tentativas
                if user.login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                
                db.session.commit()
                
                # Log tentativa inválida
                AuditLog.log_action(
                    user_id=user.id,
                    action=ActionType.LOGIN,
                    description=f"Tentativa de login com senha inválida",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    error_message="Senha inválida"
                )
                
                return None, "Usuário ou senha inválidos"
            
            # Login bem-sucedido
            user.login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Criar tokens
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=8)
            )
            refresh_token = create_refresh_token(
                identity=user.id,
                expires_delta=timedelta(days=30)
            )
            
            # Log login bem-sucedido
            AuditLog.log_action(
                user_id=user.id,
                action=ActionType.LOGIN,
                description=f"Login realizado com sucesso",
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            
            return {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, "Login realizado com sucesso"
            
        except Exception as e:
            return None, f"Erro interno: {e}"
    
    @staticmethod
    def refresh_token(current_user_id):
        """Renova token de acesso"""
        try:
            user = User.query.get(current_user_id)
            if not user or not user.is_active:
                return None, "Usuário inválido"
            
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=8)
            )
            
            return {
                'access_token': access_token,
                'user': user.to_dict()
            }, "Token renovado"
            
        except Exception as e:
            return None, f"Erro ao renovar token: {e}"
    
    @staticmethod
    def logout_user(user_id, ip_address=None, user_agent=None):
        """Registra logout do usuário"""
        try:
            # Log logout
            AuditLog.log_action(
                user_id=user_id,
                action=ActionType.LOGOUT,
                description="Logout realizado",
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            
            return True, "Logout realizado"
            
        except Exception as e:
            return False, f"Erro no logout: {e}"
    
    @staticmethod
    def create_user(username, email, password, is_admin=False, created_by=None):
        """Cria novo usuário"""
        try:
            # Verificar se usuário já existe
            if User.query.filter_by(username=username).first():
                return None, "Nome de usuário já existe"
            
            if User.query.filter_by(email=email).first():
                return None, "Email já cadastrado"
            
            # Criar usuário
            user = User(
                username=username,
                email=email,
                is_admin=is_admin
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Log criação
            AuditLog.log_action(
                user_id=created_by,
                action=ActionType.CREATE,
                resource_type='user',
                resource_id=str(user.id),
                description=f"Usuário criado: {username}",
                success=True
            )
            
            return user, "Usuário criado com sucesso"
            
        except Exception as e:
            db.session.rollback()
            return None, f"Erro ao criar usuário: {e}"
    
    @staticmethod
    def update_user(user_id, data, updated_by=None):
        """Atualiza dados do usuário"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "Usuário não encontrado"
            
            # Atualizar campos permitidos
            if 'email' in data:
                # Verificar se email já existe
                existing = User.query.filter(
                    User.email == data['email'],
                    User.id != user_id
                ).first()
                if existing:
                    return None, "Email já cadastrado"
                user.email = data['email']
            
            if 'is_admin' in data:
                user.is_admin = data['is_admin']
            
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            if 'password' in data and data['password']:
                user.set_password(data['password'])
            
            db.session.commit()
            
            # Log atualização
            AuditLog.log_action(
                user_id=updated_by,
                action=ActionType.UPDATE,
                resource_type='user',
                resource_id=str(user.id),
                description=f"Usuário atualizado: {user.username}",
                details=data,
                success=True
            )
            
            return user, "Usuário atualizado com sucesso"
            
        except Exception as e:
            db.session.rollback()
            return None, f"Erro ao atualizar usuário: {e}"
    
    @staticmethod
    def get_current_user(user_id):
        """Obtém dados do usuário atual"""
        try:
            user = User.query.get(user_id)
            if user and user.is_active:
                return user.to_dict()
            return None
        except:
            return None

