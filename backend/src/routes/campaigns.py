"""
Rotas de campanhas de envio
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.campaign import Campaign, CampaignType, CampaignStatus
from ..models.audit import AuditLog, ActionType
from ..services.auth_service import AuthService
from ..services.email_service import EmailService
from ..services.whatsapp_service import WhatsAppService
from ..config.database import db

campaigns_bp = Blueprint('campaigns', __name__)

@campaigns_bp.route('/', methods=['GET'])
@jwt_required()
def get_campaigns():
    """Lista todas as campanhas"""
    try:
        current_user_id = get_jwt_identity()
        
        # Parâmetros de filtro
        status = request.args.get('status')
        type_filter = request.args.get('type')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Query base
        query = Campaign.query
        
        # Aplicar filtros
        if status:
            query = query.filter(Campaign.status == CampaignStatus(status))
        
        if type_filter:
            query = query.filter(Campaign.type == CampaignType(type_filter))
        
        # Ordenar por data de criação
        query = query.order_by(Campaign.created_at.desc())
        
        # Paginação
        campaigns = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'campaigns': [campaign.to_dict() for campaign in campaigns.items],
                'total': campaigns.total,
                'pages': campaigns.pages,
                'current_page': page,
                'per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@campaigns_bp.route('/', methods=['POST'])
@jwt_required()
def create_campaign():
    """Cria nova campanha"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['name', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo {field} é obrigatório'
                }), 400
        
        # Criar campanha
        campaign = Campaign(
            name=data['name'],
            description=data.get('description', ''),
            type=CampaignType(data['type']),
            email_template_id=data.get('email_template_id'),
            whatsapp_template_id=data.get('whatsapp_template_id'),
            target_filter=data.get('target_filter', {}),
            scheduled_at=datetime.fromisoformat(data['scheduled_at']) if data.get('scheduled_at') else None,
            created_by=current_user_id
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        # Log da criação
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.CREATE,
            resource_type='campaign',
            resource_id=str(campaign.id),
            description=f"Campanha criada: {campaign.name}",
            details=data,
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Campanha criada com sucesso',
            'data': campaign.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@campaigns_bp.route('/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    """Obtém campanha específica"""
    try:
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({
                'success': False,
                'message': 'Campanha não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': campaign.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@campaigns_bp.route('/<int:campaign_id>', methods=['PUT'])
@jwt_required()
def update_campaign(campaign_id):
    """Atualiza campanha"""
    try:
        current_user_id = get_jwt_identity()
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({
                'success': False,
                'message': 'Campanha não encontrada'
            }), 404
        
        # Verificar se campanha pode ser editada
        if campaign.status in [CampaignStatus.RUNNING, CampaignStatus.COMPLETED]:
            return jsonify({
                'success': False,
                'message': 'Campanha não pode ser editada neste status'
            }), 400
        
        data = request.get_json()
        
        # Atualizar campos
        if 'name' in data:
            campaign.name = data['name']
        if 'description' in data:
            campaign.description = data['description']
        if 'email_template_id' in data:
            campaign.email_template_id = data['email_template_id']
        if 'whatsapp_template_id' in data:
            campaign.whatsapp_template_id = data['whatsapp_template_id']
        if 'target_filter' in data:
            campaign.target_filter = data['target_filter']
        if 'scheduled_at' in data:
            campaign.scheduled_at = datetime.fromisoformat(data['scheduled_at']) if data['scheduled_at'] else None
        
        campaign.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log da atualização
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.UPDATE,
            resource_type='campaign',
            resource_id=str(campaign.id),
            description=f"Campanha atualizada: {campaign.name}",
            details=data,
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Campanha atualizada com sucesso',
            'data': campaign.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@campaigns_bp.route('/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    """Exclui campanha"""
    try:
        current_user_id = get_jwt_identity()
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({
                'success': False,
                'message': 'Campanha não encontrada'
            }), 404
        
        # Verificar se campanha pode ser excluída
        if campaign.status == CampaignStatus.RUNNING:
            return jsonify({
                'success': False,
                'message': 'Campanha em execução não pode ser excluída'
            }), 400
        
        campaign_name = campaign.name
        
        db.session.delete(campaign)
        db.session.commit()
        
        # Log da exclusão
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.DELETE,
            resource_type='campaign',
            resource_id=str(campaign_id),
            description=f"Campanha excluída: {campaign_name}",
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Campanha excluída com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@campaigns_bp.route('/<int:campaign_id>/start', methods=['POST'])
@jwt_required()
def start_campaign(campaign_id):
    """Inicia execução da campanha"""
    try:
        current_user_id = get_jwt_identity()
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({
                'success': False,
                'message': 'Campanha não encontrada'
            }), 404
        
        # Verificar se campanha pode ser iniciada
        if campaign.status != CampaignStatus.DRAFT and campaign.status != CampaignStatus.SCHEDULED:
            return jsonify({
                'success': False,
                'message': 'Campanha não pode ser iniciada neste status'
            }), 400
        
        # Atualizar status
        campaign.status = CampaignStatus.RUNNING
        campaign.started_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log do início
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.CAMPAIGN_START,
            resource_type='campaign',
            resource_id=str(campaign.id),
            description=f"Campanha iniciada: {campaign.name}",
            success=True
        )
        
        # Aqui seria implementada a lógica de execução em background
        # Por enquanto, simular conclusão imediata
        campaign.status = CampaignStatus.COMPLETED
        campaign.completed_at = datetime.utcnow()
        campaign.sent_count = 10  # Simulado
        campaign.delivered_count = 8  # Simulado
        campaign.failed_count = 2  # Simulado
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Campanha iniciada com sucesso',
            'data': campaign.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@campaigns_bp.route('/<int:campaign_id>/stop', methods=['POST'])
@jwt_required()
def stop_campaign(campaign_id):
    """Para execução da campanha"""
    try:
        current_user_id = get_jwt_identity()
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({
                'success': False,
                'message': 'Campanha não encontrada'
            }), 404
        
        # Verificar se campanha pode ser parada
        if campaign.status != CampaignStatus.RUNNING:
            return jsonify({
                'success': False,
                'message': 'Campanha não está em execução'
            }), 400
        
        # Atualizar status
        campaign.status = CampaignStatus.CANCELLED
        campaign.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log da parada
        AuditLog.log_action(
            user_id=current_user_id,
            action=ActionType.UPDATE,
            resource_type='campaign',
            resource_id=str(campaign.id),
            description=f"Campanha cancelada: {campaign.name}",
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Campanha cancelada com sucesso',
            'data': campaign.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

@campaigns_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_campaign_stats():
    """Obtém estatísticas das campanhas"""
    try:
        # Contar campanhas por status
        stats = {
            'total': Campaign.query.count(),
            'draft': Campaign.query.filter_by(status=CampaignStatus.DRAFT).count(),
            'scheduled': Campaign.query.filter_by(status=CampaignStatus.SCHEDULED).count(),
            'running': Campaign.query.filter_by(status=CampaignStatus.RUNNING).count(),
            'completed': Campaign.query.filter_by(status=CampaignStatus.COMPLETED).count(),
            'failed': Campaign.query.filter_by(status=CampaignStatus.FAILED).count(),
            'cancelled': Campaign.query.filter_by(status=CampaignStatus.CANCELLED).count()
        }
        
        # Estatísticas de envio
        completed_campaigns = Campaign.query.filter_by(status=CampaignStatus.COMPLETED).all()
        
        total_sent = sum(c.sent_count or 0 for c in completed_campaigns)
        total_delivered = sum(c.delivered_count or 0 for c in completed_campaigns)
        total_failed = sum(c.failed_count or 0 for c in completed_campaigns)
        
        stats.update({
            'total_sent': total_sent,
            'total_delivered': total_delivered,
            'total_failed': total_failed,
            'success_rate': round((total_delivered / total_sent * 100) if total_sent > 0 else 0, 2)
        })
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {e}'
        }), 500

