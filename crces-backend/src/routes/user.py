from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import or_

from src.models.user import db, User, Role, Permission
from src.models.audit import AuditLog

user_bp = Blueprint('user', __name__)

def require_permission(permission_name):
    """Decorator para verificar permissões"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.has_permission(permission_name):
                return jsonify({'message': 'Permissão insuficiente'}), 403
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@user_bp.route('/', methods=['GET'])
@jwt_required()
@require_permission('manage_users')
def get_users():
    """Lista todos os usuários com paginação e filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        role_filter = request.args.get('role', '')
        active_filter = request.args.get('active', '')
        
        # Limita per_page para evitar sobrecarga
        per_page = min(per_page, 100)
        
        # Query base
        query = User.query
        
        # Filtro de busca
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )
        
        # Filtro por role
        if role_filter:
            query = query.join(User.roles).filter(Role.name == role_filter)
        
        # Filtro por status ativo
        if active_filter:
            is_active = active_filter.lower() == 'true'
            query = query.filter(User.is_active == is_active)
        
        # Paginação
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@require_permission('manage_users')
def get_user(user_id):
    """Obtém um usuário específico"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter usuário: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@user_bp.route('/', methods=['POST'])
@jwt_required()
@require_permission('manage_users')
def create_user():
    """Cria um novo usuário"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validações obrigatórias
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Verifica se username já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username já existe'}), 409
        
        # Verifica se email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email já existe'}), 409
        
        # Cria novo usuário
        user = User(
            username=data['username'],
            email=data['email'],
            is_active=data.get('is_active', True),
            is_verified=data.get('is_verified', False)
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Para obter o ID
        
        # Adiciona roles se fornecidos
        role_names = data.get('roles', [])
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)
        
        db.session.commit()
        
        # Log criação do usuário
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='CREATE',
            resource_type='User',
            resource_id=str(user.id),
            new_values=user.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar usuário: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_permission('manage_users')
def update_user(user_id):
    """Atualiza um usuário"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Armazena valores antigos para auditoria
        old_values = user.to_dict()
        
        # Atualiza campos permitidos
        if 'username' in data and data['username'] != user.username:
            # Verifica se novo username já existe
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'message': 'Username já existe'}), 409
            user.username = data['username']
        
        if 'email' in data and data['email'] != user.email:
            # Verifica se novo email já existe
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'message': 'Email já existe'}), 409
            user.email = data['email']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'is_verified' in data:
            user.is_verified = data['is_verified']
        
        # Atualiza senha se fornecida
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Atualiza roles se fornecidos
        if 'roles' in data:
            user.roles.clear()
            for role_name in data['roles']:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    user.roles.append(role)
        
        # Desbloqueia conta se solicitado
        if data.get('unlock_account'):
            user.unlock_account()
        
        db.session.commit()
        
        # Log atualização do usuário
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='UPDATE',
            resource_type='User',
            resource_id=str(user.id),
            old_values=old_values,
            new_values=user.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Usuário atualizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar usuário: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@require_permission('manage_users')
def delete_user(user_id):
    """Desativa um usuário (soft delete)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Não permite deletar a si mesmo
        if user_id == current_user_id:
            return jsonify({'message': 'Não é possível deletar sua própria conta'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Armazena valores antigos para auditoria
        old_values = user.to_dict()
        
        # Soft delete - apenas desativa o usuário
        user.is_active = False
        db.session.commit()
        
        # Log desativação do usuário
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='DELETE',
            resource_type='User',
            resource_id=str(user.id),
            old_values=old_values,
            new_values={'is_active': False},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({'message': 'Usuário desativado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao deletar usuário: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@user_bp.route('/roles', methods=['GET'])
@jwt_required()
@require_permission('manage_users')
def get_roles():
    """Lista todos os roles disponíveis"""
    try:
        roles = Role.query.all()
        
        return jsonify({
            'roles': [role.to_dict() for role in roles]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar roles: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@user_bp.route('/permissions', methods=['GET'])
@jwt_required()
@require_permission('system_admin')
def get_permissions():
    """Lista todas as permissões disponíveis"""
    try:
        permissions = Permission.query.all()
        
        return jsonify({
            'permissions': [perm.to_dict() for perm in permissions]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar permissões: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Permite ao usuário atualizar seu próprio perfil"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Armazena valores antigos para auditoria
        old_values = user.to_dict()
        
        # Campos que o usuário pode atualizar em seu próprio perfil
        if 'email' in data and data['email'] != user.email:
            # Verifica se novo email já existe
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'message': 'Email já existe'}), 409
            user.email = data['email']
            user.is_verified = False  # Requer nova verificação
        
        db.session.commit()
        
        # Log atualização do perfil
        AuditLog.log_action(
            user_id=current_user_id,
            username=user.username,
            action_type='UPDATE_PROFILE',
            resource_type='User',
            resource_id=str(user.id),
            old_values=old_values,
            new_values=user.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar perfil: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Permite ao usuário alterar sua própria senha"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'message': 'Senha atual e nova senha são obrigatórias'}), 400
        
        # Verifica senha atual
        if not user.check_password(current_password):
            AuditLog.log_action(
                user_id=current_user_id,
                username=user.username,
                action_type='CHANGE_PASSWORD_FAILED',
                resource_type='User',
                resource_id=str(user.id),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                endpoint=request.endpoint,
                method=request.method,
                success=False,
                error_message='Senha atual incorreta'
            )
            return jsonify({'message': 'Senha atual incorreta'}), 401
        
        # Atualiza senha
        user.set_password(new_password)
        db.session.commit()
        
        # Log alteração de senha
        AuditLog.log_action(
            user_id=current_user_id,
            username=user.username,
            action_type='CHANGE_PASSWORD',
            resource_type='User',
            resource_id=str(user.id),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao alterar senha: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500
