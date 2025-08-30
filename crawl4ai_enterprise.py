#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawl4AI Enterprise Engine - Production-Ready Web Scraping
Integrates Crawl4AI 0.7.x enterprise features with intelligent routing
"""

import asyncio
import json
import logging
import random
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, BrowserConfig
    from crawl4ai.extraction_strategy import LLMExtractionStrategy, JsonCssExtractionStrategy
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
    from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy
    from crawl4ai.content_filter_strategy import PruningContentFilter
    
    # 0.7.x Enterprise Features
    try:
        from crawl4ai import VirtualScrollConfig, SeedingConfig, AsyncUrlSeeder, MatchMode
        ENTERPRISE_FEATURES_AVAILABLE = True
    except ImportError:
        ENTERPRISE_FEATURES_AVAILABLE = False
        
    # Advanced stealth features
    try:
        from crawl4ai import UndetectedAdapter, RateLimiter, ProxyConfig
        ADVANCED_STEALTH_AVAILABLE = True
    except ImportError:
        ADVANCED_STEALTH_AVAILABLE = False
        
except ImportError:
    print("❌ crawl4ai not installed. Install with: pip install crawl4ai")
    raise

# Intent Detection System
class IntentType(Enum):
    ARTICLE = "article"
    DATA = "data"  
    SOCIAL = "social"
    ECOMMERCE = "ecommerce"
    DOCS = "docs"
    MEDIA = "media"
    FORM = "form"
    SEARCH = "search"
    GENERIC = "generic"

@dataclass
class CrawlRequest:
    """Standardized crawl request structure"""
    url: str
    intent: Optional[IntentType] = None
    options: Dict[str, Any] = None
    extraction_query: Optional[str] = None
    stealth_level: int = 1  # 1-5 scale
    enable_ai: bool = False
    ai_instruction: Optional[str] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}

@dataclass
class CrawlResult:
    """Standardized crawl result structure"""
    status: str
    url: str
    intent: Optional[IntentType] = None
    content: str = ""
    extracted_content: Any = None
    metadata: Dict[str, Any] = None
    media: Dict[str, List] = None
    links: List[Dict] = None
    performance: Dict[str, Any] = None
    stealth_features: Dict[str, Any] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.media is None:
            self.media = {"images": [], "videos": []}
        if self.links is None:
            self.links = []
        if self.performance is None:
            self.performance = {}

class EnterpriseWebCrawler:
    """Enterprise-grade web crawler with 0.7.x features"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        self.session_cache = {}
        self.performance_metrics = {}
        
        # Intent detection patterns
        self.intent_patterns = {
            IntentType.ARTICLE: [
                r'/(article|blog|post|news|story)/',
                r'medium\.com', r'substack\.com', r'dev\.to',
                r'/\d{4}/\d{2}/', r'wordpress\.com'
            ],
            IntentType.SOCIAL: [
                r'twitter\.com', r'instagram\.com', r'linkedin\.com',
                r'facebook\.com', r'tiktok\.com', r'reddit\.com'
            ],
            IntentType.ECOMMERCE: [
                r'amazon\.com', r'ebay\.com', r'shopify\.com',
                r'/product/', r'/shop/', r'/store/', r'\.shop'
            ],
            IntentType.DOCS: [
                r'/docs/', r'/documentation/', r'/api/',
                r'github\.io', r'readthedocs\.io', r'/wiki/'
            ],
            IntentType.MEDIA: [
                r'youtube\.com', r'vimeo\.com', r'twitch\.tv',
                r'/gallery/', r'/photos/', r'/images/'
            ],
            IntentType.DATA: [
                r'/data/', r'/dataset/', r'/api/', r'\.json',
                r'/table/', r'/dashboard/', r'/stats/'
            ]
        }
        
        # Stealth configurations by level
        self.stealth_configs = {
            1: {"basic": True, "user_agent": True},
            2: {"basic": True, "user_agent": True, "simulate_user": True},
            3: {"basic": True, "user_agent": True, "simulate_user": True, "magic": True},
            4: {"enterprise": True, "all_features": True, "human_delays": True},
            5: {"maximum": True, "proxy_rotation": True, "advanced_evasion": True}
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup enterprise logging"""
        logger = logging.getLogger("crawl4ai_enterprise")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    def detect_intent(self, url: str, context: Optional[str] = None) -> IntentType:
        """Intelligent intent detection from URL and context"""
        url_lower = url.lower()
        
        # Pattern matching
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                import re
                if re.search(pattern, url_lower):
                    self.logger.info(f"🎯 Intent detected: {intent_type.value} from URL pattern")
                    return intent_type
        
        # Context-based detection if provided
        if context:
            context_lower = context.lower()
            if any(word in context_lower for word in ['article', 'blog', 'news', 'story']):
                return IntentType.ARTICLE
            elif any(word in context_lower for word in ['shop', 'buy', 'product', 'price']):
                return IntentType.ECOMMERCE
            elif any(word in context_lower for word in ['data', 'table', 'chart', 'stats']):
                return IntentType.DATA
        
        return IntentType.GENERIC
    
    def create_adaptive_config(self, intent: IntentType, request: CrawlRequest) -> CrawlerRunConfig:
        """Create adaptive configuration based on intent"""
        base_config = {
            "markdown_generator": DefaultMarkdownGenerator(),
            "verbose": True,
            "word_count_threshold": 50
        }
        
        # Intent-specific optimizations
        if intent == IntentType.ARTICLE:
            base_config.update({
                "remove_overlay_elements": True,
                "scan_full_page": True
            })
            # Note: content_filter moved to markdown_generator in 0.7.x
            try:
                base_config["markdown_generator"] = DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter(threshold=0.48)
                )
            except Exception:
                # Fallback if PruningContentFilter isn't available
                base_config["markdown_generator"] = DefaultMarkdownGenerator()
            
        elif intent == IntentType.DATA:
            # Optimize for structured data extraction
            base_config.update({
                "js_code": self._get_data_extraction_js(),
                "delay_before_return_html": 3.0,
                "word_count_threshold": 10  # Include small data elements
            })
            
        elif intent == IntentType.SOCIAL:
            # Social media requires special handling
            if ENTERPRISE_FEATURES_AVAILABLE:
                base_config["virtual_scroll_config"] = VirtualScrollConfig(
                    container_selector="[data-testid='primaryColumn'], main, .feed",
                    scroll_count=10,
                    scroll_by="container_height",
                    wait_after_scroll=1.5
                )
            base_config.update({
                "js_code": self._get_social_media_js(),
                "delay_before_return_html": 4.0
            })
            
        elif intent == IntentType.ECOMMERCE:
            base_config.update({
                "js_code": self._get_ecommerce_js(),
                "delay_before_return_html": 2.5,
                "remove_overlay_elements": True
            })
            
        elif intent == IntentType.DOCS:
            # Documentation sites
            base_config.update({
                "scan_full_page": True,
                "word_count_threshold": 20
            })
            # Apply content filter through markdown generator
            try:
                base_config["markdown_generator"] = DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter(threshold=0.3)
                )
            except Exception:
                # Fallback if PruningContentFilter isn't available
                base_config["markdown_generator"] = DefaultMarkdownGenerator()
            
        elif intent == IntentType.MEDIA:
            # Media-rich sites
            base_config.update({
                "js_code": self._get_media_extraction_js(),
                "delay_before_return_html": 3.0
            })
        
        # Apply stealth configuration
        stealth_config = self._create_stealth_config(request.stealth_level)
        base_config.update(stealth_config)
        
        # Custom options from request
        base_config.update(request.options)
        
        return CrawlerRunConfig(**base_config)
    
    def _create_stealth_config(self, level: int) -> Dict[str, Any]:
        """Create stealth configuration by level"""
        config = {}
        
        if level >= 1:
            # Basic stealth
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            config["user_agent"] = random.choice(user_agents)
            
        if level >= 2:
            # Human simulation
            config.update({
                "simulate_user": True,
                "mean_delay": 1.0,
                "max_range": 2.0
            })
            
        if level >= 3:
            # Magic anti-detection
            config.update({
                "magic": True,
                "override_navigator": True,
                "remove_overlay_elements": True
            })
            
        if level >= 4:
            # Enterprise features
            config.update({
                "user_agent_mode": "random",
                "user_agent_generator_config": {
                    "platform": "windows",
                    "browser": "chrome",
                    "device_type": "desktop"
                },
                "delay_before_return_html": 2.0
            })
            
        if level >= 5:
            # Maximum stealth
            config.update({
                "js_code": self._get_advanced_stealth_js(),
                "mean_delay": 2.0,
                "max_range": 4.0,
                "scan_full_page": True
            })
            
        return config
    
    def _get_data_extraction_js(self) -> str:
        """JavaScript for data extraction optimization"""
        return """
        // Data extraction optimization
        (async () => {
            // Expand collapsible sections
            const expandButtons = document.querySelectorAll('[aria-expanded="false"], .expand, .show-more');
            expandButtons.forEach(btn => btn.click());
            
            // Load lazy tables and charts
            const lazyElements = document.querySelectorAll('[data-src], .lazy-load');
            lazyElements.forEach(el => {
                if (el.dataset.src) {
                    el.src = el.dataset.src;
                }
            });
            
            // Scroll to trigger lazy loading
            const tables = document.querySelectorAll('table, .data-table, .grid');
            for (const table of tables) {
                table.scrollIntoView({ behavior: 'smooth' });
                await new Promise(r => setTimeout(r, 500));
            }
            
            await new Promise(r => setTimeout(r, 2000));
        })();
        """
    
    def _get_social_media_js(self) -> str:
        """JavaScript for social media optimization"""
        return """
        // Social media content loading
        (async () => {
            const scrollContainer = document.querySelector('[data-testid="primaryColumn"], main, .feed') || document.body;
            const initialHeight = scrollContainer.scrollHeight;
            let currentHeight = initialHeight;
            let scrollAttempts = 0;
            const maxScrolls = 8;
            
            while (scrollAttempts < maxScrolls) {
                // Scroll by container height
                scrollContainer.scrollTop = scrollContainer.scrollHeight;
                
                // Wait for content to load
                await new Promise(r => setTimeout(r, 1500));
                
                // Check if new content loaded
                const newHeight = scrollContainer.scrollHeight;
                if (newHeight === currentHeight) {
                    break; // No new content
                }
                
                currentHeight = newHeight;
                scrollAttempts++;
                
                // Click "Show more" buttons if they exist
                const showMoreBtns = document.querySelectorAll('[data-testid="showMore"], .show-more, .load-more');
                showMoreBtns.forEach(btn => {
                    if (btn.offsetHeight > 0) btn.click();
                });
                
                await new Promise(r => setTimeout(r, 1000));
            }
            
            console.log(`Loaded ${scrollAttempts} additional sections`);
        })();
        """
    
    def _get_ecommerce_js(self) -> str:
        """JavaScript for e-commerce optimization"""
        return """
        // E-commerce site optimization
        (async () => {
            // Close popups and overlays
            const overlays = document.querySelectorAll('.popup, .modal, .overlay, .newsletter-popup, .cookie-banner');
            overlays.forEach(overlay => {
                const closeBtn = overlay.querySelector('.close, .dismiss, [aria-label="close"], .fa-times');
                if (closeBtn) closeBtn.click();
                else overlay.style.display = 'none';
            });
            
            // Expand product details
            const expandBtns = document.querySelectorAll('.read-more, .show-details, .expand-description');
            expandBtns.forEach(btn => btn.click());
            
            // Load product images
            const images = document.querySelectorAll('img[data-src], img.lazy');
            images.forEach(img => {
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                }
            });
            
            // Trigger reviews/ratings loading
            const reviewSections = document.querySelectorAll('.reviews, .ratings, .feedback');
            reviewSections.forEach(section => {
                section.scrollIntoView({ behavior: 'smooth' });
            });
            
            await new Promise(r => setTimeout(r, 2000));
        })();
        """
    
    def _get_media_extraction_js(self) -> str:
        """JavaScript for media extraction"""
        return """
        // Media extraction and interaction
        (async () => {
            // Identify all media elements
            const images = Array.from(document.querySelectorAll('img')).map(img => ({
                src: img.src || img.dataset.src,
                alt: img.alt,
                width: img.naturalWidth || img.width,
                height: img.naturalHeight || img.height,
                lazy: !!img.dataset.src
            }));
            
            const videos = Array.from(document.querySelectorAll('video, iframe[src*="youtube"], iframe[src*="vimeo"]')).map(vid => ({
                src: vid.src,
                type: vid.tagName.toLowerCase(),
                title: vid.title || vid.alt
            }));
            
            // Load lazy media
            const lazyImages = document.querySelectorAll('img[data-src]');
            lazyImages.forEach(img => {
                img.src = img.dataset.src;
            });
            
            // Store media data
            window.crawl4ai_media_enhanced = { images, videos, timestamp: Date.now() };
            
            // Expand gallery sections
            const galleryBtns = document.querySelectorAll('.gallery-expand, .view-all, .show-gallery');
            galleryBtns.forEach(btn => btn.click());
            
            await new Promise(r => setTimeout(r, 1500));
        })();
        """
    
    def _get_advanced_stealth_js(self) -> str:
        """Advanced stealth JavaScript for maximum evasion"""
        return """
        // Advanced stealth behavior simulation
        (async () => {
            const wait = (ms) => new Promise(r => setTimeout(r, ms + Math.random() * ms * 0.3));
            
            // Realistic viewport behavior
            const viewport = { width: window.innerWidth, height: window.innerHeight };
            
            // Human-like mouse movements
            const mouseEvents = ['mousemove', 'mouseenter', 'mouseleave'];
            for (let i = 0; i < 5; i++) {
                const x = Math.random() * viewport.width * 0.8 + viewport.width * 0.1;
                const y = Math.random() * viewport.height * 0.8 + viewport.height * 0.1;
                
                const event = new MouseEvent('mousemove', {
                    clientX: x, clientY: y, bubbles: true, cancelable: true
                });
                document.dispatchEvent(event);
                await wait(200);
            }
            
            // Natural reading pattern scrolling
            const scrollHeight = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
            const scrollSteps = Math.min(Math.floor(scrollHeight / viewport.height), 6);
            
            for (let i = 0; i < scrollSteps; i++) {
                const progress = i / Math.max(scrollSteps - 1, 1);
                const targetY = scrollHeight * progress * 0.85; // Don't scroll to absolute bottom
                
                window.scrollTo({ top: targetY, behavior: 'smooth' });
                await wait(1200);
                
                // Occasional micro-adjustments
                if (Math.random() > 0.6) {
                    window.scrollBy(0, (Math.random() - 0.5) * 80);
                    await wait(300);
                }
                
                // Random pause simulation (reading)
                if (Math.random() > 0.7) {
                    await wait(2000);
                }
            }
            
            // Return to optimal reading position
            window.scrollTo({ top: viewport.height * 0.2, behavior: 'smooth' });
            await wait(800);
            
            console.log('Advanced stealth simulation completed');
        })();
        """
    
    async def smart_crawl(self, request: CrawlRequest) -> CrawlResult:
        """Intelligent crawling with automatic optimization"""
        start_time = time.time()
        
        # Detect intent if not provided
        if not request.intent:
            request.intent = self.detect_intent(request.url, request.extraction_query)
        
        self.logger.info(f"🚀 Smart crawl: {request.url} (intent: {request.intent.value})")
        
        try:
            # Create adaptive configuration
            config = self.create_adaptive_config(request.intent, request)
            
            # Add AI extraction if requested
            if request.enable_ai and request.ai_instruction:
                config = await self._add_ai_extraction(config, request.ai_instruction)
            
            # Execute crawl
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(request.url, config=config)
            
            # Process results
            if result.success:
                crawl_result = CrawlResult(
                    status="success",
                    url=result.url,
                    intent=request.intent,
                    content=result.markdown,
                    metadata=result.metadata,
                    media=result.media,
                    links=list(result.links)[:20] if result.links else [],  # Limit links for performance
                    performance={
                        "duration": time.time() - start_time,
                        "content_size": len(result.markdown),
                        "links_found": len(list(result.links)) if result.links else 0,
                        "media_found": (
                            len(result.media.get("images", [])) + len(result.media.get("videos", []))
                            if result.media else 0
                        )
                    }
                )
                
                # Add extracted content if available
                if hasattr(result, 'extracted_content') and result.extracted_content:
                    crawl_result.extracted_content = result.extracted_content
                
                # Process intent-specific post-processing
                if request.extraction_query:
                    crawl_result.extracted_content = self._process_extraction_query(
                        crawl_result.content, request.extraction_query, request.intent
                    )
                
                self.logger.info(f"✅ Crawl completed in {crawl_result.performance['duration']:.2f}s")
                return crawl_result
            else:
                return CrawlResult(
                    status="error",
                    url=request.url,
                    error=result.error_message,
                    performance={"duration": time.time() - start_time}
                )
                
        except Exception as e:
            self.logger.error(f"Smart crawl failed: {e}")
            return CrawlResult(
                status="error",
                url=request.url,
                error=str(e),
                performance={"duration": time.time() - start_time}
            )
    
    async def _add_ai_extraction(self, config: CrawlerRunConfig, instruction: str) -> CrawlerRunConfig:
        """Add AI extraction to configuration"""
        try:
            # Use local LLM as default (free)
            llm_config = LLMConfig(
                provider="ollama/llama3.2",
                # Fallback to other providers if needed
            )
            
            extraction_strategy = LLMExtractionStrategy(
                llm_config=llm_config,
                instruction=instruction,
                extraction_type="block",
                chunk_token_threshold=2000,
                apply_chunking=True,
                verbose=True
            )
            
            config.extraction_strategy = extraction_strategy
            return config
            
        except Exception as e:
            self.logger.warning(f"AI extraction setup failed: {e}")
            return config
    
    def _process_extraction_query(self, content: str, query: str, intent: IntentType) -> Dict[str, Any]:
        """Process extraction query based on intent"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Intent-specific extraction logic
        if intent == IntentType.DATA:
            return self._extract_data_elements(content, query)
        elif intent == IntentType.ARTICLE:
            return self._extract_article_elements(content, query)
        elif intent == IntentType.ECOMMERCE:
            return self._extract_product_elements(content, query)
        else:
            return self._generic_extraction(content, query)
    
    def _extract_data_elements(self, content: str, query: str) -> Dict[str, Any]:
        """Extract data-specific elements"""
        import re
        
        # Find tables, numbers, statistics
        tables = re.findall(r'\|[^\n]*\|(?:\n\|[^\n]*\|)+', content)
        numbers = re.findall(r'\d+(?:\.\d+)?%?', content)
        
        # Find relevant sections
        query_words = query.lower().split()
        relevant_lines = []
        
        for line in content.split('\n'):
            line_lower = line.lower()
            relevance_score = sum(1 for word in query_words if word in line_lower)
            if relevance_score >= 2 or any(char in line for char in ['|', ':', '$', '%']):
                relevant_lines.append(line.strip())
        
        return {
            "type": "data_extraction",
            "tables": tables[:5],  # Top 5 tables
            "numbers": numbers[:20],  # Top 20 numbers
            "relevant_data": relevant_lines[:15],
            "query": query
        }
    
    def _extract_article_elements(self, content: str, query: str) -> Dict[str, Any]:
        """Extract article-specific elements"""
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Find most relevant paragraphs
        query_words = query.lower().split()
        scored_paragraphs = []
        
        for para in paragraphs:
            para_lower = para.lower()
            score = sum(1 for word in query_words if word in para_lower)
            if score > 0:
                scored_paragraphs.append((score, para))
        
        # Sort by relevance
        scored_paragraphs.sort(reverse=True, key=lambda x: x[0])
        
        return {
            "type": "article_extraction",
            "summary_paragraphs": [p[1] for p in scored_paragraphs[:3]],
            "all_relevant": [p[1] for p in scored_paragraphs[:10]],
            "total_paragraphs": len(paragraphs),
            "query": query
        }
    
    def _extract_product_elements(self, content: str, query: str) -> Dict[str, Any]:
        """Extract e-commerce product elements"""
        import re
        
        # Find prices
        prices = re.findall(r'\$\d+(?:\.\d{2})?|\d+(?:\.\d{2})?\s*(?:USD|EUR|GBP)', content)
        
        # Find product-related terms
        product_terms = ['price', 'cost', 'buy', 'purchase', 'discount', 'sale', 'review', 'rating']
        
        relevant_lines = []
        for line in content.split('\n'):
            line_lower = line.lower()
            if any(term in line_lower for term in product_terms) or any(word in line_lower for word in query.lower().split()):
                relevant_lines.append(line.strip())
        
        return {
            "type": "product_extraction",
            "prices": prices[:10],
            "product_info": relevant_lines[:15],
            "query": query
        }
    
    def _generic_extraction(self, content: str, query: str) -> Dict[str, Any]:
        """Generic extraction for any content type"""
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        query_words = query.lower().split()
        
        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            relevance_score = sum(1 for word in query_words if word in sentence_lower)
            if relevance_score >= 2:
                relevant_sentences.append(sentence)
        
        return {
            "type": "generic_extraction",
            "relevant_content": relevant_sentences[:10],
            "total_sentences": len(sentences),
            "query": query
        }
    
    async def batch_smart_crawl(self, requests: List[CrawlRequest], max_concurrent: int = 3) -> List[CrawlResult]:
        """Batch processing with intelligent concurrency"""
        self.logger.info(f"📦 Batch crawling {len(requests)} URLs")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_semaphore(request: CrawlRequest) -> CrawlResult:
            async with semaphore:
                return await self.smart_crawl(request)
        
        tasks = [crawl_with_semaphore(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(CrawlResult(
                    status="error",
                    url=requests[i].url,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        successful = sum(1 for r in processed_results if r.status == "success")
        self.logger.info(f"✅ Batch completed: {successful}/{len(requests)} successful")
        
        return processed_results
    
    async def discover_urls(self, base_url: str, query: str, max_urls: int = 20) -> List[str]:
        """Intelligent URL discovery using 0.7.x seeding features"""
        if not ENTERPRISE_FEATURES_AVAILABLE:
            self.logger.warning("URL seeding not available - using basic discovery")
            return [base_url]
        
        try:
            async with AsyncUrlSeeder() as seeder:
                config = SeedingConfig(
                    source="sitemap",
                    extract_head=True,
                    query=query,
                    scoring_method="bm25",
                    score_threshold=0.3,
                    max_urls=max_urls
                )
                
                urls = await seeder.urls(base_url, config)
                discovered = [url_data['url'] for url_data in urls]
                
                self.logger.info(f"🔍 Discovered {len(discovered)} relevant URLs")
                return discovered
                
        except Exception as e:
            self.logger.error(f"URL discovery failed: {e}")
            return [base_url]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance and usage metrics"""
        return {
            "cache_size": len(self.session_cache),
            "total_crawls": len(self.performance_metrics),
            "avg_duration": sum(m.get("duration", 0) for m in self.performance_metrics.values()) / max(len(self.performance_metrics), 1),
            "success_rate": sum(1 for m in self.performance_metrics.values() if m.get("status") == "success") / max(len(self.performance_metrics), 1),
            "features_available": {
                "enterprise": ENTERPRISE_FEATURES_AVAILABLE,
                "advanced_stealth": ADVANCED_STEALTH_AVAILABLE
            }
        }

# Export the main class
__all__ = ["EnterpriseWebCrawler", "CrawlRequest", "CrawlResult", "IntentType"]