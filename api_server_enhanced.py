#!/usr/bin/env python3
"""
Enhanced Flask API server for Crawl4AI with Database Integration
Provides REST endpoints with persistent storage and improved result management
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from uuid import UUID, uuid4
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import traceback
import threading
from typing import Optional, Dict, Any, List

# Import our existing POC, enterprise engine, stealth engine, and validation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from crawl4ai_poc import Crawl4AIPOCTool
from crawl4ai_enterprise import EnterpriseWebCrawler, CrawlRequest, IntentType
from crawl4ai_stealth_definitive import Crawl4AIStealthEngine, StealthResult
from api_validation import (
    api_endpoint, validate_url, validate_urls_array, validate_query,
    validate_stealth_level, validate_concurrent, validate_max_urls,
    validate_action, sanitize_options, ValidationError
)

# Import database components
from database.config import init_database
from database.models import db, CrawlSession, CrawlResult, CrawlMode, CrawlStatus
from database.service import DatabaseService

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize database
database = init_database(app)

# Initialize our POC instance, enterprise crawler, and definitive stealth engine
poc = Crawl4AIPOCTool()
enterprise_crawler = EnterpriseWebCrawler()
stealth_engine = Crawl4AIStealthEngine()

def run_async(coro):
    """Helper to run async functions in Flask"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def get_crawl_mode(mode_str: str) -> CrawlMode:
    """Convert string to CrawlMode enum"""
    mode_map = {
        'simple': CrawlMode.SIMPLE,
        'advanced': CrawlMode.ADVANCED,
        'extract': CrawlMode.EXTRACT,
        'batch': CrawlMode.BATCH,
        'media': CrawlMode.MEDIA,
        'interactive': CrawlMode.INTERACTIVE,
        'ai': CrawlMode.AI,
        'stealth': CrawlMode.STEALTH,
        'smart': CrawlMode.SMART,
        'intelligent': CrawlMode.SMART  # Map intelligent to smart mode
    }
    return mode_map.get(mode_str.lower(), CrawlMode.SIMPLE)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint with database status"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1')).fetchone()
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'crawl4ai-enhanced-api',
        'database': db_status,
        'version': '2.0.0'
    })

@app.route('/api/smart-crawl', methods=['POST'])
@api_endpoint(required_fields=['url'])
def smart_crawl():
    """Smart crawl endpoint with database persistence"""
    data = request.get_json()
    
    # Validate and sanitize inputs
    url = validate_url(data.get('url'))
    stealth_level = validate_stealth_level(data.get('stealth_level', 4))
    custom_user_agent = data.get('user_agent')
    intent = data.get('intent', 'general')
    extraction_query = data.get('extraction_query', '')
    
    # Deep crawl parameters
    max_pages = min(int(data.get('max_pages', 5)), 20)
    max_depth = min(int(data.get('max_depth', 2)), 5)
    crawl_strategy = data.get('strategy', 'bfs').lower()
    
    # AI extraction configuration
    ai_extraction = data.get('ai_extraction', {})
    if not ai_extraction:
        ai_extraction = {'model': 'groq', 'enabled': True}
    
    # Debug: Show what we received
    print(f"🔍 Debug AI extraction config: {ai_extraction}")
    print(f"🔑 API key present: {'***' if ai_extraction.get('api_key') else 'None'}")
    
    print(f"🤖 AI-First Deep Crawl - AI extraction MANDATORY")
    print(f"📝 Extraction query: '{extraction_query}'")
    print(f"🔄 Strategy: {crawl_strategy.upper()}, Pages: {max_pages}, Depth: {max_depth}")
    
    # Create database record
    crawl_result = DatabaseService.create_crawl_result(
        url=url,
        mode=CrawlMode.SMART,
        stealth_level=stealth_level,
        custom_user_agent=custom_user_agent,
        extraction_query=extraction_query,
        custom_config={
            'intent': intent,
            'max_pages': max_pages,
            'max_depth': max_depth,
            'strategy': crawl_strategy,
            'ai_extraction': ai_extraction
        }
    )
    
    try:
        # Update status to in_progress
        DatabaseService.update_crawl_result(crawl_result.id, {}, CrawlStatus.IN_PROGRESS)
        
        # Map frontend model names to provider strings
        model = ai_extraction.get('model', 'groq')
        provider_map = {
            'ollama': 'ollama/llama3.2',
            'gpt-4': 'openai/gpt-4o',
            'claude-3': 'anthropic/claude-3-5-sonnet',
            'gemini-pro': 'gemini/gemini-1.5-pro',
            'groq': 'groq/llama-3.3-70b-versatile'
        }
        provider = provider_map.get(model, 'groq/llama-3.3-70b-versatile')
        
        # Perform the crawl
        async def _ai_deep_crawl():
            return await poc.ai_enhanced_deep_crawl(
                url=url,
                extraction_instruction=extraction_query or f"Extract and analyze key information from this website about {intent}. Provide comprehensive insights and actionable information.",
                max_pages=max_pages,
                max_depth=max_depth,
                strategy=crawl_strategy,
                provider=provider,
                api_token=ai_extraction.get('api_key')
            )
        
        result = run_async(_ai_deep_crawl())
        
        if result and result.get('status') == 'success':
            # Update database with successful result
            DatabaseService.update_crawl_result(
                crawl_result.id, 
                result, 
                CrawlStatus.COMPLETED
            )
            
            # Get updated result from database
            updated_result = DatabaseService.get_crawl_result(crawl_result.id)
            
            return jsonify({
                'status': 'success',
                'result_id': str(crawl_result.id),
                'crawl_type': result.get('crawl_type', 'ai_enhanced_deep_crawl'),
                'url': result.get('url', url),
                'timestamp': datetime.now().isoformat(),
                
                # AI-First Deep Crawl specific data
                'instruction': result.get('instruction', extraction_query),
                'strategy': result.get('strategy', crawl_strategy.upper()),
                'pages_crawled': result.get('pages_crawled', 0),
                'pages_requested': result.get('pages_requested', max_pages),
                'max_depth': result.get('max_depth', max_depth),
                'ai_provider': result.get('ai_provider', provider),
                
                # AI synthesis - the main result
                'ai_synthesis': result.get('ai_synthesis', ''),
                'ai_analysis': result.get('ai_synthesis', ''),
                'extracted_content': result.get('ai_synthesis', ''),
                
                # Individual page results
                'individual_pages': result.get('individual_pages', []),
                'total_content_length': result.get('total_content_length', 0),
                
                # Enhanced metadata
                'metadata': result.get('metadata', {}),
                'performance': {
                    'pages_crawled': result.get('pages_crawled', 0),
                    'ai_processing_mandatory': True,
                    'deep_crawl_enabled': True,
                    'synthesis_generated': result.get('metadata', {}).get('synthesis_generated', False),
                    'database_stored': True,
                    'result_id': str(crawl_result.id)
                },
                
                # Database metadata
                'database': {
                    'result_id': str(crawl_result.id),
                    'session_id': str(updated_result.session_id) if updated_result else None,
                    'stored_at': updated_result.completed_at.isoformat() if updated_result and updated_result.completed_at else None
                }
            })
        else:
            # Update database with failed result
            error_msg = result.get('error', 'AI-enhanced deep crawl failed') if result else 'Unknown error'
            DatabaseService.update_crawl_result(
                crawl_result.id,
                {'error': error_msg},
                CrawlStatus.FAILED
            )
            
            return jsonify({
                'status': 'error',
                'error': error_msg,
                'result_id': str(crawl_result.id),
                'crawl_type': result.get('crawl_type', 'ai_enhanced_deep_crawl_failed') if result else 'crawl_failed',
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'attempted_config': {
                    'max_pages': max_pages,
                    'max_depth': max_depth,
                    'strategy': crawl_strategy,
                    'ai_mandatory': True
                }
            }), 500
            
    except Exception as e:
        # Update database with error
        DatabaseService.update_crawl_result(
            crawl_result.id,
            {'error': str(e)},
            CrawlStatus.FAILED
        )
        
        print(f"Smart crawl error: {e}")
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'error': str(e),
            'result_id': str(crawl_result.id),
            'url': url,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/crawl', methods=['POST'])
def crawl():
    """Enhanced crawl endpoint with database persistence"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'No data provided'
            }), 400
            
        mode = data.get('mode', 'simple')
        url = data.get('url')
        
        if not url:
            return jsonify({
                'status': 'error',
                'error': 'URL is required'
            }), 400
        
        # Create database record
        crawl_result = DatabaseService.create_crawl_result(
            url=url,
            mode=get_crawl_mode(mode),
            stealth_level=data.get('stealth_level', 0),
            custom_user_agent=data.get('user_agent'),
            extraction_query=data.get('extraction_query') or data.get('query') or data.get('instruction'),
            custom_config=data
        )
        
        try:
            # Update status to in_progress
            DatabaseService.update_crawl_result(crawl_result.id, {}, CrawlStatus.IN_PROGRESS)
            
            # Route to appropriate POC method based on mode
            async def _crawl():
                result = None
                
                if mode == 'simple':
                    output_format = data.get('format', 'markdown')
                    stealth = data.get('stealth', False)
                    result = await poc.simple_crawl(url, output_format, stealth)
                    
                elif mode == 'advanced':
                    js_code = data.get('js', '')
                    wait_time = int(data.get('wait', 2))
                    stealth = data.get('stealth', False)
                    result = await poc.advanced_crawl_with_js(url, js_code, wait_time, stealth)
                    
                elif mode == 'extract':
                    query = data.get('query', '')
                    if not query:
                        raise ValueError('Query is required for extraction mode')
                    result = await poc.crawl_with_extraction(url, query)
                    
                elif mode == 'batch':
                    urls = data.get('urls', '').strip().split('\n')
                    urls = [u.strip() for u in urls if u.strip()]
                    concurrent = int(data.get('concurrent', 2))
                    if not urls:
                        raise ValueError('URLs are required for batch mode')
                    result = await poc.batch_crawl(urls, concurrent)
                    
                elif mode == 'media':
                    download_images = data.get('download_images', True)
                    download_videos = data.get('download_videos', False)
                    result = await poc.crawl_with_media_download(url, download_images, download_videos)
                    
                elif mode == 'interactive':
                    question = data.get('question', data.get('actions', 'Extract main content'))
                    result = await poc.interactive_crawl(url, question)
                    
                elif mode == 'ai':
                    instruction = data.get('extraction_query', data.get('instruction', ''))
                    if not instruction:
                        raise ValueError('Instruction is required for AI mode')
                    stealth = data.get('stealth', False)
                    result = await poc.ai_powered_crawl(url, instruction, provider=provider, api_token=ai_extraction.get('api_key'), use_stealth=stealth)
                    
                elif mode == 'stealth':
                    stealth_level = int(data.get('stealth_level', 5))
                    custom_user_agent = data.get('user_agent')
                    stealth_result = await stealth_engine.stealth_crawl(url, stealth_level, custom_user_agent)
                    result = {
                        'status': 'success' if stealth_result.success and stealth_result.detection_bypassed else 'error',
                        'url': stealth_result.url,
                        'content': stealth_result.content,
                        'stealth_features': stealth_result.stealth_config,
                        'detection_bypassed': stealth_result.detection_bypassed,
                        'response_time': stealth_result.response_time,
                        'error': stealth_result.error
                    }
                    
                elif mode in ['intelligent', 'smart']:
                    # Use AI-powered crawl for intelligent/smart mode
                    instruction = data.get('extraction_query', data.get('instruction', 'Extract main content and key information'))
                    stealth = data.get('stealth_level', 0) > 0
                    result = await poc.ai_powered_crawl(url, instruction, provider=provider, api_token=ai_extraction.get('api_key'), use_stealth=stealth)
                    
                else:
                    raise ValueError(f'Unknown mode: {mode}')
                    
                return result
                
            # Run the async operation
            result = run_async(_crawl())
            
            # Handle POC method results
            if result and isinstance(result, dict):
                if result.get('status') == 'success':
                    # Update database with successful result
                    DatabaseService.update_crawl_result(
                        crawl_result.id,
                        result,
                        CrawlStatus.COMPLETED
                    )
                    
                    # Get updated result from database for metadata
                    updated_result = DatabaseService.get_crawl_result(crawl_result.id)
                    
                    # POC methods return structured Dict results
                    response_data = {
                        'status': 'success',
                        'result_id': str(crawl_result.id),
                        'mode': mode,
                        'url': url,
                        'timestamp': datetime.now().isoformat(),
                        'content': result.get('content', ''),
                        'metadata': result.get('metadata', {}),
                        'stealth_features': result.get('stealth_features', []) if mode == 'stealth' or data.get('stealth') else None,
                        
                        # Database metadata
                        'database': {
                            'result_id': str(crawl_result.id),
                            'session_id': str(updated_result.session_id) if updated_result else None,
                            'stored_at': updated_result.completed_at.isoformat() if updated_result and updated_result.completed_at else None,
                            'content_length': updated_result.content_length if updated_result else None
                        }
                    }
                    
                    # Add mode-specific data
                    if 'extracted_content' in result:
                        response_data['extracted_content'] = result['extracted_content']
                        
                    if mode == 'batch' and 'batch_results' in result:
                        response_data['batch_results'] = result['batch_results']
                        
                    if 'media' in result:
                        response_data['media'] = result['media']
                        
                    if 'ai_analysis' in result:
                        response_data['ai_analysis'] = result['ai_analysis']
                        
                    return jsonify(response_data)
                
                else:
                    # Update database with failed result
                    error_msg = result.get('error', 'Unknown error occurred')
                    DatabaseService.update_crawl_result(
                        crawl_result.id,
                        {'error': error_msg},
                        CrawlStatus.FAILED
                    )
                    
                    return jsonify({
                        'status': 'error',
                        'error': error_msg,
                        'result_id': str(crawl_result.id),
                        'mode': mode,
                        'url': url,
                        'timestamp': datetime.now().isoformat()
                    }), 500
            
            else:
                # Handle unexpected result format
                error_msg = f'Unexpected result format: {type(result)}'
                DatabaseService.update_crawl_result(
                    crawl_result.id,
                    {'error': error_msg},
                    CrawlStatus.FAILED
                )
                
                return jsonify({
                    'status': 'error',
                    'error': error_msg,
                    'result_id': str(crawl_result.id),
                    'mode': mode,
                    'url': url,
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        except Exception as e:
            # Update database with error
            DatabaseService.update_crawl_result(
                crawl_result.id,
                {'error': str(e)},
                CrawlStatus.FAILED
            )
            raise e
            
    except Exception as e:
        print(f"API Error: {e}")
        print(f"Error type: {type(e)}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': f"{type(e).__name__}: {str(e)}",
            'timestamp': datetime.now().isoformat()
        }), 500

# New database-specific endpoints
@app.route('/api/results', methods=['GET'])
def get_results():
    """Get crawl results with pagination and filtering"""
    try:
        # Parse query parameters
        page = max(1, int(request.args.get('page', 1)))
        limit = min(100, max(1, int(request.args.get('limit', 20))))
        offset = (page - 1) * limit
        
        query = request.args.get('query')
        mode = request.args.get('mode')
        status = request.args.get('status')
        domain = request.args.get('domain')
        include_content = request.args.get('include_content', 'false').lower() == 'true'
        
        # Convert string parameters to enums
        crawl_mode = None
        if mode:
            try:
                crawl_mode = get_crawl_mode(mode)
            except:
                pass
        
        crawl_status = None
        if status:
            try:
                crawl_status = CrawlStatus(status.lower())
            except:
                pass
        
        # Search results
        results, total = DatabaseService.search_crawl_results(
            query=query,
            mode=crawl_mode,
            status=crawl_status,
            domain=domain,
            limit=limit,
            offset=offset,
            include_content=include_content
        )
        
        # Convert to dictionaries
        results_data = [result.to_dict(include_content=include_content) for result in results]
        
        return jsonify({
            'status': 'success',
            'results': results_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit,
                'has_next': offset + limit < total,
                'has_prev': page > 1
            },
            'filters': {
                'query': query,
                'mode': mode,
                'status': status,
                'domain': domain
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Get results error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/results/<result_id>', methods=['GET'])
def get_result(result_id):
    """Get specific crawl result by ID"""
    try:
        include_content = request.args.get('include_content', 'true').lower() == 'true'
        
        result = DatabaseService.get_crawl_result(UUID(result_id), include_content=include_content)
        if not result:
            return jsonify({
                'status': 'error',
                'error': 'Result not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'result': result.to_dict(include_content=include_content),
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError:
        return jsonify({
            'status': 'error',
            'error': 'Invalid result ID format'
        }), 400
    except Exception as e:
        print(f"Get result error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get crawl statistics and analytics"""
    try:
        stats = DatabaseService.get_crawl_statistics()
        
        return jsonify({
            'status': 'success',
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Get statistics error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/recent', methods=['GET'])
def get_recent():
    """Get recent crawl results"""
    try:
        limit = min(50, max(1, int(request.args.get('limit', 10))))
        include_content = request.args.get('include_content', 'false').lower() == 'true'
        
        results = DatabaseService.get_recent_crawls(limit=limit, include_content=include_content)
        results_data = [result.to_dict(include_content=include_content) for result in results]
        
        return jsonify({
            'status': 'success',
            'results': results_data,
            'count': len(results_data),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Get recent error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Keep existing endpoints
@app.route('/api/modes', methods=['GET'])
def get_modes():
    """Get available crawl modes and their configurations"""
    modes = {
        'simple': {
            'title': 'Simple Crawl',
            'description': 'Basic web scraping with markdown/HTML output',
            'fields': ['url', 'format', 'stealth']
        },
        'advanced': {
            'title': 'Advanced JS Crawl',
            'description': 'JavaScript execution and dynamic content handling',
            'fields': ['url', 'js', 'wait', 'stealth']
        },
        'extract': {
            'title': 'Content Extract',
            'description': 'Keyword-based content extraction and filtering',
            'fields': ['url', 'query', 'stealth']
        },
        'batch': {
            'title': 'Batch Crawl',
            'description': 'Multiple URLs with concurrent processing',
            'fields': ['urls', 'concurrent', 'stealth']
        },
        'media': {
            'title': 'Media Extract',
            'description': 'Extract images, videos, and downloadable content',
            'fields': ['url', 'stealth']
        },
        'interactive': {
            'title': 'Interactive Session',
            'description': 'Handle dynamic content with user interactions',
            'fields': ['url', 'actions', 'stealth']
        },
        'ai': {
            'title': 'AI-Powered Extract',
            'description': 'Intelligent content extraction with AI analysis',
            'fields': ['url', 'extraction_query', 'stealth']
        },
        'stealth': {
            'title': 'Definitive Stealth',
            'description': 'Advanced anti-detection crawling with 0.7.x stealth engine',
            'fields': ['url', 'stealth_level', 'user_agent']
        },
        'smart': {
            'title': 'Smart AI Deep Crawl',
            'description': 'AI-enhanced multi-page deep crawling with synthesis',
            'fields': ['url', 'extraction_query', 'max_pages', 'max_depth', 'strategy', 'ai_extraction']
        }
    }
    
    return jsonify({
        'status': 'success',
        'modes': modes
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /api/health',
            'GET /api/modes',
            'GET /api/statistics',
            'GET /api/recent',
            'GET /api/results',
            'GET /api/results/<id>',
            'POST /api/crawl',
            'POST /api/smart-crawl'
        ]
    }), 404

if __name__ == '__main__':
    print("🚀 Starting Enhanced Crawl4AI API Server with Database...")
    print("🔗 Frontend URL: http://localhost:3000")
    print("🌐 API Base URL: http://localhost:5000/api")
    print("📊 Database: PostgreSQL with persistent storage")
    print("📚 Enhanced Endpoints:")
    print("  GET  /api/health - Health check with DB status")
    print("  GET  /api/modes - Available crawl modes")
    print("  GET  /api/statistics - Crawl statistics and analytics")
    print("  GET  /api/recent - Recent crawl results")
    print("  GET  /api/results - Search and filter crawl results")
    print("  GET  /api/results/<id> - Get specific result by ID")
    print("  POST /api/crawl - Execute crawl operations with persistence")
    print("  POST /api/smart-crawl - AI-enhanced smart crawling with persistence")
    
    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables initialized")
        except Exception as e:
            print(f"⚠️  Database initialization warning: {e}")
    
    # Run Flask server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )