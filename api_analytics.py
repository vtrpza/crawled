"""
Analytics and advanced endpoints for Crawl4AI Enhanced API
Provides detailed analytics, batch operations, and advanced result management
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from uuid import UUID
from typing import Dict, Any, List, Optional
import traceback

from database.models import db, CrawlResult, CrawlSession, SiteAnalytics, CrawlMode, CrawlStatus
from database.service import DatabaseService

# Create Blueprint for analytics endpoints
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/overview', methods=['GET'])
def get_analytics_overview():
    """Get comprehensive analytics overview"""
    try:
        # Time range
        days = int(request.args.get('days', 7))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Overall statistics
        overall_stats = db.session.query(
            db.func.count(CrawlResult.id).label('total_crawls'),
            db.func.count(CrawlResult.id).filter(CrawlResult.status == CrawlStatus.COMPLETED.value).label('successful'),
            db.func.count(CrawlResult.id).filter(CrawlResult.status == CrawlStatus.FAILED.value).label('failed'),
            db.func.count(CrawlResult.id).filter(CrawlResult.status == CrawlStatus.IN_PROGRESS.value).label('in_progress'),
            db.func.avg(CrawlResult.response_time_ms).filter(CrawlResult.status == CrawlStatus.COMPLETED.value).label('avg_response_time'),
            db.func.sum(CrawlResult.content_length).label('total_content_processed')
        ).filter(CrawlResult.requested_at >= start_date).first()
        
        # Mode distribution
        mode_stats = db.session.query(
            CrawlResult.mode,
            db.func.count(CrawlResult.id).label('count'),
            db.func.count(CrawlResult.id).filter(CrawlResult.status == CrawlStatus.COMPLETED.value).label('successful')
        ).filter(CrawlResult.requested_at >= start_date).group_by(CrawlResult.mode).all()
        
        # Daily activity
        daily_stats = db.session.query(
            db.func.date(CrawlResult.requested_at).label('date'),
            db.func.count(CrawlResult.id).label('crawls'),
            db.func.count(CrawlResult.id).filter(CrawlResult.status == CrawlStatus.COMPLETED.value).label('successful')
        ).filter(CrawlResult.requested_at >= start_date)\
         .group_by(db.func.date(CrawlResult.requested_at))\
         .order_by(db.func.date(CrawlResult.requested_at)).all()
        
        # Top domains
        domain_stats = db.session.query(
            SiteAnalytics.domain,
            SiteAnalytics.total_pages_crawled,
            SiteAnalytics.successful_crawls,
            SiteAnalytics.avg_response_time_ms
        ).order_by(SiteAnalytics.total_pages_crawled.desc()).limit(10).all()
        
        return jsonify({
            'status': 'success',
            'period': f'Last {days} days',
            'overview': {
                'total_crawls': overall_stats.total_crawls or 0,
                'successful_crawls': overall_stats.successful or 0,
                'failed_crawls': overall_stats.failed or 0,
                'in_progress_crawls': overall_stats.in_progress or 0,
                'success_rate': (overall_stats.successful / overall_stats.total_crawls * 100) if overall_stats.total_crawls else 0,
                'avg_response_time_ms': float(overall_stats.avg_response_time) if overall_stats.avg_response_time else None,
                'total_content_mb': (overall_stats.total_content_processed / 1024 / 1024) if overall_stats.total_content_processed else 0
            },
            'mode_distribution': [
                {
                    'mode': stat.mode.value,
                    'total': stat.count,
                    'successful': stat.successful,
                    'success_rate': (stat.successful / stat.count * 100) if stat.count else 0
                }
                for stat in mode_stats
            ],
            'daily_activity': [
                {
                    'date': stat.date.isoformat(),
                    'crawls': stat.crawls,
                    'successful': stat.successful,
                    'success_rate': (stat.successful / stat.crawls * 100) if stat.crawls else 0
                }
                for stat in daily_stats
            ],
            'top_domains': [
                {
                    'domain': stat.domain,
                    'total_crawls': stat.total_pages_crawled,
                    'successful_crawls': stat.successful_crawls,
                    'avg_response_time_ms': float(stat.avg_response_time_ms) if stat.avg_response_time_ms else None
                }
                for stat in domain_stats
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Analytics overview error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/domains', methods=['GET'])
def get_domain_analytics():
    """Get detailed domain analytics"""
    try:
        domain = request.args.get('domain')
        limit = min(50, max(1, int(request.args.get('limit', 20))))
        
        if domain:
            # Specific domain analytics
            analytics = DatabaseService.get_domain_analytics(domain)
            if not analytics:
                return jsonify({
                    'status': 'error',
                    'error': 'Domain not found'
                }), 404
            
            # Recent crawls for this domain
            recent_crawls = db.session.query(CrawlResult)\
                .filter(CrawlResult.url.like(f'%{domain}%'))\
                .order_by(CrawlResult.requested_at.desc())\
                .limit(10).all()
            
            return jsonify({
                'status': 'success',
                'domain': domain,
                'analytics': analytics.to_dict(),
                'recent_crawls': [crawl.to_dict(include_content=False) for crawl in recent_crawls],
                'timestamp': datetime.now().isoformat()
            })
        else:
            # All domains overview
            domains = DatabaseService.get_top_domains(limit=limit)
            
            return jsonify({
                'status': 'success',
                'domains': [domain.to_dict() for domain in domains],
                'count': len(domains),
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        current_app.logger.error(f"Domain analytics error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/performance', methods=['GET'])
def get_performance_metrics():
    """Get performance metrics and trends"""
    try:
        days = int(request.args.get('days', 7))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Response time trends
        response_time_trends = db.session.query(
            db.func.date(CrawlResult.requested_at).label('date'),
            db.func.avg(CrawlResult.response_time_ms).label('avg_response_time'),
            db.func.min(CrawlResult.response_time_ms).label('min_response_time'),
            db.func.max(CrawlResult.response_time_ms).label('max_response_time')
        ).filter(
            CrawlResult.requested_at >= start_date,
            CrawlResult.status == CrawlStatus.COMPLETED.value,
            CrawlResult.response_time_ms.isnot(None)
        ).group_by(db.func.date(CrawlResult.requested_at))\
         .order_by(db.func.date(CrawlResult.requested_at)).all()
        
        # Content size trends
        content_size_trends = db.session.query(
            db.func.date(CrawlResult.requested_at).label('date'),
            db.func.avg(CrawlResult.content_length).label('avg_content_length'),
            db.func.sum(CrawlResult.content_length).label('total_content_length')
        ).filter(
            CrawlResult.requested_at >= start_date,
            CrawlResult.status == CrawlStatus.COMPLETED.value,
            CrawlResult.content_length.isnot(None)
        ).group_by(db.func.date(CrawlResult.requested_at))\
         .order_by(db.func.date(CrawlResult.requested_at)).all()
        
        # Error analysis
        error_analysis = db.session.query(
            db.func.substr(CrawlResult.error_message, 1, 50).label('error_type'),
            db.func.count(CrawlResult.id).label('count')
        ).filter(
            CrawlResult.requested_at >= start_date,
            CrawlResult.status == CrawlStatus.FAILED.value,
            CrawlResult.error_message.isnot(None)
        ).group_by(db.func.substr(CrawlResult.error_message, 1, 50))\
         .order_by(db.func.count(CrawlResult.id).desc()).limit(10).all()
        
        return jsonify({
            'status': 'success',
            'period': f'Last {days} days',
            'response_time_trends': [
                {
                    'date': trend.date.isoformat(),
                    'avg_response_time_ms': float(trend.avg_response_time) if trend.avg_response_time else None,
                    'min_response_time_ms': float(trend.min_response_time) if trend.min_response_time else None,
                    'max_response_time_ms': float(trend.max_response_time) if trend.max_response_time else None
                }
                for trend in response_time_trends
            ],
            'content_size_trends': [
                {
                    'date': trend.date.isoformat(),
                    'avg_content_length': int(trend.avg_content_length) if trend.avg_content_length else None,
                    'total_content_mb': (trend.total_content_length / 1024 / 1024) if trend.total_content_length else None
                }
                for trend in content_size_trends
            ],
            'error_analysis': [
                {
                    'error_type': error.error_type,
                    'count': error.count,
                    'percentage': 0  # Will be calculated on frontend
                }
                for error in error_analysis
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Performance metrics error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/export', methods=['GET'])
def export_results():
    """Export crawl results in various formats"""
    try:
        format_type = request.args.get('format', 'json').lower()
        days = int(request.args.get('days', 7))
        limit = min(1000, max(1, int(request.args.get('limit', 100))))
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get results
        results = db.session.query(CrawlResult)\
            .filter(CrawlResult.requested_at >= start_date)\
            .order_by(CrawlResult.requested_at.desc())\
            .limit(limit).all()
        
        if format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'id', 'url', 'mode', 'status', 'title', 'requested_at', 'completed_at',
                'response_time_ms', 'content_length', 'domain', 'error_message'
            ])
            
            # Data
            for result in results:
                writer.writerow([
                    str(result.id), result.url, result.mode.value if result.mode else '',
                    result.status.value if result.status else '', result.title or '',
                    result.requested_at.isoformat() if result.requested_at else '',
                    result.completed_at.isoformat() if result.completed_at else '',
                    result.response_time_ms or '', result.content_length or '',
                    result.domain or '', result.error_message or ''
                ])
            
            csv_data = output.getvalue()
            output.close()
            
            return csv_data, 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=crawl_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        
        else:
            # JSON format (default)
            results_data = [result.to_dict(include_content=False) for result in results]
            
            return jsonify({
                'status': 'success',
                'format': 'json',
                'period': f'Last {days} days',
                'count': len(results_data),
                'results': results_data,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        current_app.logger.error(f"Export error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/cleanup', methods=['POST'])
def cleanup_old_data():
    """Clean up old crawl results"""
    try:
        days = int(request.json.get('days', 30)) if request.json else 30
        
        if days < 7:
            return jsonify({
                'status': 'error',
                'error': 'Cannot delete data newer than 7 days'
            }), 400
        
        deleted_count = DatabaseService.cleanup_old_results(days=days)
        
        return jsonify({
            'status': 'success',
            'deleted_count': deleted_count,
            'days': days,
            'message': f'Cleaned up {deleted_count} results older than {days} days',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Cleanup error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500