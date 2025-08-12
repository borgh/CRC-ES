"""
Rotas de auditoria do sistema CRC-ES
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import AuditLog, User, db
from datetime import datetime, timedelta

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Obter logs de auditoria"""
    try:
        # Parâmetros de filtro
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action_filter = request.args.get('action')
        user_filter = request.args.get('user_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Query base
        query = AuditLog.query
        
        # Aplicar filtros
        if action_filter:
            query = query.filter(AuditLog.action.like(f'%{action_filter}%'))
        
        if user_filter:
            query = query.filter_by(user_id=user_filter)
        
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.timestamp >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(AuditLog.timestamp < date_to_obj)
        
        # Ordenar e paginar
        logs = query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Enriquecer com dados do usuário
        logs_data = []
        for log in logs.items:
            log_dict = log.to_dict()
            if log.user_id:
                user = User.query.get(log.user_id)
                log_dict['username'] = user.username if user else 'Usuário removido'
            logs_data.append(log_dict)
        
        return jsonify({
            'logs': logs_data,
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

@audit_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_audit_stats():
    """Obter estatísticas de auditoria"""
    try:
        # Período para estatísticas (últimos 30 dias)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Ações mais comuns
        common_actions = db.session.query(
            AuditLog.action,
            db.func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= thirty_days_ago
        ).group_by(AuditLog.action).order_by(
            db.func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        # Usuários mais ativos
        active_users = db.session.query(
            User.username,
            db.func.count(AuditLog.id).label('count')
        ).join(
            AuditLog, User.id == AuditLog.user_id
        ).filter(
            AuditLog.timestamp >= thirty_days_ago
        ).group_by(User.username).order_by(
            db.func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        # Atividade por dia (últimos 7 dias)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_activity = db.session.query(
            db.func.date(AuditLog.timestamp).label('date'),
            db.func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= seven_days_ago
        ).group_by(
            db.func.date(AuditLog.timestamp)
        ).order_by(
            db.func.date(AuditLog.timestamp)
        ).all()
        
        # Total de logs
        total_logs = AuditLog.query.count()
        recent_logs = AuditLog.query.filter(AuditLog.timestamp >= thirty_days_ago).count()
        
        return jsonify({
            'stats': {
                'total_logs': total_logs,
                'recent_logs': recent_logs,
                'common_actions': [{'action': action, 'count': count} for action, count in common_actions],
                'active_users': [{'username': username, 'count': count} for username, count in active_users],
                'daily_activity': [{'date': str(date), 'count': count} for date, count in daily_activity]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@audit_bp.route('/actions', methods=['GET'])
@jwt_required()
def get_audit_actions():
    """Obter lista de ações disponíveis para filtro"""
    try:
        actions = db.session.query(AuditLog.action).distinct().all()
        action_list = [action[0] for action in actions]
        
        return jsonify({'actions': sorted(action_list)}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@audit_bp.route('/export', methods=['POST'])
@jwt_required()
def export_audit_logs():
    """Exportar logs de auditoria"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Filtros para exportação
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        action_filter = data.get('action')
        
        # Query base
        query = AuditLog.query
        
        # Aplicar filtros
        if action_filter:
            query = query.filter(AuditLog.action.like(f'%{action_filter}%'))
        
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.timestamp >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(AuditLog.timestamp < date_to_obj)
        
        # Limitar exportação a 10000 registros
        logs = query.order_by(AuditLog.timestamp.desc()).limit(10000).all()
        
        # Preparar dados para exportação
        export_data = []
        for log in logs:
            log_dict = log.to_dict()
            if log.user_id:
                user = User.query.get(log.user_id)
                log_dict['username'] = user.username if user else 'Usuário removido'
            export_data.append(log_dict)
        
        # Log da exportação
        audit_log = AuditLog(
            user_id=user_id,
            action='audit_export',
            details=f'Exportação de {len(export_data)} logs de auditoria',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Logs exportados com sucesso',
            'count': len(export_data),
            'data': export_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

