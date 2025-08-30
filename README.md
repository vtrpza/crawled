# CRAWLED - AI-First Deep Web Scraping Platform

A comprehensive AI-first web scraping solution that demonstrates advanced capabilities of the Crawl4AI framework with **modern Svelte frontend** and **intelligent API backend**.

## 🚀 Features

### 🌐 **Modern Svelte Frontend**
- **Cutting-Edge UI**: Built with SvelteKit, Vite, and Tailwind CSS with cyberpunk aesthetics
- **AI-First Design**: Mandatory AI processing for intelligent content analysis
- **All 8 Scraping Modes**: Simple, Advanced, Extract, Batch, Media, Interactive, AI, and Ultimate Stealth
- **Real-time Integration**: Live connection to intelligent backend API
- **Responsive & Accessible**: Mobile-first design with WCAG compliance
- **Cyberpunk Theme**: Neon colors, animations, and futuristic styling
- **Component Architecture**: Modular Svelte components for scalability

**🔗 Access the web interface at: [http://localhost:3000](http://localhost:3000)**

### 🔧 CLI & Backend Features

### Core Crawling Capabilities
- **Simple Crawl**: Basic web scraping with markdown/HTML output
- **Advanced Crawl**: JavaScript execution, dynamic content loading
- **Content Extraction**: Keyword-based content filtering and extraction
- **Batch Processing**: Concurrent crawling of multiple URLs
- **Media Detection**: Image and video identification with download options
- **Interactive Q&A**: Question-answering based on crawled content
- **AI-Powered Analysis**: LLM-based content extraction and analysis with multiple provider support
- **🥷 Ultimate Stealth**: Anti-detection crawling with UndetectedAdapter, proxy rotation, and human simulation

### Technical Features
- ✅ Async/await architecture for performance
- ✅ Configurable concurrency limits
- ✅ Multiple output formats (JSON, Markdown, HTML)
- ✅ Error handling and logging
- ✅ File output support
- ✅ JavaScript injection capabilities
- ✅ Content filtering and chunking
- ✅ Media extraction and analysis
- ✅ **Advanced Stealth**: UndetectedAdapter, user agent randomization, proxy support, human behavior simulation
- ✅ **Anti-Detection**: Viewport randomization, rate limiting, JavaScript fingerprint spoofing
- ✅ **Graceful Fallbacks**: Automatic degradation when stealth features unavailable

## 📦 Installation & Setup

### 🌐 Svelte Frontend (Recommended)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt
pip install flask flask-cors

# 2. Install Crawl4AI setup (first time only)
crawl4ai-setup

# 3. Install Node.js dependencies for Svelte frontend
npm install

# 4. Start the complete stack
npm run dev              # Svelte Frontend (Terminal 1) - http://localhost:3000
python api_server.py     # Backend API (Terminal 2) - http://localhost:5000
```

**🎉 That's it! Open [http://localhost:3000](http://localhost:3000) to experience the modern Svelte interface.**

### 🔧 CLI Only Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Crawl4AI setup (first time only)
crawl4ai-setup

# Make the script executable
chmod +x crawl4ai_poc.py
```

### AI Provider Setup (Optional)

The AI command supports multiple LLM providers. Choose based on your needs:

**🆓 Free Options:**
- **Ollama**: Install locally for free AI analysis
  ```bash
  # Install Ollama (macOS/Linux)
  curl -fsSL https://ollama.ai/install.sh | sh
  # Pull a model
  ollama pull llama3.2
  ```

**☁️ Cloud Providers (Require API Keys):**
- **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Google Gemini**: Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey)  
- **Groq**: Get API key from [Groq Console](https://console.groq.com/keys)
- **Anthropic**: Get API key from [Anthropic Console](https://console.anthropic.com/)

**Usage Examples:**
```bash
# Free with Ollama (local)
python crawl4ai_poc.py ai https://example.com --instruction "Summarize this"

# With API key
python crawl4ai_poc.py ai https://example.com --instruction "Analyze this" --provider "openai/gpt-4o" --api-token "your-key"
```

## 🎯 Usage

### 🌐 Web Interface Usage

1. **Start both servers** (frontend + backend):
```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend API
python api_server.py
```

2. **Open your browser** to [http://localhost:3000](http://localhost:3000)

3. **Select a crawling mode**:
   - **Simple**: Basic web scraping
   - **Advanced**: JavaScript execution and dynamic content
   - **Extract**: Keyword-based content extraction
   - **Batch**: Multiple URLs with concurrent processing
   - **Media**: Extract images, videos, and downloadable content
   - **Interactive**: Handle dynamic content with user interactions
   - **AI**: Intelligent content extraction with AI analysis
   - **🥷 Ultimate Stealth**: Military-grade anti-detection crawling

4. **Fill in the form** with your target URL and options

5. **Click "Start Crawl"** and watch real-time results appear!

**🎨 Features of the Web Interface:**
- Real-time crawl progress and results
- Responsive design that works on mobile
- Stealth mode indicators and special UI themes
- Live metadata display (word count, links found, images, etc.)
- Error handling with helpful suggestions
- Modern animations and smooth interactions

### 🔧 CLI Usage Examples

### 1. Simple Web Scraping
```bash
# Basic crawl with markdown output
python crawl4ai_poc.py simple https://example.com

# Save to file
python crawl4ai_poc.py simple https://example.com --output results.md

# HTML output format
python crawl4ai_poc.py simple https://example.com --format html
```

### 2. Advanced Scraping with JavaScript
```bash
# Dynamic content with default JS and wait time
python crawl4ai_poc.py advanced https://spa-site.com --wait 5

# Custom JavaScript injection
python crawl4ai_poc.py advanced https://site.com --js "document.querySelector('.load-more').click();"

# Save advanced results
python crawl4ai_poc.py advanced https://dynamic-site.com --output advanced_results.json
```

**Note**: The `--wait` parameter specifies seconds to wait after JavaScript execution before capturing the final HTML.

### 3. Content Extraction
```bash
# Extract content about specific topics
python crawl4ai_poc.py extract https://news-site.com --query "artificial intelligence"

# Multi-keyword extraction
python crawl4ai_poc.py extract https://tech-blog.com --query "python programming tutorial"

# Save extraction results
python crawl4ai_poc.py extract https://docs-site.com --query "API documentation" --output extraction.json
```

### 4. Batch Processing
```bash
# Crawl multiple URLs with default concurrency
python crawl4ai_poc.py batch https://site1.com https://site2.com https://site3.com

# Control concurrency
python crawl4ai_poc.py batch https://site1.com https://site2.com --concurrent 5

# Save batch results
python crawl4ai_poc.py batch https://site1.com https://site2.com --output batch_results.json
```

### 5. Media-Aware Crawling
```bash
# Detect images and videos
python crawl4ai_poc.py media https://gallery-site.com

# Enable downloads (POC level)
python crawl4ai_poc.py media https://media-site.com --images --videos

# Save media analysis
python crawl4ai_poc.py media https://portfolio.com --output media_analysis.json
```

### 6. Interactive Q&A
```bash
# Ask questions about content
python crawl4ai_poc.py interactive https://docs.python.org --question "How to install Python?"

# Technical documentation Q&A
python crawl4ai_poc.py interactive https://api-docs.com --question "What are the rate limits?"

# Save Q&A results
python crawl4ai_poc.py interactive https://faq-site.com --question "troubleshooting" --output qa_results.json
```

### 7. Ultimate Stealth Crawling
```bash
# Maximum stealth mode with all anti-detection features
python crawl4ai_poc.py stealth https://protected-site.com

# Stealth with proxy rotation
python crawl4ai_poc.py stealth https://bot-detection.com --proxy-list "proxy1:8080,proxy2:3128:user:pass"

# Custom user agent and timing
python crawl4ai_poc.py stealth https://anti-bot.com --user-agent firefox --delay-min 3.0 --delay-max 6.0

# Visible mode for debugging (less stealthy)
python crawl4ai_poc.py stealth https://site.com --visible --no-human-simulation

# Add stealth to any existing command
python crawl4ai_poc.py simple https://example.com --stealth
python crawl4ai_poc.py advanced https://spa-site.com --stealth --wait 5
python crawl4ai_poc.py ai https://news.com --instruction "Summarize" --stealth

# Save stealth results
python crawl4ai_poc.py stealth https://protected-api.com --output stealth_results.json
```

**🥷 Stealth Features Included:**
- ✅ **UndetectedAdapter**: Maximum anti-detection with undetected-chromedriver
- ✅ **User Agent Randomization**: Rotates between realistic browser signatures
- ✅ **Viewport Randomization**: Random screen resolutions to avoid fingerprinting
- ✅ **Human Behavior Simulation**: Mouse movements, scrolling, and realistic delays
- ✅ **Proxy Rotation**: Support for HTTP/HTTPS proxies with authentication
- ✅ **Rate Limiting**: Configurable delays to mimic human browsing patterns
- ✅ **Headless Mode**: Invisible crawling for maximum stealth
- ✅ **JavaScript Anti-Detection**: Advanced browser fingerprint spoofing
- ✅ **Graceful Fallback**: Automatic fallback to standard mode if stealth fails

### 8. AI-Powered Analysis
```bash
# Free AI analysis with Ollama (requires local Ollama installation)
python crawl4ai_poc.py ai https://news-article.com --instruction "Summarize the main points and key takeaways"

# OpenAI GPT-4 analysis
python crawl4ai_poc.py ai https://research-paper.com --instruction "Extract methodology and conclusions" --provider "openai/gpt-4o" --api-token "sk-your-openai-token"

# Google Gemini analysis
python crawl4ai_poc.py ai https://tech-blog.com --instruction "Identify trends and predictions" --provider "gemini/gemini-1.5-pro" --api-token "your-gemini-api-key"

# Groq fast inference
python crawl4ai_poc.py ai https://documentation.com --instruction "Create a step-by-step guide" --provider "groq/llama3-70b-8192" --api-token "your-groq-api-key"

# Anthropic Claude analysis
python crawl4ai_poc.py ai https://long-article.com --instruction "Analyze arguments and provide counterpoints" --provider "anthropic/claude-3-5-sonnet" --api-token "your-anthropic-key"

# Save AI analysis results
python crawl4ai_poc.py ai https://content-site.com --instruction "Extract key insights" --provider "openai/gpt-4o-mini" --api-token "your-key" --output ai_analysis.json
```

## 🏗️ Architecture Overview

### Frontend Architecture (Svelte)

1. **SvelteKit Application**
   - Modern reactive frontend with component-based architecture
   - Vite build system for fast development and optimized production
   - Tailwind CSS with custom cyberpunk design system
   - TypeScript support for type safety

2. **Component Structure**
   - `AppEnhanced.svelte`: Main application component
   - `CrawlForm.svelte`: Interactive crawling configuration
   - `Results.svelte`: Real-time results display with animations
   - Modular design for easy maintenance and scaling

3. **Styling & Theme**
   - Cyberpunk aesthetic with neon colors (cyan, pink, lime)
   - Custom animations: fade-in, slide-up, cyber-pulse, glitch effects
   - Responsive design with mobile-first approach
   - Custom font stacks including JetBrains Mono and Orbitron

### Backend Architecture (Python)

1. **Crawl4AIPOCTool Class**
   - Main orchestrator for all crawling operations
   - Handles configuration and result processing
   - Provides unified interface for different crawling modes

2. **Async Methods**
   - `simple_crawl()`: Basic scraping with format options
   - `advanced_crawl_with_js()`: Dynamic content handling
   - `crawl_with_extraction()`: Content filtering and extraction
   - `batch_crawl()`: Concurrent multi-URL processing
   - `crawl_with_media_download()`: Media detection and analysis
   - `interactive_crawl()`: Q&A content processing
   - `stealth_crawl()`: Ultimate anti-detection crawling
   - `ai_powered_crawl()`: LLM-based content analysis

3. **API Server (Flask)**
   - RESTful API endpoints for frontend integration
   - CORS enabled for cross-origin requests
   - Real-time processing with async support
   - Error handling and response formatting

### Data Flow
```
Svelte Frontend → Flask API → Crawl4AI → Processing → JSON Response
    ↓                ↓           ↓            ↓            ↓
[User Input] → [HTTP Request] → [Configuration] → [Content Analysis] → [Live Results]
```

## 🔧 Configuration Options

### JavaScript Execution
- Custom JS code injection
- Wait time configuration
- Dynamic content loading
- Interactive element handling

### Content Processing
- Markdown generation
- HTML cleaning
- Content chunking
- Keyword-based filtering

### Output Management
- Multiple format support (JSON, Markdown, HTML)
- File saving capabilities
- Structured result organization
- Error reporting

## 📊 Output Examples

### Simple Crawl Output
```json
{
  "status": "success",
  "url": "https://example.com",
  "title": "Example Domain",
  "content": "# Example Domain\n\nThis domain is for use in examples...",
  "links": [...],
  "media": {...},
  "metadata": {...}
}
```

### Batch Crawl Results
```json
{
  "status": "completed",
  "total_urls": 3,
  "successful": 2,
  "failed": 1,
  "results": [...]
}
```

### Interactive Q&A Output
```json
{
  "status": "success",
  "url": "https://docs-site.com",
  "question": "How to install?",
  "answer_candidate": [
    "Installation is simple with pip install package-name.",
    "To install, download the installer and run setup.exe.",
    "System requirements include Python 3.8 or higher."
  ],
  "confidence": "simulated_poc_level"
}
```

## 🚨 Limitations & POC Notes

This is a **proof-of-concept** demonstration with the following limitations:

1. **Q&A Functionality**: Uses simple keyword matching, not LLM integration
2. **Media Downloads**: Detection only, actual downloading not implemented
3. **Error Recovery**: Basic error handling, not production-ready
4. **Content Extraction**: Regex-based, not semantic understanding
5. **Performance**: Not optimized for large-scale operations

## 🔮 Future Enhancements

- [ ] LLM integration for intelligent Q&A
- [ ] Real media download functionality
- [ ] Advanced content extraction with semantic analysis
- [ ] Database storage for crawl results
- [ ] Web UI interface
- [ ] Scheduled crawling capabilities
- [ ] Advanced authentication handling
- [ ] Content deduplication
- [ ] Performance monitoring and metrics

## 🛠️ Development

### Prerequisites
- Python 3.8+
- Crawl4AI framework
- Modern web browser (for dynamic content)

### Testing
```bash
# Test simple functionality
python crawl4ai_poc.py simple https://httpbin.org/html

# Test advanced features
python crawl4ai_poc.py advanced https://httpbin.org/delay/2 --wait 3

# Test extraction
python crawl4ai_poc.py extract https://httpbin.org/html --query "Herman Melville"
```

## 📝 License

This POC is open source and free to use for educational and research purposes.

## 🤝 Contributing

This is a proof-of-concept. For production use, consider:
- Adding comprehensive error handling
- Implementing proper logging
- Adding configuration file support
- Creating unit tests
- Optimizing performance for large-scale use

---

**Built with Crawl4AI** - The most advanced web scraping framework for AI applications.