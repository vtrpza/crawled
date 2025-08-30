#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawl4AI Definitive Stealth Engine - 0.7.x Compatible
Maximum stealth implementation for bypassing bot detection systems like Magazine Luiza
Based on official Crawl4AI 0.7.x documentation and working examples
"""

import asyncio
import json
import logging
import random
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass

try:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
except ImportError:
    print("❌ crawl4ai not installed. Install with: pip install crawl4ai")
    raise

@dataclass
class StealthResult:
    """Stealth crawl result with detailed metrics"""
    success: bool
    url: str
    content: str
    stealth_config: Dict[str, Any]
    detection_bypassed: bool
    response_time: float
    user_agent_used: str
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class Crawl4AIStealthEngine:
    """Definitive stealth crawler using proven 0.7.x techniques"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Enhanced user agents optimized for Brazilian e-commerce sites
        self.stealth_user_agents = [
            # Chrome variants (most common in Brazil)
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", 
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            # Firefox variants 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0",
            # Mobile browsers (growing in Brazil)
            "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        ]
        
        # Stealth escalation levels
        self.stealth_levels = {
            1: "Basic stealth - user agent rotation",
            2: "Enhanced stealth - user simulation + navigator override", 
            3: "Advanced stealth - magic detection handling",
            4: "Maximum stealth - human behavior patterns",
            5: "Extreme stealth - all features + custom JS"
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup detailed logging"""
        logger = logging.getLogger("crawl4ai_stealth")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def create_stealth_config(self, level: int = 5, custom_user_agent: str = None) -> CrawlerRunConfig:
        """
        Create stealth configuration based on official 0.7.x approach with CDN bypass
        """
        # Base stealth configuration using proven 0.7.x methods
        base_config = {
            # Core anti-detection features  
            "simulate_user": True,      # Simulate human mouse movements  
            "override_navigator": True,  # Override navigator properties
            "magic": True,              # Auto-handle common bot detection patterns
            
            # Human-like timing (longer delays for CDN bypass)
            "mean_delay": 3.0,
            "max_range": 6.0,
            "delay_before_return_html": 5.0,
            
            # Additional stealth features
            "remove_overlay_elements": True,  # Remove popups/overlays
            "scan_full_page": True,          # Full page scan
            "verbose": True
        }
        
        # Custom user agent override or use random selection
        if custom_user_agent:
            base_config["user_agent"] = custom_user_agent
        else:
            # Use random user agent from our proven list
            base_config["user_agent"] = random.choice(self.stealth_user_agents)
        
        # Level-specific enhancements with enhanced timing
        if level >= 2:
            base_config.update({
                "mean_delay": 2.0,
                "max_range": 4.0,
                "page_timeout": 45000  # Longer timeout for stability
            })
            
        if level >= 3:
            base_config.update({
                "delay_before_return_html": 5.0,
                "word_count_threshold": 5,  # Include more content
                "wait_until": "load",  # More reliable than networkidle
                "page_timeout": 30000  # Reduce timeout to prevent hanging
            })
            
        if level >= 4:
            base_config.update({
                "mean_delay": 3.5,
                "max_range": 7.0,
                "delay_before_return_html": 7.0,
                "session_id": "stealth_session_" + str(level),  # Persistent session
                "page_timeout": 35000  # Balanced timeout
            })
            
        if level >= 5:
            # Maximum stealth with all features
            base_config.update({
                "js_code": self._get_stealth_javascript(),
                "mean_delay": 4.5,
                "max_range": 9.0,
                "delay_before_return_html": 8.0,
                "session_id": "max_stealth_session",
                "page_timeout": 40000,  # Reasonable timeout to prevent hangs
                "wait_until": "domcontentloaded",  # More reliable than networkidle
                "wait_for_images": False,  # Don't wait for images to prevent timeouts
                "adjust_viewport_to_content": True  # Dynamic viewport adjustment
            })
        
        return CrawlerRunConfig(**base_config)
    
    def _get_stealth_javascript(self) -> str:
        """
        Advanced JavaScript for maximum stealth behavior with CDN bypass techniques
        Simulates realistic human browsing patterns and evades fingerprinting
        """
        return """
        // Advanced stealth behavior simulation with CDN/edge bypass techniques
        (async () => {
            const wait = (ms) => new Promise(r => setTimeout(r, ms + Math.random() * ms * 0.4));
            
            // Advanced fingerprinting evasion
            console.log('🥷 Advanced stealth mode activated - CDN bypass techniques');
            
            // 1. Override webdriver detection
            if (navigator.webdriver) {
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            }
            
            // 2. Simulate realistic viewport and screen properties
            const viewport = {
                width: window.innerWidth,
                height: window.innerHeight
            };
            
            // 3. Add realistic browser plugins simulation
            Object.defineProperty(navigator, 'plugins', {
                get: () => ({
                    length: 3,
                    0: { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                    1: { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    2: { name: 'Native Client', filename: 'internal-nacl-plugin' }
                })
            });
            
            // 4. Simulate realistic language preferences (Brazilian Portuguese)
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
            
            // 5. Wait for initial page load (CDN detection often checks immediate behavior)
            await wait(3000);
            
            // 1. Natural mouse movement patterns
            const mouseEvents = ['mousemove', 'mouseenter', 'mouseleave'];
            for (let i = 0; i < 8; i++) {
                const x = Math.random() * viewport.width * 0.9 + viewport.width * 0.05;
                const y = Math.random() * viewport.height * 0.9 + viewport.height * 0.05;
                
                // Create realistic mouse movement
                const event = new MouseEvent('mousemove', {
                    clientX: x,
                    clientY: y,
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                document.dispatchEvent(event);
                await wait(180);
            }
            
            // 2. Human reading pattern scrolling
            const totalHeight = Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.offsetHeight,
                document.body.clientHeight,
                document.documentElement.clientHeight
            );
            
            const scrollSteps = Math.min(Math.floor(totalHeight / viewport.height), 8);
            console.log(`📜 Simulating ${scrollSteps} scroll steps for reading pattern`);
            
            for (let i = 0; i < scrollSteps; i++) {
                const progress = i / Math.max(scrollSteps - 1, 1);
                const targetY = totalHeight * progress * 0.85; // Don't scroll to absolute bottom
                
                window.scrollTo({
                    top: targetY,
                    behavior: 'smooth'
                });
                
                await wait(1400);
                
                // Occasional micro-adjustments (human behavior)
                if (Math.random() > 0.65) {
                    const microAdjust = (Math.random() - 0.5) * 100;
                    window.scrollBy(0, microAdjust);
                    await wait(350);
                }
                
                // Random pause simulation (reading comprehension)
                if (Math.random() > 0.75) {
                    await wait(2500);
                }
                
                // Interact with page elements occasionally
                if (Math.random() > 0.8) {
                    const clickableElements = document.querySelectorAll('button, a, input, [role="button"]');
                    if (clickableElements.length > 0) {
                        const randomElement = clickableElements[Math.floor(Math.random() * Math.min(clickableElements.length, 3))];
                        if (randomElement && randomElement.offsetHeight > 0) {
                            // Simulate hover without clicking
                            const hoverEvent = new MouseEvent('mouseenter', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            randomElement.dispatchEvent(hoverEvent);
                            await wait(200);
                        }
                    }
                }
            }
            
            // 3. Return to optimal reading position
            const readingPosition = Math.min(viewport.height * 0.3, totalHeight * 0.1);
            window.scrollTo({
                top: readingPosition,
                behavior: 'smooth'
            });
            await wait(800);
            
            // 4. Close any overlays or popups that might interfere
            const overlaySelectors = [
                '.popup', '.modal', '.overlay', '.cookie-banner', 
                '.newsletter-popup', '[data-testid*="popup"]',
                '[class*="modal"]', '[class*="overlay"]'
            ];
            
            overlaySelectors.forEach(selector => {
                const overlays = document.querySelectorAll(selector);
                overlays.forEach(overlay => {
                    const closeBtn = overlay.querySelector('.close, .dismiss, [aria-label*="close" i], .fa-times, .x-button, [data-testid*="close"]');
                    if (closeBtn) {
                        console.log('🚫 Closing overlay/popup');
                        closeBtn.click();
                    } else if (overlay.style) {
                        overlay.style.display = 'none';
                    }
                });
            });
            
            // 5. Advanced CDN bypass techniques
            
            // A) Header consistency simulation (CDN often checks request headers vs JS environment)
            if (navigator.language !== 'pt-BR') {
                Object.defineProperty(navigator, 'language', {
                    get: () => 'pt-BR',
                    configurable: false
                });
            }
            
            // B) Request interception simulation
            if (window.fetch) {
                const originalFetch = window.fetch;
                window.fetch = function(...args) {
                    console.log('🌐 Intercepted fetch request:', args[0]);
                    return originalFetch.apply(this, args);
                };
            }
            
            // C) Simulate genuine browser timing patterns
            window.performance.mark('page-interaction-start');
            
            // D) Override common bot detection methods
            Object.defineProperty(window, 'outerHeight', {
                get: () => window.innerHeight
            });
            Object.defineProperty(window, 'outerWidth', {
                get: () => window.innerWidth  
            });
            
            // E) Simulate realistic timezone and language consistency
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            if (timezone !== 'America/Sao_Paulo') {
                // Override timezone to match Brazilian target
                Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
                    value: function() { 
                        return { ...this.constructor.prototype.resolvedOptions.call(this), timeZone: 'America/Sao_Paulo' }; 
                    }
                });
            }
            
            // F) Add realistic CPU usage patterns (prevents too-fast execution detection)
            for (let i = 0; i < 50; i++) {
                Math.random() * Math.random() * new Date().getTime();
                if (i % 10 === 0) await wait(5);
            }
            
            // G) Advanced fingerprint consistency
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(contextType, ...args) {
                if (contextType === '2d') {
                    const context = originalGetContext.apply(this, arguments);
                    // Add noise to prevent canvas fingerprinting
                    if (context) {
                        const originalGetImageData = context.getImageData;
                        context.getImageData = function() {
                            const imageData = originalGetImageData.apply(this, arguments);
                            if (imageData && imageData.data) {
                                // Add minimal noise to bypass fingerprinting
                                for (let i = 0; i < imageData.data.length; i += 100) {
                                    imageData.data[i] = imageData.data[i] ^ (Math.random() > 0.5 ? 1 : 0);
                                }
                            }
                            return imageData;
                        };
                    }
                    return context;
                }
                return originalGetContext.apply(this, arguments);
            };
            
            // 6. Final human behavior - random focus events
            const focusableElements = document.querySelectorAll('input, button, a, select, textarea');
            if (focusableElements.length > 0) {
                const randomFocusable = focusableElements[Math.floor(Math.random() * Math.min(focusableElements.length, 5))];
                if (randomFocusable && randomFocusable.offsetHeight > 0) {
                    randomFocusable.focus();
                    await wait(300);
                    randomFocusable.blur();
                }
            }
            
            console.log('✅ Advanced stealth simulation completed');
        })();
        """
    
    async def stealth_crawl(self, url: str, stealth_level: int = 5, custom_user_agent: str = None) -> StealthResult:
        """
        Execute stealth crawl with maximum anti-detection
        """
        start_time = time.time()
        self.logger.info(f"🥷 Starting stealth crawl (level {stealth_level}): {url}")
        
        try:
            # Create stealth configuration
            config = self.create_stealth_config(stealth_level, custom_user_agent)
            
            # Set markdown generator
            config.markdown_generator = DefaultMarkdownGenerator()
            
            # Get the user agent that will be used
            used_user_agent = custom_user_agent or "randomized"
            
            self.logger.info(f"🔧 Stealth config: {self.stealth_levels.get(stealth_level, 'Unknown level')}")
            self.logger.info(f"🎭 User agent: {'custom' if custom_user_agent else 'randomized'}")
            
            # Enhanced browser configuration for maximum stealth
            from crawl4ai import BrowserConfig
            browser_config = BrowserConfig(
                headless=True,
                browser_type="chromium", 
                user_agent=config.user_agent,
                viewport_width=1920,
                viewport_height=1080,
                accept_downloads=False,
                java_script_enabled=True
            )
            
            # Execute crawl with enhanced stealth config
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url, config=config)
            
            response_time = time.time() - start_time
            
            if result.success:
                # Check if we bypassed detection (more specific indicators)
                content = result.markdown.lower()
                
                # Primary detection indicators (definitive bot challenges)
                primary_indicators = [
                    'complete o captcha', 'i\'m not a robot', 'verify you are human',
                    'bot detection', 'access denied', 'blocked', 'suspicious activity',
                    'security check', 'verification required', 'parece que você acessou nosso site de uma forma'
                ]
                
                # Check for actual challenge page vs legitimate content mentioning these words
                is_challenge_page = any(indicator in content for indicator in primary_indicators)
                has_product_content = any(term in content for term in ['produto', 'preço', 'comprar', 'adicionar'])
                
                # Detection is bypassed if no challenge page indicators OR has actual product content
                detection_bypassed = not is_challenge_page or has_product_content
                
                self.logger.info(f"✅ Crawl successful in {response_time:.2f}s")
                self.logger.info(f"🛡️ Detection bypassed: {detection_bypassed}")
                
                return StealthResult(
                    success=True,
                    url=result.url,
                    content=result.markdown,
                    stealth_config={
                        "level": stealth_level,
                        "user_agent_mode": "random" if not custom_user_agent else "custom",
                        "simulate_user": True,
                        "override_navigator": True,
                        "magic": True,
                        "mean_delay": config.mean_delay,
                        "max_range": config.max_range,
                        "delay_before_return_html": config.delay_before_return_html,
                        "javascript_stealth": stealth_level >= 5
                    },
                    detection_bypassed=detection_bypassed,
                    response_time=response_time,
                    user_agent_used=used_user_agent,
                    metadata=result.metadata
                )
            else:
                self.logger.error(f"❌ Crawl failed: {result.error_message}")
                return StealthResult(
                    success=False,
                    url=url,
                    content="",
                    stealth_config={},
                    detection_bypassed=False,
                    response_time=response_time,
                    user_agent_used=used_user_agent,
                    error=result.error_message
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"💥 Stealth crawl exception: {e}")
            return StealthResult(
                success=False,
                url=url,
                content="",
                stealth_config={},
                detection_bypassed=False,
                response_time=response_time,
                user_agent_used=custom_user_agent or "unknown",
                error=str(e)
            )
    
    async def test_stealth_levels(self, url: str) -> Dict[int, StealthResult]:
        """
        Test all stealth levels against a target URL
        """
        self.logger.info(f"🧪 Testing all stealth levels against: {url}")
        results = {}
        
        for level in range(1, 6):
            self.logger.info(f"\n📊 Testing stealth level {level}: {self.stealth_levels[level]}")
            result = await self.stealth_crawl(url, stealth_level=level)
            results[level] = result
            
            # Wait between tests to avoid rate limiting
            await asyncio.sleep(2)
        
        return results
    
    async def benchmark_stealth(self, benchmark_url: str = "https://www.magazineluiza.com.br/celulares-e-smartphones/l/te/") -> Dict[str, Any]:
        """
        Benchmark stealth capabilities against the Magazine Luiza target
        """
        self.logger.info(f"🎯 Benchmarking stealth against: {benchmark_url}")
        
        # Test maximum stealth
        result = await self.stealth_crawl(benchmark_url, stealth_level=5)
        
        benchmark_report = {
            "target_url": benchmark_url,
            "stealth_level_used": 5,
            "success": result.success,
            "detection_bypassed": result.detection_bypassed,
            "response_time": result.response_time,
            "content_size": len(result.content),
            "stealth_features": result.stealth_config,
            "user_agent": result.user_agent_used,
            "timestamp": time.time(),
            "error": result.error
        }
        
        # Analyze content for success indicators
        if result.success and result.content:
            content_lower = result.content.lower()
            success_indicators = {
                "has_products": any(word in content_lower for word in ['celular', 'smartphone', 'produto', 'preco', 'price']),
                "no_captcha": 'captcha' not in content_lower,
                "no_block_message": 'bloqueado' not in content_lower and 'blocked' not in content_lower,
                "content_length": len(result.content)
            }
            benchmark_report["success_indicators"] = success_indicators
        
        self.logger.info(f"📈 Benchmark completed: {'SUCCESS' if result.detection_bypassed else 'DETECTED'}")
        return benchmark_report

# Export the main class
__all__ = ["Crawl4AIStealthEngine", "StealthResult"]

# CLI functionality
async def main():
    """CLI interface for stealth testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Crawl4AI Definitive Stealth Engine")
    parser.add_argument("url", help="URL to crawl")
    parser.add_argument("--level", type=int, default=5, choices=[1,2,3,4,5], 
                       help="Stealth level (1-5)")
    parser.add_argument("--benchmark", action="store_true", 
                       help="Run benchmark against Magazine Luiza")
    parser.add_argument("--test-all-levels", action="store_true",
                       help="Test all stealth levels")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    engine = Crawl4AIStealthEngine()
    
    if args.benchmark:
        result = await engine.benchmark_stealth(args.url)
        print("\n🎯 STEALTH BENCHMARK RESULTS")
        print("=" * 50)
        print(json.dumps(result, indent=2))
        
    elif args.test_all_levels:
        results = await engine.test_stealth_levels(args.url)
        print("\n🧪 STEALTH LEVEL COMPARISON")
        print("=" * 50)
        for level, result in results.items():
            status = "✅ SUCCESS" if result.detection_bypassed else "❌ DETECTED"
            print(f"Level {level}: {status} ({result.response_time:.2f}s)")
        
    else:
        result = await engine.stealth_crawl(args.url, stealth_level=args.level)
        print("\n🥷 STEALTH CRAWL RESULTS")
        print("=" * 50)
        print(f"Success: {result.success}")
        print(f"Detection Bypassed: {result.detection_bypassed}")
        print(f"Response Time: {result.response_time:.2f}s")
        print(f"Content Size: {len(result.content)} chars")
        if result.error:
            print(f"Error: {result.error}")
    
    if args.output:
        with open(args.output, 'w') as f:
            if args.test_all_levels:
                json.dump({k: result.__dict__ for k, result in results.items()}, f, indent=2)
            else:
                json.dump(result.__dict__ if not args.benchmark else result, f, indent=2)
        print(f"💾 Results saved to {args.output}")

if __name__ == "__main__":
    print("🥷 Crawl4AI Definitive Stealth Engine - 0.7.x Compatible")
    print("=" * 60)
    asyncio.run(main())