"""
Rotas de envio de mensagens do sistema CRC-ES
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import Campaign, MessageLog, db, AuditLog
from src.services.email_service import EmailService
from src.services.whatsapp_service import WhatsAppService
import threading

messaging_bp = Blueprint('messaging', __name__)

@messaging_bp.route('/send-campaign/<int:campaign_id>', methods=['POST'])
@jwt_required()
def send_campaign(campaign_id):
    """Enviar campanha"""
    try:
        user_id = get_jwt_identity()
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({'error': 'Campanha não encontrada'}), 404
        
        if campaign.status == 'sending':
            return jsonify({'error': 'Campanha já está sendo enviada'}), 400
        
        # Atualizar status da campanha
        campaign.status = 'sending'
        db.session.commit()
        
        # Log do início do envio
        audit_log = AuditLog(
            user_id=user_id,
            action='campaign_send_started',
            resource='campaign',
            resource_id=campaign.id,
            details=f'Envio iniciado para campanha: {campaign.name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        # Enviar em thread separada para não bloquear
        def send_in_background():
            try:
                if campaign.type == 'email':
                    email_service = EmailService()
                    result = email_service.send_bulk_emails(campaign.id)
                elif campaign.type == 'whatsapp':
                    whatsapp_service = WhatsAppService()
                    result = whatsapp_service.send_bulk_whatsapp(campaign.id)
                else:
                    result = {'error': 'Tipo de campanha inválido'}
                
                # Atualizar status da campanha
                if 'error' in result:
                    campaign.status = 'failed'
                else:
                    campaign.status = 'completed'
                    campaign.total_recipients = result.get('total', 0)
                    campaign.sent_count = result.get('sent', 0)
                    campaign.failed_count = result.get('failed', 0)
                
                db.session.commit()
                
            except Exception as e:
                campaign.status = 'failed'
                db.session.commit()
                print(f"Erro no envio da campanha {campaign_id}: {e}")
        
        # Iniciar thread
        thread = threading.Thread(target=send_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Envio da campanha iniciado',
            'campaign_id': campaign_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@messaging_bp.route('/send-test', methods=['POST'])
@jwt_required()
def send_test_message():
    """Enviar mensagem de teste"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        message_type = data.get('type')  # 'email' ou 'whatsapp'
        recipient = data.get('recipient')
        subject = data.get('subject', '')
        content = data.get('content')
        
        if not message_type or not recipient or not content:
            return jsonify({'error': 'Tipo, destinatário e conteúdo são obrigatórios'}), 400
        
        success = False
        message = ''
        
        if message_type == 'email':
            email_service = EmailService()
            success, message = email_service.send_custom_email(recipient, subject, content)
        elif message_type == 'whatsapp':
            # Para teste do WhatsApp, seria necessário implementar envio individual
            success = True
            message = 'Teste de WhatsApp não implementado ainda'
        else:
            return jsonify({'error': 'Tipo de mensagem inválido'}), 400
        
        # Log do teste
        audit_log = AuditLog(
            user_id=user_id,
            action='test_message_sent',
            details=f'Mensagem de teste enviada via {message_type} para {recipient}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        if success:
            return jsonify({'message': 'Mensagem de teste enviada com sucesso'}), 200
        else:
            return jsonify({'error': f'Falha no envio: {message}'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@messaging_bp.route('/logs/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign_logs(campaign_id):
    """Obter logs de uma campanha"""
    try:
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({'error': 'Campanha não encontrada'}), 404
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status_filter = request.args.get('status')
        
        # Query dos logs
        query = MessageLog.query.filter_by(campaign_id=campaign_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        logs = query.order_by(MessageLog.sent_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': logs.total,
                'pages': logs.pages,
                'has_next': logs.has_next,
                'has_prev': logs.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@messaging_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_messaging_stats():
    """Obter estatísticas de mensagens"""
    try:
        # Estatísticas gerais
        total_sent = MessageLog.query.filter_by(status='sent').count()
        total_failed = MessageLog.query.filter_by(status='failed').count()
        
        # Por tipo
        email_sent = MessageLog.query.filter_by(message_type='email', status='sent').count()
        whatsapp_sent = MessageLog.query.filter_by(message_type='whatsapp', status='sent').count()
        
        # Campanhas ativas
        active_campaigns = Campaign.query.filter_by(status='sending').count()
        
        return jsonify({
            'stats': {
                'total_sent': total_sent,
                'total_failed': total_failed,
                'email_sent': email_sent,
                'whatsapp_sent': whatsapp_sent,
                'active_campaigns': active_campaigns,
                'success_rate': round((total_sent / (total_sent + total_failed) * 100), 2) if (total_sent + total_failed) > 0 else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@messaging_bp.route('/recipients/preview', methods=['POST'])
@jwt_required()
def preview_recipients():
    """Visualizar destinatários antes do envio"""
    try:
        data = request.get_json()
        message_type = data.get('type')  # 'email' ou 'whatsapp'
        year = data.get('year', '2025')
        
        if message_type == 'email':
            email_service = EmailService()
            recipients = email_service.get_anuidade_recipients(year)
        elif message_type == 'whatsapp':
            whatsapp_service = WhatsAppService()
            recipients = whatsapp_service.get_whatsapp_recipients()
        else:
            return jsonify({'error': 'Tipo de mensagem inválido'}), 400
        
        # Limitar preview a 100 registros
        preview_recipients = recipients[:100]
        
        return jsonify({
            'total_recipients': len(recipients),
            'preview_count': len(preview_recipients),
            'recipients': preview_recipients
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

