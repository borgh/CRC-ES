from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from src.models.user import User
from src.models.template import db, EmailTemplate, WhatsAppTemplate
from src.models.audit import AuditLog

template_bp = Blueprint('template', __name__)

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

# Rotas para Templates de Email

@template_bp.route('/email', methods=['GET'])
@jwt_required()
@require_permission('view_dashboard')
def get_email_templates():
    """Lista todos os templates de email"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        # Limita per_page para evitar sobrecarga
        per_page = min(per_page, 100)
        
        # Query base
        query = EmailTemplate.query
        
        # Filtro de busca
        if search:
            query = query.filter(
                or_(
                    EmailTemplate.name.ilike(f'%{search}%'),
                    EmailTemplate.description.ilike(f'%{search}%')
                )
            )
        
        # Filtro por templates ativos
        if active_only:
            query = query.filter(EmailTemplate.is_active == True)
        
        # Ordena por data de criação (mais recentes primeiro)
        query = query.order_by(EmailTemplate.created_at.desc())
        
        # Paginação
        templates = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        include_content = request.args.get('include_content', 'false').lower() == 'true'
        
        return jsonify({
            'templates': [template.to_dict(include_content=include_content) for template in templates.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': templates.total,
                'pages': templates.pages,
                'has_next': templates.has_next,
                'has_prev': templates.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar templates de email: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@template_bp.route('/email/<int:template_id>', methods=['GET'])
@jwt_required()
@require_permission('view_dashboard')
def get_email_template(template_id):
    """Obtém um template de email específico"""
    try:
        template = EmailTemplate.query.get(template_id)
        
        if not template:
            return jsonify({'message': 'Template não encontrado'}), 404
        
        return jsonify({
            'template': template.to_dict(include_content=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter template de email: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@template_bp.route('/email', methods=['POST'])
@jwt_required()
@require_permission('manage_templates')
def create_email_template():
    """Cria um novo template de email"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validações obrigatórias
        required_fields = ['name', 'subject', 'html_content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Cria novo template
        template = EmailTemplate(
            name=data['name'],
            description=data.get('description', ''),
            subject=data['subject'],
            html_content=data['html_content'],
            text_content=data.get('text_content', ''),
            created_by=current_user_id
        )
        
        # Define variáveis disponíveis
        if data.get('available_variables'):
            template.set_available_variables(data['available_variables'])
        else:
            # Extrai automaticamente das variáveis do conteúdo
            variables = template.extract_variables_from_content()
            template.set_available_variables(variables)
        
        # Valida template
        errors = template.validate_template()
        if errors:
            return jsonify({'message': 'Erros de validação', 'errors': errors}), 400
        
        db.session.add(template)
        db.session.commit()
        
        # Log criação do template
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='CREATE',
            resource_type='EmailTemplate',
            resource_id=str(template.id),
            new_values=template.to_dict(include_content=False),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Template de email criado com sucesso',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar template de email: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@template_bp.route('/email/<int:template_id>', methods=['PUT'])
@jwt_required()
@require_permission('manage_templates')
def update_email_template(template_id):
    """Atualiza um template de email"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        template = EmailTemplate.query.get(template_id)
        if not template:
            return jsonify({'message': 'Template não encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Armazena valores antigos para auditoria
        old_values = template.to_dict(include_content=False)
        
        # Atualiza campos permitidos
        if 'name' in data:
            template.name = data['name']
        
        if 'description' in data:
            template.description = data['description']
        
        if 'subject' in data:
            template.subject = data['subject']
        
        if 'html_content' in data:
            template.html_content = data['html_content']
        
        if 'text_content' in data:
            template.text_content = data['text_content']
        
        if 'is_active' in data:
            template.is_active = data['is_active']
        
        # Atualiza variáveis disponíveis
        if 'available_variables' in data:
            template.set_available_variables(data['available_variables'])
        else:
            # Extrai automaticamente das variáveis do conteúdo
            variables = template.extract_variables_from_content()
            template.set_available_variables(variables)
        
        # Incrementa versão
        template.version += 1
        
        # Valida template
        errors = template.validate_template()
        if errors:
            return jsonify({'message': 'Erros de validação', 'errors': errors}), 400
        
        db.session.commit()
        
        # Log atualização do template
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='UPDATE',
            resource_type='EmailTemplate',
            resource_id=str(template.id),
            old_values=old_values,
            new_values=template.to_dict(include_content=False),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Template de email atualizado com sucesso',
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar template de email: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@template_bp.route('/email/<int:template_id>/clone', methods=['POST'])
@jwt_required()
@require_permission('manage_templates')
def clone_email_template(template_id):
    """Clona um template de email"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        template = EmailTemplate.query.get(template_id)
        if not template:
            return jsonify({'message': 'Template não encontrado'}), 404
        
        data = request.get_json() or {}
        new_name = data.get('name', f"{template.name} (Cópia)")
        
        # Clona template
        cloned_template = template.clone(new_name=new_name, created_by=current_user_id)
        
        db.session.add(cloned_template)
        db.session.commit()
        
        # Log clonagem do template
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='CLONE',
            resource_type='EmailTemplate',
            resource_id=str(cloned_template.id),
            new_values=cloned_template.to_dict(include_content=False),
            additional_data={'original_template_id': template_id},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Template clonado com sucesso',
            'template': cloned_template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao clonar template de email: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

# Rotas para Templates de WhatsApp

@template_bp.route('/whatsapp', methods=['GET'])
@jwt_required()
@require_permission('view_dashboard')
def get_whatsapp_templates():
    """Lista todos os templates de WhatsApp"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        # Limita per_page para evitar sobrecarga
        per_page = min(per_page, 100)
        
        # Query base
        query = WhatsAppTemplate.query
        
        # Filtro de busca
        if search:
            query = query.filter(
                or_(
                    WhatsAppTemplate.name.ilike(f'%{search}%'),
                    WhatsAppTemplate.description.ilike(f'%{search}%')
                )
            )
        
        # Filtro por templates ativos
        if active_only:
            query = query.filter(WhatsAppTemplate.is_active == True)
        
        # Ordena por data de criação (mais recentes primeiro)
        query = query.order_by(WhatsAppTemplate.created_at.desc())
        
        # Paginação
        templates = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        include_content = request.args.get('include_content', 'false').lower() == 'true'
        
        return jsonify({
            'templates': [template.to_dict(include_content=include_content) for template in templates.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': templates.total,
                'pages': templates.pages,
                'has_next': templates.has_next,
                'has_prev': templates.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar templates de WhatsApp: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@template_bp.route('/whatsapp/<int:template_id>', methods=['GET'])
@jwt_required()
@require_permission('view_dashboard')
def get_whatsapp_template(template_id):
    """Obtém um template de WhatsApp específico"""
    try:
        template = WhatsAppTemplate.query.get(template_id)
        
        if not template:
            return jsonify({'message': 'Template não encontrado'}), 404
        
        return jsonify({
            'template': template.to_dict(include_content=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter template de WhatsApp: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@template_bp.route('/whatsapp', methods=['POST'])
@jwt_required()
@require_permission('manage_templates')
def create_whatsapp_template():
    """Cria um novo template de WhatsApp"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validações obrigatórias
        required_fields = ['name', 'message_content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Cria novo template
        template = WhatsAppTemplate(
            name=data['name'],
            description=data.get('description', ''),
            message_content=data['message_content'],
            has_attachment=data.get('has_attachment', False),
            attachment_type=data.get('attachment_type'),
            attachment_caption=data.get('attachment_caption', ''),
            created_by=current_user_id
        )
        
        # Define variáveis disponíveis
        if data.get('available_variables'):
            template.set_available_variables(data['available_variables'])
        else:
            # Extrai automaticamente das variáveis do conteúdo
            variables = template.extract_variables_from_content()
            template.set_available_variables(variables)
        
        # Valida template
        errors = template.validate_template()
        if errors:
            return jsonify({'message': 'Erros de validação', 'errors': errors}), 400
        
        db.session.add(template)
        db.session.commit()
        
        # Log criação do template
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='CREATE',
            resource_type='WhatsAppTemplate',
            resource_id=str(template.id),
            new_values=template.to_dict(include_content=False),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Template de WhatsApp criado com sucesso',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar template de WhatsApp: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@template_bp.route('/whatsapp/<int:template_id>', methods=['PUT'])
@jwt_required()
@require_permission('manage_templates')
def update_whatsapp_template(template_id):
    """Atualiza um template de WhatsApp"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        template = WhatsAppTemplate.query.get(template_id)
        if not template:
            return jsonify({'message': 'Template não encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Armazena valores antigos para auditoria
        old_values = template.to_dict(include_content=False)
        
        # Atualiza campos permitidos
        if 'name' in data:
            template.name = data['name']
        
        if 'description' in data:
            template.description = data['description']
        
        if 'message_content' in data:
            template.message_content = data['message_content']
        
        if 'has_attachment' in data:
            template.has_attachment = data['has_attachment']
        
        if 'attachment_type' in data:
            template.attachment_type = data['attachment_type']
        
        if 'attachment_caption' in data:
            template.attachment_caption = data['attachment_caption']
        
        if 'is_active' in data:
            template.is_active = data['is_active']
        
        # Atualiza variáveis disponíveis
        if 'available_variables' in data:
            template.set_available_variables(data['available_variables'])
        else:
            # Extrai automaticamente das variáveis do conteúdo
            variables = template.extract_variables_from_content()
            template.set_available_variables(variables)
        
        # Incrementa versão
        template.version += 1
        
        # Valida template
        errors = template.validate_template()
        if errors:
            return jsonify({'message': 'Erros de validação', 'errors': errors}), 400
        
        db.session.commit()
        
        # Log atualização do template
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='UPDATE',
            resource_type='WhatsAppTemplate',
            resource_id=str(template.id),
            old_values=old_values,
            new_values=template.to_dict(include_content=False),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Template de WhatsApp atualizado com sucesso',
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar template de WhatsApp: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@template_bp.route('/whatsapp/<int:template_id>/clone', methods=['POST'])
@jwt_required()
@require_permission('manage_templates')
def clone_whatsapp_template(template_id):
    """Clona um template de WhatsApp"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        template = WhatsAppTemplate.query.get(template_id)
        if not template:
            return jsonify({'message': 'Template não encontrado'}), 404
        
        data = request.get_json() or {}
        new_name = data.get('name', f"{template.name} (Cópia)")
        
        # Clona template
        cloned_template = template.clone(new_name=new_name, created_by=current_user_id)
        
        db.session.add(cloned_template)
        db.session.commit()
        
        # Log clonagem do template
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='CLONE',
            resource_type='WhatsAppTemplate',
            resource_id=str(cloned_template.id),
            new_values=cloned_template.to_dict(include_content=False),
            additional_data={'original_template_id': template_id},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Template clonado com sucesso',
            'template': cloned_template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao clonar template de WhatsApp: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

