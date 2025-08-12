"""
Rotas de campanhas do sistema CRC-ES
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import Campaign, Template, User, db, AuditLog
from datetime import datetime

campaigns_bp = Blueprint('campaigns', __name__)

@campaigns_bp.route('/', methods=['GET'])
@jwt_required()
def get_campaigns():
    """Listar campanhas"""
    try:
        campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
        return jsonify({
            'campaigns': [campaign.to_dict() for campaign in campaigns]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaigns_bp.route('/', methods=['POST'])
@jwt_required()
def create_campaign():
    """Criar nova campanha"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        campaign_type = data.get('type')  # 'email' ou 'whatsapp'
        template_id = data.get('template_id')
        
        if not name or not campaign_type:
            return jsonify({'error': 'Nome e tipo são obrigatórios'}), 400
        
        if campaign_type not in ['email', 'whatsapp']:
            return jsonify({'error': 'Tipo deve ser email ou whatsapp'}), 400
        
        # Verificar se template existe
        if template_id:
            template = Template.query.get(template_id)
            if not template:
                return jsonify({'error': 'Template não encontrado'}), 404
        
        # Criar campanha
        campaign = Campaign(
            name=name,
            description=description,
            type=campaign_type,
            template_id=template_id,
            created_by=user_id
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        # Log da criação
        audit_log = AuditLog(
            user_id=user_id,
            action='campaign_created',
            resource='campaign',
            resource_id=campaign.id,
            details=f'Campanha criada: {name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Campanha criada com sucesso',
            'campaign': campaign.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaigns_bp.route('/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    """Obter campanha específica"""
    try:
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({'error': 'Campanha não encontrada'}), 404
        
        return jsonify({'campaign': campaign.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaigns_bp.route('/<int:campaign_id>', methods=['PUT'])
@jwt_required()
def update_campaign(campaign_id):
    """Atualizar campanha"""
    try:
        user_id = get_jwt_identity()
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({'error': 'Campanha não encontrada'}), 404
        
        data = request.get_json()
        
        # Atualizar campos
        if 'name' in data:
            campaign.name = data['name']
        if 'description' in data:
            campaign.description = data['description']
        if 'template_id' in data:
            campaign.template_id = data['template_id']
        if 'status' in data:
            campaign.status = data['status']
        
        db.session.commit()
        
        # Log da atualização
        audit_log = AuditLog(
            user_id=user_id,
            action='campaign_updated',
            resource='campaign',
            resource_id=campaign.id,
            details=f'Campanha atualizada: {campaign.name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Campanha atualizada com sucesso',
            'campaign': campaign.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaigns_bp.route('/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    """Deletar campanha"""
    try:
        user_id = get_jwt_identity()
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({'error': 'Campanha não encontrada'}), 404
        
        campaign_name = campaign.name
        
        db.session.delete(campaign)
        db.session.commit()
        
        # Log da exclusão
        audit_log = AuditLog(
            user_id=user_id,
            action='campaign_deleted',
            resource='campaign',
            resource_id=campaign_id,
            details=f'Campanha deletada: {campaign_name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'message': 'Campanha deletada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaigns_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_campaign_stats():
    """Obter estatísticas das campanhas"""
    try:
        # Estatísticas gerais
        total_campaigns = Campaign.query.count()
        active_campaigns = Campaign.query.filter_by(status='sending').count()
        completed_campaigns = Campaign.query.filter_by(status='completed').count()
        
        # Campanhas por tipo
        email_campaigns = Campaign.query.filter_by(type='email').count()
        whatsapp_campaigns = Campaign.query.filter_by(type='whatsapp').count()
        
        # Campanhas recentes
        recent_campaigns = Campaign.query.order_by(Campaign.created_at.desc()).limit(5).all()
        
        return jsonify({
            'stats': {
                'total_campaigns': total_campaigns,
                'active_campaigns': active_campaigns,
                'completed_campaigns': completed_campaigns,
                'email_campaigns': email_campaigns,
                'whatsapp_campaigns': whatsapp_campaigns
            },
            'recent_campaigns': [campaign.to_dict() for campaign in recent_campaigns]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

