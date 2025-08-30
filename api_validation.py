#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Validation and Error Handling Module
Production-ready validation, sanitization, and error handling
"""

import re
import logging
import time
import traceback
from functools import wraps
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from flask import request, jsonify
from datetime import datetime

# Setup logging
logger = logging.getLogger("api_validation")

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None, code: str = "VALIDATION_ERROR"):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}  # IP -> [(timestamp, endpoint)]
        self.limits = {
            "default": (60, 60),  # 60 requests per 60 seconds
            "/api/smart-crawl": (30, 60),  # 30 requests per 60 seconds
            "/api/batch-smart-crawl": (10, 60),  # 10 requests per 60 seconds
            "/api/discover-urls": (20, 60)  # 20 requests per 60 seconds
        }
    
    def is_allowed(self, client_ip: str, endpoint: str) -> Tuple[bool, int]:
        """Check if request is allowed, return (allowed, reset_time)"""
        now = time.time()
        key = f"{client_ip}:{endpoint}"
        
        # Get rate limit for endpoint
        max_requests, window = self.limits.get(endpoint, self.limits["default"])
        
        # Clean old requests
        if key in self.requests:
            self.requests[key] = [
                (ts, ep) for ts, ep in self.requests[key] 
                if now - ts < window
            ]
        else:
            self.requests[key] = []
        
        # Check limit
        current_requests = len(self.requests[key])
        
        if current_requests >= max_requests:
            # Calculate reset time
            oldest_request = min(ts for ts, _ in self.requests[key])
            reset_time = int(oldest_request + window)
            return False, reset_time
        
        # Record this request
        self.requests[key].append((now, endpoint))
        return True, 0

# Global rate limiter instance
rate_limiter = RateLimiter()

def validate_url(url: str) -> str:
    """Validate and sanitize URL"""
    if not url:
        raise ValidationError("URL is required", "url")
    
    # Basic URL validation
    if not isinstance(url, str):
        raise ValidationError("URL must be a string", "url")
    
    # Length check
    if len(url) > 2048:
        raise ValidationError("URL too long (max 2048 characters)", "url")
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    # Parse and validate URL structure
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValidationError("Invalid URL format", "url")
        
        # Security checks
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError("Only HTTP and HTTPS URLs are allowed", "url")
        
        # Block internal/localhost URLs in production
        if parsed.hostname in ['localhost', '127.0.0.1'] or parsed.hostname.startswith('192.168.'):
            logger.warning(f"Internal URL blocked: {url}")
            # Allow in development, block in production
            # raise ValidationError("Internal URLs are not allowed", "url")
        
        return url
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Invalid URL: {str(e)}", "url")

def validate_urls_array(urls: List[str], max_count: int = 10) -> List[str]:
    """Validate array of URLs"""
    if not urls:
        raise ValidationError("URLs array is required", "urls")
    
    if not isinstance(urls, list):
        raise ValidationError("URLs must be an array", "urls")
    
    if len(urls) == 0:
        raise ValidationError("At least one URL is required", "urls")
    
    if len(urls) > max_count:
        raise ValidationError(f"Maximum {max_count} URLs allowed", "urls")
    
    # Validate each URL
    validated_urls = []
    for i, url in enumerate(urls):
        try:
            validated_url = validate_url(url)
            validated_urls.append(validated_url)
        except ValidationError as e:
            raise ValidationError(f"URL {i+1}: {e.message}", "urls")
    
    return validated_urls

def validate_query(query: str, max_length: int = 500) -> str:
    """Validate search/extraction query"""
    if query is None:
        return ""
    
    if not isinstance(query, str):
        raise ValidationError("Query must be a string", "query")
    
    if len(query) > max_length:
        raise ValidationError(f"Query too long (max {max_length} characters)", "query")
    
    # Sanitize query
    query = query.strip()
    
    # Basic injection protection
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'exec\s*\('
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValidationError("Query contains potentially dangerous content", "query")
    
    return query

def validate_stealth_level(level: Any) -> int:
    """Validate stealth level parameter"""
    if level is None or level == "":
        return 2  # Default
    
    try:
        # Handle string numbers and floats
        if isinstance(level, str):
            level = level.strip()
            if level == "":
                return 2  # Default for empty string
        
        level = int(float(level))  # Convert through float to handle "2.0" strings
        if level < 1 or level > 5:
            raise ValidationError("Stealth level must be between 1 and 5", "stealth_level")
        return level
    except (ValueError, TypeError):
        raise ValidationError("Stealth level must be a number", "stealth_level")

def validate_concurrent(concurrent: Any, max_concurrent: int = 5) -> int:
    """Validate concurrency parameter"""
    if concurrent is None:
        return 3  # Default
    
    try:
        concurrent = int(concurrent)
        if concurrent < 1:
            raise ValidationError("Concurrency must be at least 1", "concurrent")
        if concurrent > max_concurrent:
            concurrent = max_concurrent  # Cap at maximum
        return concurrent
    except (ValueError, TypeError):
        raise ValidationError("Concurrency must be a number", "concurrent")

def validate_max_urls(max_urls: Any, limit: int = 25) -> int:
    """Validate max URLs parameter"""
    if max_urls is None:
        return 15  # Default
    
    try:
        max_urls = int(max_urls)
        if max_urls < 1:
            raise ValidationError("Max URLs must be at least 1", "max_urls")
        if max_urls > limit:
            max_urls = limit  # Cap at limit
        return max_urls
    except (ValueError, TypeError):
        raise ValidationError("Max URLs must be a number", "max_urls")

def validate_action(action: str) -> str:
    """Validate action parameter"""
    if not action:
        return "smart"  # Default
    
    valid_actions = [
        'smart', 'article', 'data', 'social', 'ecommerce',
        'docs', 'media', 'form', 'search', 'generic'
    ]
    
    if action not in valid_actions:
        raise ValidationError(f"Invalid action. Must be one of: {', '.join(valid_actions)}", "action")
    
    return action

def sanitize_options(options: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize options dictionary"""
    if not options:
        return {}
    
    if not isinstance(options, dict):
        raise ValidationError("Options must be an object", "options")
    
    # Whitelist allowed option keys
    allowed_keys = [
        'delay_before_return_html', 'word_count_threshold', 'verbose',
        'remove_overlay_elements', 'scan_full_page', 'wait_after_scroll',
        'scroll_count', 'user_agent_mode'
    ]
    
    sanitized = {}
    for key, value in options.items():
        if key in allowed_keys:
            # Basic type validation
            if key in ['delay_before_return_html'] and isinstance(value, (int, float)):
                sanitized[key] = float(value)
            elif key in ['word_count_threshold', 'scroll_count'] and isinstance(value, int):
                sanitized[key] = int(value)
            elif key in ['verbose', 'remove_overlay_elements', 'scan_full_page'] and isinstance(value, bool):
                sanitized[key] = bool(value)
            elif key == 'user_agent_mode' and isinstance(value, str):
                if value in ['random', 'chrome', 'firefox', 'safari']:
                    sanitized[key] = value
    
    return sanitized

def rate_limit(f):
    """Rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        endpoint = request.endpoint
        
        allowed, reset_time = rate_limiter.is_allowed(client_ip, endpoint)
        
        if not allowed:
            return jsonify({
                'status': 'error',
                'error': 'Rate limit exceeded',
                'code': 'RATE_LIMIT_EXCEEDED',
                'reset_time': reset_time,
                'timestamp': datetime.now().isoformat()
            }), 429
        
        return f(*args, **kwargs)
    return decorated_function

def validate_request(required_fields: List[str] = None, 
                    optional_fields: List[str] = None):
    """Request validation decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get JSON data
                data = request.get_json()
                if not data:
                    return jsonify({
                        'status': 'error',
                        'error': 'JSON data required',
                        'code': 'MISSING_JSON_DATA',
                        'timestamp': datetime.now().isoformat()
                    }), 400
                
                # Validate required fields
                if required_fields:
                    for field in required_fields:
                        if field not in data:
                            return jsonify({
                                'status': 'error',
                                'error': f'Missing required field: {field}',
                                'code': 'MISSING_REQUIRED_FIELD',
                                'field': field,
                                'timestamp': datetime.now().isoformat()
                            }), 400
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                logger.warning(f"Validation error: {e.message} (field: {e.field})")
                return jsonify({
                    'status': 'error',
                    'error': e.message,
                    'code': e.code,
                    'field': e.field,
                    'timestamp': datetime.now().isoformat()
                }), 400
            except Exception as e:
                logger.error(f"Validation decorator error: {e}")
                return jsonify({
                    'status': 'error',
                    'error': 'Invalid request format',
                    'code': 'INVALID_REQUEST',
                    'timestamp': datetime.now().isoformat()
                }), 400
        
        return decorated_function
    return decorator

def handle_api_error(f):
    """API error handling decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {f.__name__}: {e.message}")
            return jsonify({
                'status': 'error',
                'error': e.message,
                'code': e.code,
                'field': e.field,
                'timestamp': datetime.now().isoformat()
            }), 400
        except Exception as e:
            # Log full error for debugging
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            logger.error(traceback.format_exc())
            
            # Return safe error message to client
            return jsonify({
                'status': 'error',
                'error': 'Internal server error',
                'code': 'INTERNAL_ERROR',
                'timestamp': datetime.now().isoformat()
            }), 500
    
    return decorated_function

def log_api_request(f):
    """API request logging decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        logger.info(f"API Request: {request.method} {request.path} from {client_ip}")
        
        try:
            response = f(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log response status
            if hasattr(response, 'status_code'):
                status = response.status_code
            else:
                status = 200  # Default for successful returns
            
            logger.info(f"API Response: {request.path} -> {status} ({duration:.2f}s)")
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"API Error: {request.path} -> Error ({duration:.2f}s): {e}")
            raise
    
    return decorated_function

# Combined decorator for all API endpoints
def api_endpoint(required_fields: List[str] = None):
    """Combined decorator for API endpoints with all protections"""
    def decorator(f):
        return log_api_request(
            handle_api_error(
                rate_limit(
                    validate_request(required_fields)(f)
                )
            )
        )
    return decorator