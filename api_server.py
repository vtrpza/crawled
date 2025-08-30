#!/usr/bin/env python3
"""
Simple Flask API server for Crawl4AI POC
Provides REST endpoints that mirror our POC functionality
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import threading

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

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'crawl4ai-poc-api'
    })

@app.route('/api/smart-crawl', methods=['POST'])
@api_endpoint(required_fields=['url'])
def smart_crawl():
    """Smart crawl endpoint with AI-first deep crawling as default"""
    data = request.get_json()
    
    # Validate and sanitize inputs
    url = validate_url(data.get('url'))
    stealth_level = validate_stealth_level(data.get('stealth_level', 4))  # Default to medium stealth
    custom_user_agent = data.get('user_agent')
    intent = data.get('intent', 'general')
    extraction_query = data.get('extraction_query', '')
    
    # Deep crawl parameters (new for AI-first experience)
    max_pages = min(int(data.get('max_pages', 5)), 20)  # Limit to 20 pages max
    max_depth = min(int(data.get('max_depth', 2)), 5)   # Limit to 5 levels deep
    crawl_strategy = data.get('strategy', 'bfs').lower()
    
    # AI extraction is now MANDATORY - always enabled
    ai_extraction = data.get('ai_extraction', {})
    if not ai_extraction:
        # Force AI extraction with default settings
        ai_extraction = {'model': 'groq', 'enabled': True}
    
    # Debug: Show what we received
    print(f"🔍 Debug AI extraction config: {ai_extraction}")
    print(f"🔑 API key present: {'***' if ai_extraction.get('api_key') else 'None'}")
    
    print(f"🤖 AI-First Deep Crawl - AI extraction MANDATORY")
    print(f"📝 Extraction query: '{extraction_query}'")
    print(f"🔄 Strategy: {crawl_strategy.upper()}, Pages: {max_pages}, Depth: {max_depth}")
    
    # Map frontend model names to provider strings
    model = ai_extraction.get('model', 'groq')
    provider_map = {
        'ollama': 'ollama/llama3.2',
        'gpt-4': 'openai/gpt-4o',
        'claude-3': 'anthropic/claude-3-5-sonnet',
        'gemini-pro': 'gemini/gemini-1.5-pro',
        'groq': 'groq/llama-3.3-70b-versatile'  # Best Groq model - default for AI-first experience
    }
    provider = provider_map.get(model, 'groq/llama-3.3-70b-versatile')  # Default to best Groq model
    
    # Use AI-enhanced deep crawl as the DEFAULT mode
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
        # AI-Enhanced Deep Crawl Success Response
        return jsonify({
            'status': 'success',
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
            'ai_analysis': result.get('ai_synthesis', ''),  # Backward compatibility
            'extracted_content': result.get('ai_synthesis', ''),  # Backward compatibility
            
            # Individual page results
            'individual_pages': result.get('individual_pages', []),
            'total_content_length': result.get('total_content_length', 0),
            
            # Enhanced metadata
            'metadata': result.get('metadata', {}),
            'performance': {
                'pages_crawled': result.get('pages_crawled', 0),
                'ai_processing_mandatory': True,
                'deep_crawl_enabled': True,
                'synthesis_generated': result.get('metadata', {}).get('synthesis_generated', False)
            },
            
            # Stealth and AI features
            'stealth_features': {
                'ai_powered': True,
                'ai_mandatory': True,
                'deep_crawl': True,
                'stealth_level': stealth_level,
                'provider': result.get('ai_provider', provider),
                'fallback_mode': result.get('crawl_type', '').endswith('_fallback')
            }
        })
    else:
        return jsonify({
            'status': 'error',
            'error': result.get('error', 'AI-enhanced deep crawl failed'),
            'crawl_type': result.get('crawl_type', 'ai_enhanced_deep_crawl_failed'),
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'attempted_config': {
                'max_pages': max_pages,
                'max_depth': max_depth,
                'strategy': crawl_strategy,
                'ai_mandatory': True
            }
        }), 500

@app.route('/api/batch-smart-crawl', methods=['POST'])
@api_endpoint(required_fields=['urls'])
def batch_smart_crawl():
    """Batch smart crawl endpoint for multiple URLs"""
    data = request.get_json()
    
    # Validate and sanitize inputs
    urls = validate_urls_array(data.get('urls'), max_count=10)
    action = validate_action(data.get('action', 'smart'))
    stealth_level = validate_stealth_level(data.get('stealth_level'))
    max_concurrent = validate_concurrent(data.get('concurrent'), max_concurrent=5)
    options = sanitize_options(data.get('options', {}))
    
    # Create crawl requests
    requests = []
    for url in urls:
        crawl_request = CrawlRequest(
            url=url,
            stealth_level=stealth_level,
            options=options
        )
        requests.append(crawl_request)
    
    # Execute batch crawl
    async def _batch_crawl():
        return await enterprise_crawler.batch_smart_crawl(requests, max_concurrent)
    
    results = run_async(_batch_crawl())
    
    # Format batch response
    batch_response = {
        'status': 'completed',
        'total_urls': len(requests),
        'successful': sum(1 for r in results if r.status == "success"),
        'failed': sum(1 for r in results if r.status == "error"),
        'timestamp': datetime.now().isoformat(),
        'results': []
    }
    
    # Add individual results (limited data for performance)
    for result in results:
        if result.status == "success":
            batch_response['results'].append({
                'url': result.url,
                'status': 'success',
                'intent': result.intent.value if result.intent else 'generic',
                'content_size': len(result.content),
                'links_found': len(result.links) if result.links else 0,
                'media_found': (
                    len(result.media['images']) + len(result.media['videos'])
                    if result.media else 0
                ),
                'duration': result.performance.get('duration', 0),
                'preview': result.content[:200] + '...' if len(result.content) > 200 else result.content
            })
        else:
            batch_response['results'].append({
                'url': result.url,
                'status': 'error',
                'error': result.error,
                'duration': result.performance.get('duration', 0) if result.performance else 0
            })
    
    return jsonify(batch_response)

@app.route('/api/discover-urls', methods=['POST'])
@api_endpoint()
def discover_urls():
    """URL discovery endpoint using intelligent seeding"""
    data = request.get_json()
    
    # Validate and sanitize inputs
    base_url = validate_url(data.get('base_url') or data.get('url', ''))
    query = validate_query(data.get('query', ''))
    max_urls = validate_max_urls(data.get('max_urls'), limit=25)
    
    # Execute URL discovery
    async def _discover():
        return await enterprise_crawler.discover_urls(base_url, query, max_urls)
    
    discovered_urls = run_async(_discover())
    
    return jsonify({
        'status': 'success',
        'base_url': base_url,
        'query': query,
        'discovered_count': len(discovered_urls),
        'urls': discovered_urls,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Performance and usage metrics endpoint"""
    try:
        metrics = enterprise_crawler.get_performance_metrics()
        return jsonify({
            'status': 'success',
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/crawl', methods=['POST'])
def crawl():
    """Main crawl endpoint that handles all modes"""
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
                result = await poc.ai_powered_crawl(url, instruction, use_stealth=stealth)
                
            elif mode == 'stealth':
                stealth_level = int(data.get('stealth_level', 5))
                custom_user_agent = data.get('user_agent')
                # Use our definitive stealth engine
                stealth_result = await stealth_engine.stealth_crawl(url, stealth_level, custom_user_agent)
                # Convert to POC format for compatibility
                result = {
                    'status': 'success' if stealth_result.success and stealth_result.detection_bypassed else 'error',
                    'url': stealth_result.url,
                    'content': stealth_result.content,
                    'stealth_features': stealth_result.stealth_config,
                    'detection_bypassed': stealth_result.detection_bypassed,
                    'response_time': stealth_result.response_time,
                    'error': stealth_result.error
                }
                
            else:
                raise ValueError(f'Unknown mode: {mode}')
                
            return result
            
        # Run the async operation
        result = run_async(_crawl())
            
        # Handle POC method results (they return Dict objects)
        if result and isinstance(result, dict):
            if result.get('status') == 'success':
                # POC methods return structured Dict results
                response_data = {
                    'status': 'success',
                    'mode': mode,
                    'url': url,
                    'timestamp': datetime.now().isoformat(),
                    'content': result.get('content', ''),
                    'metadata': result.get('metadata', {}),
                    'stealth_features': result.get('stealth_features', []) if mode == 'stealth' or data.get('stealth') else None
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
                # POC method returned error
                return jsonify({
                    'status': 'error',
                    'error': result.get('error', 'Unknown error occurred'),
                    'mode': mode,
                    'url': url,
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        else:
            # Handle unexpected result format
            return jsonify({
                'status': 'error',
                'error': f'Unexpected result format: {type(result)}',
                'mode': mode,
                'url': url,
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        print(f"API Error: {e}")
        print(f"Error type: {type(e)}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': f"{type(e).__name__}: {str(e)}",
            'timestamp': datetime.now().isoformat()
        }), 500

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
            'GET /api/metrics', 
            'POST /api/crawl',
            'POST /api/smart-crawl',
            'POST /api/batch-smart-crawl',
            'POST /api/discover-urls'
        ]
    }), 404

if __name__ == '__main__':
    print("🚀 Starting Crawl4AI POC API Server...")
    print("🔗 Frontend URL: http://localhost:3000")
    print("🌐 API Base URL: http://localhost:5000/api")
    print("📚 Endpoints:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/modes - Available crawl modes")
    print("  POST /api/crawl - Execute crawl operations")
    
    # Run Flask server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )