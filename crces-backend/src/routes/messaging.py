from flask import Blueprint, request, jsonify, g
from src.services.whatsapp_service import WhatsAppService
from src.services.email_service import EmailService
from src.services.security_service import SecurityService
from src.models.campaign import Campaign, CampaignMessage
from src.models.audit import AuditLog
from src.models.user import db
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

messaging_bp = Blueprint('messaging', __name__)
security = SecurityService()
whatsapp_service = WhatsAppService()
email_service = EmailService()

@messaging_bp.route('/test-connections', methods=['GET'])
@security.require_auth
@security.rate_limit('api')
def test_connections():
    """Testa conexões com serviços de mensagem"""
    try:
        results = {
            'whatsapp': whatsapp_service.check_connection(),
            'email': email_service.test_connection()
        }
        
        # Log de auditoria
        AuditLog.create_log(
            user_id=g.current_user['user_id'],
            action='TEST_CONNECTIONS',
            resource='Messaging Services',
            description=f"Teste de conexões: WhatsApp={results['whatsapp']}, Email={results['email']}",
            ip_address=security.get_client_ip()
        )
        
        return jsonify({
            'success': True,
            'connections': results
        })
        
    except Exception as e:
        logger.error(f"Erro ao testar conexões: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@messaging_bp.route('/send-whatsapp', methods=['POST'])
@security.require_auth
@security.require_role('operator')
@security.rate_limit('api')
def send_whatsapp():
    """Envia mensagem individual via WhatsApp"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        validation_rules = {
            'phone': {'required': True, 'type': 'phone'},
            'message': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 4096}
        }
        
        validation = security.validate_input(data, validation_rules)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'errors': validation['errors']
            }), 400
        
        # Sanitiza entrada
        phone = security.sanitize_input(data['phone'])
        message = security.sanitize_input(data['message'])
        
        # Envia mensagem
        result = whatsapp_service.send_text_message(phone, message)
        
        # Log de auditoria
        AuditLog.create_log(
            user_id=g.current_user['user_id'],
            action='SEND_WHATSAPP',
            resource='WhatsApp Message',
            description=f"Mensagem enviada para {phone}: {'Sucesso' if result['success'] else 'Falha'}",
            ip_address=security.get_client_ip(),
            success=result['success']
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao enviar WhatsApp: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@messaging_bp.route('/send-email', methods=['POST'])
@security.require_auth
@security.require_role('operator')
@security.rate_limit('api')
def send_email():
    """Envia email individual"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        validation_rules = {
            'email': {'required': True, 'type': 'email'},
            'subject': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 255},
            'content': {'required': True, 'type': 'string', 'min_length': 1}
        }
        
        validation = security.validate_input(data, validation_rules)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'errors': validation['errors']
            }), 400
        
        # Sanitiza entrada
        email = security.sanitize_input(data['email'])
        subject = security.sanitize_input(data['subject'])
        content = data['content']  # HTML pode conter tags válidas
        name = security.sanitize_input(data.get('name', ''))
        
        # Envia email
        result = email_service.send_email(
            to_email=email,
            subject=subject,
            html_content=content,
            to_name=name
        )
        
        # Log de auditoria
        AuditLog.create_log(
            user_id=g.current_user['user_id'],
            action='SEND_EMAIL',
            resource='Email Message',
            description=f"Email enviado para {email}: {'Sucesso' if result['success'] else 'Falha'}",
            ip_address=security.get_client_ip(),
            success=result['success']
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@messaging_bp.route('/send-bulk-whatsapp', methods=['POST'])
@security.require_auth
@security.require_role('supervisor')
@security.rate_limit('bulk_send')
def send_bulk_whatsapp():
    """Envia mensagens em massa via WhatsApp"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        validation_rules = {
            'recipients': {'required': True, 'type': 'list'},
            'template': {'required': True, 'type': 'string', 'min_length': 1},
            'campaign_name': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 255}
        }
        
        # Validação básica
        if not isinstance(data.get('recipients'), list) or len(data.get('recipients', [])) == 0:
            return jsonify({
                'success': False,
                'error': 'Lista de destinatários é obrigatória e não pode estar vazia'
            }), 400
        
        if len(data.get('recipients', [])) > 1000:
            return jsonify({
                'success': False,
                'error': 'Máximo de 1000 destinatários por envio'
            }), 400
        
        # Cria campanha
        campaign = Campaign(
            name=security.sanitize_input(data['campaign_name']),
            type='whatsapp',
            status='running',
            total_recipients=len(data['recipients']),
            created_by=g.current_user['user_id']
        )
        db.session.add(campaign)
        db.session.commit()
        
        # Envia mensagens
        template = data['template']
        delay = data.get('delay', 2)  # Delay padrão de 2 segundos
        
        results = whatsapp_service.send_bulk_messages(
            recipients=data['recipients'],
            template=template,
            delay=delay
        )
        
        # Atualiza estatísticas da campanha
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        campaign.sent = len(results)
        campaign.delivered = successful  # Assumindo que enviado = entregue para WhatsApp
        campaign.failed = failed
        campaign.status = 'completed'
        campaign.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Salva detalhes das mensagens
        for result in results:
            message = CampaignMessage(
                campaign_id=campaign.id,
                recipient_phone=result['recipient'].get('phone'),
                recipient_email=result['recipient'].get('email'),
                status='sent' if result['success'] else 'failed',
                message_id=result.get('message_id'),
                error_message=result.get('error')
            )
            db.session.add(message)
        
        db.session.commit()
        
        # Log de auditoria
        AuditLog.create_log(
            user_id=g.current_user['user_id'],
            action='SEND_BULK_WHATSAPP',
            resource='WhatsApp Campaign',
            description=f"Campanha '{campaign.name}': {successful} enviadas, {failed} falharam",
            ip_address=security.get_client_ip()
        )
        
        return jsonify({
            'success': True,
            'campaign_id': campaign.id,
            'total_sent': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Erro no envio em massa WhatsApp: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@messaging_bp.route('/send-bulk-email', methods=['POST'])
@security.require_auth
@security.require_role('supervisor')
@security.rate_limit('bulk_send')
def send_bulk_email():
    """Envia emails em massa"""
    try:
        data = request.get_json()
        
        # Validação básica
        if not isinstance(data.get('recipients'), list) or len(data.get('recipients', [])) == 0:
            return jsonify({
                'success': False,
                'error': 'Lista de destinatários é obrigatória e não pode estar vazia'
            }), 400
        
        if len(data.get('recipients', [])) > 1000:
            return jsonify({
                'success': False,
                'error': 'Máximo de 1000 destinatários por envio'
            }), 400
        
        # Cria campanha
        campaign = Campaign(
            name=security.sanitize_input(data['campaign_name']),
            type='email',
            status='running',
            total_recipients=len(data['recipients']),
            created_by=g.current_user['user_id']
        )
        db.session.add(campaign)
        db.session.commit()
        
        # Envia emails
        subject_template = data['subject_template']
        html_template = data['html_template']
        text_template = data.get('text_template')
        delay = data.get('delay', 1)  # Delay padrão de 1 segundo
        
        results = email_service.send_bulk_emails(
            recipients=data['recipients'],
            subject_template=subject_template,
            html_template=html_template,
            text_template=text_template,
            delay=delay
        )
        
        # Atualiza estatísticas da campanha
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        campaign.sent = len(results)
        campaign.delivered = successful  # Assumindo que enviado = entregue para email
        campaign.failed = failed
        campaign.status = 'completed'
        campaign.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Salva detalhes das mensagens
        for result in results:
            message = CampaignMessage(
                campaign_id=campaign.id,
                recipient_phone=result['recipient'].get('phone'),
                recipient_email=result['recipient'].get('email'),
                status='sent' if result['success'] else 'failed',
                message_id=result.get('message_id'),
                error_message=result.get('error')
            )
            db.session.add(message)
        
        db.session.commit()
        
        # Log de auditoria
        AuditLog.create_log(
            user_id=g.current_user['user_id'],
            action='SEND_BULK_EMAIL',
            resource='Email Campaign',
            description=f"Campanha '{campaign.name}': {successful} enviados, {failed} falharam",
            ip_address=security.get_client_ip()
        )
        
        return jsonify({
            'success': True,
            'campaign_id': campaign.id,
            'total_sent': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Erro no envio em massa de email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@messaging_bp.route('/validate-phone', methods=['POST'])
@security.require_auth
@security.rate_limit('api')
def validate_phone():
    """Valida número de telefone no WhatsApp"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return jsonify({
                'success': False,
                'error': 'Número de telefone é obrigatório'
            }), 400
        
        is_valid = whatsapp_service.validate_phone_number(phone)
        
        return jsonify({
            'success': True,
            'phone': phone,
            'is_valid': is_valid
        })
        
    except Exception as e:
        logger.error(f"Erro ao validar telefone: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@messaging_bp.route('/validate-email', methods=['POST'])
@security.require_auth
@security.rate_limit('api')
def validate_email():
    """Valida formato de email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email é obrigatório'
            }), 400
        
        is_valid = email_service.validate_email(email)
        
        return jsonify({
            'success': True,
            'email': email,
            'is_valid': is_valid
        })
        
    except Exception as e:
        logger.error(f"Erro ao validar email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

