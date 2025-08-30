<script>
  import Header from './components/Header.svelte'
  import SearchInterface from './components/SearchInterface.svelte'
  import TerminalLogs from './components/TerminalLogs.svelte'
  import BatchProgress from './components/BatchProgress.svelte'
  import ResultsEnhanced from './components/ResultsEnhanced.svelte'
  import CrawlHistory from './components/CrawlHistory.svelte'
  import ResultViewer from './components/ResultViewer.svelte'
  
  let isProcessing = $state(false)
  let results = $state(null)
  let batchProgress = $state(null)
  let terminalLogs = $state([])
  let apiKey = $state(localStorage.getItem('crawl4ai_api_key') || null)
  let hasPromptedForApiKey = $state(false)
  
  // Enhanced state for database features
  let showHistory = $state(false)
  let showResultViewer = $state(false)
  let selectedResultId = $state(null)
  let databaseStatus = $state('unknown')
  
  $effect(() => {
    if (!hasPromptedForApiKey && !apiKey) {
      hasPromptedForApiKey = true
      promptForApiKey()
    }
    
    // Check database status on load
    checkDatabaseStatus()
  })
  
  function promptForApiKey() {
    setTimeout(() => {
      const key = prompt(
        '🤖 CRAWLED AI SETUP\n\n' +
        'Enter your AI API Key (OpenAI/Claude/Gemini) for enhanced extraction:\n\n' +
        '• Optional but recommended for better results\n' +
        '• Leave empty to use basic extraction only\n' +
        '• Key will be stored locally and securely\n\n' +
        'API Key:'
      )
      
      if (key && key.trim()) {
        apiKey = key.trim()
        localStorage.setItem('crawl4ai_api_key', apiKey)
        addTerminalLog('✅ API key configured successfully', 'success')
      } else {
        addTerminalLog('ℹ️ Basic extraction mode enabled (no AI key provided)', 'info')
      }
    }, 500)
  }
  
  // Check database status
  async function checkDatabaseStatus() {
    try {
      const response = await fetch('/api/health')
      const data = await response.json()
      
      if (data.database && data.database.includes('healthy')) {
        databaseStatus = 'healthy'
        addTerminalLog('📊 Database connection: HEALTHY', 'success')
      } else {
        databaseStatus = 'unhealthy'
        addTerminalLog('📊 Database connection: UNHEALTHY', 'warning')
      }
    } catch (error) {
      databaseStatus = 'error'
      addTerminalLog('📊 Database connection: ERROR', 'error')
    }
  }
  
  function addTerminalLog(message, level = 'info') {
    const timestamp = new Date().toLocaleTimeString()
    terminalLogs = [...terminalLogs, { message, level, timestamp }]
    
    // Keep only last 50 logs
    if (terminalLogs.length > 50) {
      terminalLogs = terminalLogs.slice(1)
    }
  }
  
  function handleCrawlStart() {
    isProcessing = true
    results = null
    batchProgress = null
    addTerminalLog('🚀 Initializing crawl operation...', 'info')
  }

  async function handleCrawlSubmit(data) {
    handleCrawlStart()
    
    try {
      // Process the crawl request with the provided data
      addTerminalLog(`🔍 Starting crawl for: ${data.url}`, 'info')
      addTerminalLog(`⚙️ Mode: ${data.mode}, Intent: ${data.intent}`, 'info')
      
      // Make the actual API call
      const response = await fetch('/api/crawl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
      
      if (response.ok) {
        const result = await response.json()
        handleCrawlComplete({ detail: result })
        addTerminalLog('✅ Crawl completed successfully', 'success')
      } else {
        const error = await response.json()
        addTerminalLog(`❌ Crawl failed: ${error.error || 'Unknown error'}`, 'error')
        isProcessing = false
      }
    } catch (error) {
      addTerminalLog(`❌ Network error: ${error.message}`, 'error')
      isProcessing = false
    }
  }

  function handleCrawlClear() {
    results = null
    batchProgress = null
    addTerminalLog('🧹 Interface cleared', 'info')
  }
  
  function handleCrawlProgress(event) {
    batchProgress = event.detail
    
    if (batchProgress.status === 'processing') {
      addTerminalLog(`📊 Batch progress: ${batchProgress.completed}/${batchProgress.total} completed`, 'info')
    }
  }
  
  function handleCrawlComplete(event) {
    isProcessing = false
    results = event.detail
    batchProgress = null
    
    const status = results.status === 'success' ? 'success' : 'error'
    const emoji = results.status === 'success' ? '✅' : '❌'
    
    if (results.status === 'success') {
      // Enhanced logging with database info
      addTerminalLog(`${emoji} Crawl completed successfully`, status)
      
      if (results.database?.result_id) {
        addTerminalLog(`📊 Result stored in database (ID: ${results.database.result_id.slice(0, 8)}...)`, 'success')
      }
      
      if (results.ai_analysis || results.ai_synthesis) {
        addTerminalLog('🤖 AI analysis completed', 'success')
      }
      
      if (results.pages_crawled && results.pages_crawled > 1) {
        addTerminalLog(`📄 ${results.pages_crawled} pages processed`, 'info')
      }
      
      if (results.performance?.database_stored) {
        addTerminalLog('💾 Results persisted to database for future access', 'success')
      }
    } else {
      addTerminalLog(`${emoji} Crawl failed: ${results.error}`, status)
      
      if (results.result_id) {
        addTerminalLog(`📊 Error logged in database (ID: ${results.result_id.slice(0, 8)}...)`, 'info')
      }
    }
  }
  
  function handleApiKeyChange(event) {
    const newKey = event.detail?.apiKey
    if (newKey && newKey !== apiKey) {
      apiKey = newKey
      localStorage.setItem('crawl4ai_api_key', apiKey)
      addTerminalLog('✅ API key updated successfully', 'success')
    } else if (!newKey && apiKey) {
      apiKey = null
      localStorage.removeItem('crawl4ai_api_key')
      addTerminalLog('ℹ️ API key removed - using basic extraction mode', 'info')
    }
  }
  
  // Enhanced event handlers for database features
  function handleViewHistory() {
    showHistory = true
    addTerminalLog('📊 Opening crawl history...', 'info')
  }
  
  function handleCloseHistory() {
    showHistory = false
  }
  
  function handleViewResult(event) {
    selectedResultId = event.detail.resultId
    showResultViewer = true
    showHistory = false
    addTerminalLog(`🔍 Loading result: ${selectedResultId.slice(0, 8)}...`, 'info')
  }
  
  function handleCloseResultViewer() {
    showResultViewer = false
    selectedResultId = null
  }
  
  // Handle result component events
  function handleResultsEvent(event) {
    switch (event.type) {
      case 'viewResult':
        handleViewResult(event)
        break
      case 'viewHistory':
        handleViewHistory()
        break
      default:
        console.log('Unhandled results event:', event.type, event.detail)
    }
  }
  
  // Handle history component events  
  function handleHistoryEvent(event) {
    switch (event.type) {
      case 'viewResult':
        handleViewResult(event)
        break
      case 'close':
        handleCloseHistory()
        break
      default:
        console.log('Unhandled history event:', event.type, event.detail)
    }
  }
  
  // Handle result viewer events
  function handleResultViewerEvent(event) {
    switch (event.type) {
      case 'close':
        handleCloseResultViewer()
        break
      default:
        console.log('Unhandled result viewer event:', event.type, event.detail)
    }
  }
</script>

<main class="min-h-screen bg-gradient-to-br from-cyber-dark via-black to-cyber-dark text-white overflow-x-hidden">
  <!-- Animated background elements -->
  <div class="fixed inset-0 pointer-events-none">
    <div class="absolute top-20 left-10 w-2 h-2 bg-neon-cyan rounded-full animate-pulse"></div>
    <div class="absolute top-40 right-20 w-1 h-1 bg-neon-green rounded-full animate-ping"></div>
    <div class="absolute bottom-32 left-1/4 w-1 h-1 bg-neon-purple rounded-full animate-pulse"></div>
    <div class="absolute top-1/2 right-10 w-2 h-2 bg-neon-red rounded-full animate-ping"></div>
    <div class="absolute bottom-20 right-1/3 w-1 h-1 bg-neon-yellow rounded-full animate-pulse"></div>
  </div>

  <div class="relative z-10">
    <Header />
    
    <!-- Database Status Banner -->
    {#if databaseStatus === 'healthy'}
      <div class="bg-neon-green/10 border-b border-neon-green/30 px-6 py-2">
        <div class="max-w-6xl mx-auto flex items-center gap-3">
          <span class="text-neon-green">📊</span>
          <span class="font-mono text-sm text-neon-green">DATABASE_CONNECTED - Results are being persistently stored</span>
          <button 
            on:click={handleViewHistory}
            class="ml-auto px-3 py-1 bg-neon-green/20 border border-neon-green/30 rounded font-mono text-xs text-neon-green hover:bg-neon-green/30 transition-colors"
          >
            VIEW_HISTORY
          </button>
        </div>
      </div>
    {:else if databaseStatus === 'unhealthy' || databaseStatus === 'error'}
      <div class="bg-neon-red/10 border-b border-neon-red/30 px-6 py-2">
        <div class="max-w-6xl mx-auto flex items-center gap-3">
          <span class="text-neon-red">⚠️</span>
          <span class="font-mono text-sm text-neon-red">DATABASE_OFFLINE - Results will not be persisted</span>
        </div>
      </div>
    {/if}

    <div class="max-w-6xl mx-auto px-6 py-12 space-y-12">
      <!-- Main Interface -->
      <SearchInterface 
        {isProcessing}
        {apiKey}
        onSubmit={handleCrawlSubmit}
        onClear={handleCrawlClear}
      />

      <!-- Batch Progress -->
      {#if batchProgress}
        <BatchProgress progress={batchProgress} />
      {/if}

      <!-- Results -->
      {#if results}
        <ResultsEnhanced 
          {results} 
          on:viewResult={handleResultsEvent}
          on:viewHistory={handleResultsEvent}
        />
      {/if}

      <!-- Terminal Logs -->
      {#if terminalLogs.length > 0}
        <TerminalLogs logs={terminalLogs} />
      {/if}
    </div>
  </div>
  
  <!-- History Modal -->
  <CrawlHistory 
    visible={showHistory}
    on:viewResult={handleHistoryEvent}
    on:close={handleHistoryEvent}
  />
  
  <!-- Result Viewer Modal -->
  <ResultViewer 
    visible={showResultViewer}
    resultId={selectedResultId}
    on:close={handleResultViewerEvent}
  />
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0a0a0a;
    color: #ffffff;
    overflow-x: hidden;
  }

  :global(.cyber-card) {
    background: linear-gradient(135deg, rgba(0, 255, 255, 0.05) 0%, rgba(0, 0, 0, 0.8) 100%);
    border: 1px solid rgba(0, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    position: relative;
  }

  :global(.cyber-card::before) {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(0, 255, 255, 0.5) 50%, transparent 100%);
  }

  :global(.neon-glow) {
    filter: drop-shadow(0 0 10px currentColor);
  }
  
  :global(.text-neon-cyan) { color: #00ffff; }
  :global(.text-neon-green) { color: #39ff14; }
  :global(.text-neon-purple) { color: #bf00ff; }
  :global(.text-neon-red) { color: #ff073a; }
  :global(.text-neon-yellow) { color: #ffff00; }
  
  :global(.bg-neon-cyan\/10) { background-color: rgba(0, 255, 255, 0.1); }
  :global(.bg-neon-cyan\/20) { background-color: rgba(0, 255, 255, 0.2); }
  :global(.bg-neon-cyan\/30) { background-color: rgba(0, 255, 255, 0.3); }
  
  :global(.border-neon-cyan\/30) { border-color: rgba(0, 255, 255, 0.3); }
  :global(.border-neon-green\/30) { border-color: rgba(57, 255, 20, 0.3); }
  :global(.border-neon-purple\/30) { border-color: rgba(191, 0, 255, 0.3); }
  :global(.border-neon-red\/30) { border-color: rgba(255, 7, 58, 0.3); }
  :global(.border-neon-yellow\/30) { border-color: rgba(255, 255, 0, 0.3); }
  
  :global(.bg-cyber-dark) { background-color: #0d1117; }
  :global(.bg-cyber-dark\/30) { background-color: rgba(13, 17, 23, 0.3); }
  :global(.bg-cyber-dark\/50) { background-color: rgba(13, 17, 23, 0.5); }
</style>