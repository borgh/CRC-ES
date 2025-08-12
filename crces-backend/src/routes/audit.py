from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_, desc
from datetime import datetime, timedelta

from src.models.user import User
from src.models.audit import db, AuditLog, SystemHealth

audit_bp = Blueprint('audit', __name__)

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

@audit_bp.route('/logs', methods=['GET'])
@jwt_required()
@require_permission('view_audit_logs')
def get_audit_logs():
    """Lista logs de auditoria com filtros avançados"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Filtros
        user_filter = request.args.get('user', '')
        action_filter = request.args.get('action', '')
        resource_filter = request.args.get('resource', '')
        success_filter = request.args.get('success', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Limita per_page para evitar sobrecarga
        per_page = min(per_page, 200)
        
        # Query base
        query = AuditLog.query
        
        # Filtro por usuário
        if user_filter:
            query = query.filter(
                or_(
                    AuditLog.username.ilike(f'%{user_filter}%'),
                    AuditLog.user_id == user_filter if user_filter.isdigit() else False
                )
            )
        
        # Filtro por ação
        if action_filter:
            query = query.filter(AuditLog.action_type.ilike(f'%{action_filter}%'))
        
        # Filtro por recurso
        if resource_filter:
            query = query.filter(AuditLog.resource_type.ilike(f'%{resource_filter}%'))
        
        # Filtro por sucesso
        if success_filter:
            is_success = success_filter.lower() == 'true'
            query = query.filter(AuditLog.success == is_success)
        
        # Filtro por data
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(AuditLog.created_at >= date_from_obj)
            except ValueError:
                return jsonify({'message': 'Formato de data_from inválido'}), 400
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(AuditLog.created_at <= date_to_obj)
            except ValueError:
                return jsonify({'message': 'Formato de data_to inválido'}), 400
        
        # Ordena por data de criação (mais recentes primeiro)
        query = query.order_by(desc(AuditLog.created_at))
        
        # Paginação
        logs = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
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
        current_app.logger.error(f"Erro ao listar logs de auditoria: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@audit_bp.route('/logs/<int:log_id>', methods=['GET'])
@jwt_required()
@require_permission('view_audit_logs')
def get_audit_log(log_id):
    """Obtém um log de auditoria específico"""
    try:
        log = AuditLog.query.get(log_id)
        
        if not log:
            return jsonify({'message': 'Log não encontrado'}), 404
        
        return jsonify({
            'log': log.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter log de auditoria: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@audit_bp.route('/logs/summary', methods=['GET'])
@jwt_required()
@require_permission('view_audit_logs')
def get_audit_summary():
    """Obtém resumo dos logs de auditoria"""
    try:
        # Período para análise (últimos 30 dias por padrão)
        days = request.args.get('days', 30, type=int)
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Estatísticas gerais
        total_logs = AuditLog.query.filter(AuditLog.created_at >= date_from).count()
        successful_actions = AuditLog.query.filter(
            and_(AuditLog.created_at >= date_from, AuditLog.success == True)
        ).count()
        failed_actions = AuditLog.query.filter(
            and_(AuditLog.created_at >= date_from, AuditLog.success == False)
        ).count()
        
        # Top usuários mais ativos
        top_users = db.session.query(
            AuditLog.username,
            db.func.count(AuditLog.id).label('action_count')
        ).filter(
            AuditLog.created_at >= date_from
        ).group_by(
            AuditLog.username
        ).order_by(
            desc('action_count')
        ).limit(10).all()
        
        # Top ações mais realizadas
        top_actions = db.session.query(
            AuditLog.action_type,
            db.func.count(AuditLog.id).label('action_count')
        ).filter(
            AuditLog.created_at >= date_from
        ).group_by(
            AuditLog.action_type
        ).order_by(
            desc('action_count')
        ).limit(10).all()
        
        # Top recursos mais acessados
        top_resources = db.session.query(
            AuditLog.resource_type,
            db.func.count(AuditLog.id).label('access_count')
        ).filter(
            AuditLog.created_at >= date_from
        ).group_by(
            AuditLog.resource_type
        ).order_by(
            desc('access_count')
        ).limit(10).all()
        
        # Atividade por dia (últimos 7 dias)
        daily_activity = []
        for i in range(7):
            day_start = (datetime.utcnow() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_count = AuditLog.query.filter(
                and_(
                    AuditLog.created_at >= day_start,
                    AuditLog.created_at < day_end
                )
            ).count()
            
            daily_activity.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': day_count
            })
        
        daily_activity.reverse()  # Ordem cronológica
        
        return jsonify({
            'summary': {
                'period_days': days,
                'total_logs': total_logs,
                'successful_actions': successful_actions,
                'failed_actions': failed_actions,
                'success_rate': round((successful_actions / total_logs * 100) if total_logs > 0 else 0, 2)
            },
            'top_users': [{'username': user[0], 'action_count': user[1]} for user in top_users],
            'top_actions': [{'action_type': action[0], 'count': action[1]} for action in top_actions],
            'top_resources': [{'resource_type': resource[0], 'count': resource[1]} for resource in top_resources],
            'daily_activity': daily_activity
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter resumo de auditoria: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@audit_bp.route('/health', methods=['GET'])
@jwt_required()
@require_permission('view_dashboard')
def get_system_health():
    """Obtém métricas de saúde do sistema"""
    try:
        # Obtém as métricas mais recentes
        latest_health = SystemHealth.query.order_by(desc(SystemHealth.created_at)).first()
        
        # Obtém histórico das últimas 24 horas
        date_from = datetime.utcnow() - timedelta(hours=24)
        health_history = SystemHealth.query.filter(
            SystemHealth.created_at >= date_from
        ).order_by(SystemHealth.created_at).all()
        
        # Estatísticas dos últimos 7 dias
        date_from_week = datetime.utcnow() - timedelta(days=7)
        
        # Contagem de logs de erro nas últimas 24h
        error_logs_24h = AuditLog.query.filter(
            and_(
                AuditLog.created_at >= date_from,
                AuditLog.success == False
            )
        ).count()
        
        # Contagem de logins nas últimas 24h
        logins_24h = AuditLog.query.filter(
            and_(
                AuditLog.created_at >= date_from,
                AuditLog.action_type == 'LOGIN_SUCCESS'
            )
        ).count()
        
        # Usuários únicos ativos nas últimas 24h
        active_users_24h = db.session.query(AuditLog.user_id).filter(
            and_(
                AuditLog.created_at >= date_from,
                AuditLog.user_id.isnot(None)
            )
        ).distinct().count()
        
        return jsonify({
            'current_health': latest_health.to_dict() if latest_health else None,
            'history_24h': [health.to_dict() for health in health_history],
            'statistics': {
                'error_logs_24h': error_logs_24h,
                'logins_24h': logins_24h,
                'active_users_24h': active_users_24h
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter saúde do sistema: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@audit_bp.route('/health', methods=['POST'])
@jwt_required()
@require_permission('system_admin')
def record_system_health():
    """Registra métricas de saúde do sistema"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        # Registra métricas
        health = SystemHealth.record_metrics(
            cpu_usage=data.get('cpu_usage'),
            memory_usage=data.get('memory_usage'),
            disk_usage=data.get('disk_usage'),
            db_connections=data.get('db_connections'),
            db_response_time=data.get('db_response_time'),
            api_response_time=data.get('api_response_time'),
            api_error_rate=data.get('api_error_rate'),
            emails_in_queue=data.get('emails_in_queue', 0),
            whatsapp_in_queue=data.get('whatsapp_in_queue', 0),
            failed_sends_last_hour=data.get('failed_sends_last_hour', 0),
            overall_status=data.get('overall_status', 'healthy')
        )
        
        return jsonify({
            'message': 'Métricas de saúde registradas com sucesso',
            'health': health.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao registrar métricas de saúde: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@audit_bp.route('/logs/export', methods=['POST'])
@jwt_required()
@require_permission('view_audit_logs')
def export_audit_logs():
    """Exporta logs de auditoria em formato CSV"""
    try:
        data = request.get_json() or {}
        
        # Filtros similares ao get_audit_logs
        user_filter = data.get('user', '')
        action_filter = data.get('action', '')
        resource_filter = data.get('resource', '')
        success_filter = data.get('success', '')
        date_from = data.get('date_from', '')
        date_to = data.get('date_to', '')
        
        # Query base
        query = AuditLog.query
        
        # Aplica filtros
        if user_filter:
            query = query.filter(
                or_(
                    AuditLog.username.ilike(f'%{user_filter}%'),
                    AuditLog.user_id == user_filter if user_filter.isdigit() else False
                )
            )
        
        if action_filter:
            query = query.filter(AuditLog.action_type.ilike(f'%{action_filter}%'))
        
        if resource_filter:
            query = query.filter(AuditLog.resource_type.ilike(f'%{resource_filter}%'))
        
        if success_filter:
            is_success = success_filter.lower() == 'true'
            query = query.filter(AuditLog.success == is_success)
        
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(AuditLog.created_at >= date_from_obj)
            except ValueError:
                return jsonify({'message': 'Formato de data_from inválido'}), 400
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(AuditLog.created_at <= date_to_obj)
            except ValueError:
                return jsonify({'message': 'Formato de data_to inválido'}), 400
        
        # Limita a 10000 registros para evitar sobrecarga
        logs = query.order_by(desc(AuditLog.created_at)).limit(10000).all()
        
        # Converte para formato de exportação
        export_data = []
        for log in logs:
            export_data.append({
                'id': log.id,
                'timestamp': log.created_at.isoformat(),
                'user': log.username or f"ID:{log.user_id}",
                'action': log.action_type,
                'resource': log.resource_type,
                'resource_id': log.resource_id,
                'success': log.success,
                'ip_address': log.ip_address,
                'error_message': log.error_message
            })
        
        return jsonify({
            'message': f'{len(export_data)} logs exportados com sucesso',
            'data': export_data,
            'total_records': len(export_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao exportar logs de auditoria: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

