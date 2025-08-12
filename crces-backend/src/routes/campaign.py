from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime

from src.models.user import User
from src.models.campaign import db, Campaign, CampaignMessage, CampaignType, CampaignStatus
from src.models.template import EmailTemplate, WhatsAppTemplate
from src.models.audit import AuditLog

campaign_bp = Blueprint('campaign', __name__)

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

@campaign_bp.route('/', methods=['GET'])
@jwt_required()
@require_permission('view_dashboard')
def get_campaigns():
    """Lista todas as campanhas com paginação e filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        type_filter = request.args.get('type', '')
        
        # Limita per_page para evitar sobrecarga
        per_page = min(per_page, 100)
        
        # Query base
        query = Campaign.query
        
        # Filtro de busca
        if search:
            query = query.filter(
                or_(
                    Campaign.name.ilike(f'%{search}%'),
                    Campaign.description.ilike(f'%{search}%')
                )
            )
        
        # Filtro por status
        if status_filter:
            try:
                status = CampaignStatus(status_filter)
                query = query.filter(Campaign.status == status)
            except ValueError:
                pass
        
        # Filtro por tipo
        if type_filter:
            try:
                campaign_type = CampaignType(type_filter)
                query = query.filter(Campaign.type == campaign_type)
            except ValueError:
                pass
        
        # Ordena por data de criação (mais recentes primeiro)
        query = query.order_by(Campaign.created_at.desc())
        
        # Paginação
        campaigns = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'campaigns': [campaign.to_dict() for campaign in campaigns.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': campaigns.total,
                'pages': campaigns.pages,
                'has_next': campaigns.has_next,
                'has_prev': campaigns.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar campanhas: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['GET'])
@jwt_required()
@require_permission('view_dashboard')
def get_campaign(campaign_id):
    """Obtém uma campanha específica"""
    try:
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({'message': 'Campanha não encontrada'}), 404
        
        include_messages = request.args.get('include_messages', 'false').lower() == 'true'
        
        return jsonify({
            'campaign': campaign.to_dict(include_messages=include_messages)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter campanha: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campaign_bp.route('/', methods=['POST'])
@jwt_required()
@require_permission('create_campaigns')
def create_campaign():
    """Cria uma nova campanha"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Validações obrigatórias
        required_fields = ['name', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Valida tipo da campanha
        try:
            campaign_type = CampaignType(data['type'])
        except ValueError:
            return jsonify({'message': 'Tipo de campanha inválido'}), 400
        
        # Valida templates se fornecidos
        email_template = None
        whatsapp_template = None
        
        if campaign_type in [CampaignType.EMAIL, CampaignType.BOTH]:
            if not data.get('email_template_id'):
                return jsonify({'message': 'Template de email é obrigatório para campanhas de email'}), 400
            
            email_template = EmailTemplate.query.get(data['email_template_id'])
            if not email_template or not email_template.is_active:
                return jsonify({'message': 'Template de email não encontrado ou inativo'}), 404
        
        if campaign_type in [CampaignType.WHATSAPP, CampaignType.BOTH]:
            if not data.get('whatsapp_template_id'):
                return jsonify({'message': 'Template de WhatsApp é obrigatório para campanhas de WhatsApp'}), 400
            
            whatsapp_template = WhatsAppTemplate.query.get(data['whatsapp_template_id'])
            if not whatsapp_template or not whatsapp_template.is_active:
                return jsonify({'message': 'Template de WhatsApp não encontrado ou inativo'}), 404
        
        # Cria nova campanha
        campaign = Campaign(
            name=data['name'],
            description=data.get('description', ''),
            type=campaign_type,
            email_template_id=data.get('email_template_id'),
            whatsapp_template_id=data.get('whatsapp_template_id'),
            created_by=current_user_id
        )
        
        # Define critérios de seleção se fornecidos
        if data.get('selection_criteria'):
            campaign.set_selection_criteria(data['selection_criteria'])
        
        # Define agendamento se fornecido
        if data.get('scheduled_at'):
            try:
                campaign.scheduled_at = datetime.fromisoformat(data['scheduled_at'].replace('Z', '+00:00'))
                campaign.status = CampaignStatus.SCHEDULED
            except ValueError:
                return jsonify({'message': 'Formato de data de agendamento inválido'}), 400
        
        db.session.add(campaign)
        db.session.commit()
        
        # Log criação da campanha
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='CREATE',
            resource_type='Campaign',
            resource_id=str(campaign.id),
            new_values=campaign.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Campanha criada com sucesso',
            'campaign': campaign.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar campanha: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['PUT'])
@jwt_required()
@require_permission('create_campaigns')
def update_campaign(campaign_id):
    """Atualiza uma campanha"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'message': 'Campanha não encontrada'}), 404
        
        # Não permite editar campanhas em execução ou finalizadas
        if campaign.status in [CampaignStatus.RUNNING, CampaignStatus.COMPLETED]:
            return jsonify({'message': 'Não é possível editar campanhas em execução ou finalizadas'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Armazena valores antigos para auditoria
        old_values = campaign.to_dict()
        
        # Atualiza campos permitidos
        if 'name' in data:
            campaign.name = data['name']
        
        if 'description' in data:
            campaign.description = data['description']
        
        if 'type' in data:
            try:
                campaign.type = CampaignType(data['type'])
            except ValueError:
                return jsonify({'message': 'Tipo de campanha inválido'}), 400
        
        if 'email_template_id' in data:
            if data['email_template_id']:
                email_template = EmailTemplate.query.get(data['email_template_id'])
                if not email_template or not email_template.is_active:
                    return jsonify({'message': 'Template de email não encontrado ou inativo'}), 404
            campaign.email_template_id = data['email_template_id']
        
        if 'whatsapp_template_id' in data:
            if data['whatsapp_template_id']:
                whatsapp_template = WhatsAppTemplate.query.get(data['whatsapp_template_id'])
                if not whatsapp_template or not whatsapp_template.is_active:
                    return jsonify({'message': 'Template de WhatsApp não encontrado ou inativo'}), 404
            campaign.whatsapp_template_id = data['whatsapp_template_id']
        
        if 'selection_criteria' in data:
            campaign.set_selection_criteria(data['selection_criteria'])
        
        if 'scheduled_at' in data:
            if data['scheduled_at']:
                try:
                    campaign.scheduled_at = datetime.fromisoformat(data['scheduled_at'].replace('Z', '+00:00'))
                    if campaign.status == CampaignStatus.DRAFT:
                        campaign.status = CampaignStatus.SCHEDULED
                except ValueError:
                    return jsonify({'message': 'Formato de data de agendamento inválido'}), 400
            else:
                campaign.scheduled_at = None
                if campaign.status == CampaignStatus.SCHEDULED:
                    campaign.status = CampaignStatus.DRAFT
        
        db.session.commit()
        
        # Log atualização da campanha
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='UPDATE',
            resource_type='Campaign',
            resource_id=str(campaign.id),
            old_values=old_values,
            new_values=campaign.to_dict(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({
            'message': 'Campanha atualizada com sucesso',
            'campaign': campaign.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar campanha: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
@require_permission('create_campaigns')
def delete_campaign(campaign_id):
    """Cancela uma campanha"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'message': 'Campanha não encontrada'}), 404
        
        # Não permite cancelar campanhas já finalizadas
        if campaign.status == CampaignStatus.COMPLETED:
            return jsonify({'message': 'Não é possível cancelar campanhas finalizadas'}), 400
        
        # Armazena valores antigos para auditoria
        old_values = campaign.to_dict()
        
        # Cancela a campanha
        campaign.status = CampaignStatus.CANCELLED
        db.session.commit()
        
        # Log cancelamento da campanha
        AuditLog.log_action(
            user_id=current_user_id,
            username=current_user.username,
            action_type='CANCEL',
            resource_type='Campaign',
            resource_id=str(campaign.id),
            old_values=old_values,
            new_values={'status': CampaignStatus.CANCELLED.value},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            endpoint=request.endpoint,
            method=request.method,
            success=True
        )
        
        return jsonify({'message': 'Campanha cancelada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao cancelar campanha: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campaign_bp.route('/<int:campaign_id>/messages', methods=['GET'])
@jwt_required()
@require_permission('view_dashboard')
def get_campaign_messages(campaign_id):
    """Lista mensagens de uma campanha"""
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'message': 'Campanha não encontrada'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status_filter = request.args.get('status', '')
        
        # Limita per_page para evitar sobrecarga
        per_page = min(per_page, 200)
        
        # Query base
        query = CampaignMessage.query.filter_by(campaign_id=campaign_id)
        
        # Filtro por status (email ou whatsapp)
        if status_filter:
            query = query.filter(
                or_(
                    CampaignMessage.email_status == status_filter,
                    CampaignMessage.whatsapp_status == status_filter
                )
            )
        
        # Ordena por data de criação
        query = query.order_by(CampaignMessage.created_at.desc())
        
        # Paginação
        messages = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'messages': [message.to_dict() for message in messages.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': messages.total,
                'pages': messages.pages,
                'has_next': messages.has_next,
                'has_prev': messages.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar mensagens da campanha: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campaign_bp.route('/<int:campaign_id>/statistics', methods=['GET'])
@jwt_required()
@require_permission('view_dashboard')
def get_campaign_statistics(campaign_id):
    """Obtém estatísticas detalhadas de uma campanha"""
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'message': 'Campanha não encontrada'}), 404
        
        # Atualiza estatísticas
        campaign.update_statistics()
        
        return jsonify({
            'statistics': campaign.to_dict()['statistics']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas da campanha: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

