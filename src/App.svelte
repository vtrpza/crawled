<script>
  import Header from './components/Header.svelte'
  import SearchInterface from './components/SearchInterface.svelte'
  import TerminalLogs from './components/TerminalLogs.svelte'
  import BatchProgress from './components/BatchProgress.svelte'
  import Results from './components/Results.svelte'
  
  let isProcessing = $state(false)
  let results = $state(null)
  let batchProgress = $state(null)
  let terminalLogs = $state([])
  let apiKey = $state(localStorage.getItem('crawl4ai_api_key') || null)
  let hasPromptedForApiKey = $state(false)
  
  $effect(() => {
    if (!hasPromptedForApiKey && !apiKey) {
      hasPromptedForApiKey = true
      promptForApiKey()
    }
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
        console.log('✅ API key configured successfully')
      } else {
        console.log('ℹ️ Basic extraction mode enabled (no AI key provided)')
      }
    }, 500)
  }
  
  function addTerminalLog(message, level = 'info') {
    const timestamp = new Date().toLocaleTimeString()
    terminalLogs = [...terminalLogs, { message, level, timestamp }]
    
    // Keep only last 50 logs
    if (terminalLogs.length > 50) {
      terminalLogs = terminalLogs.slice(1)
    }
  }
  
  function clearLogs() {
    terminalLogs = []
  }
  
  async function handleSubmit(formData) {
    isProcessing = true
    results = null
    batchProgress = null
    
    addTerminalLog('Initiating neural crawl sequence...', 'info')
    
    try {
      addTerminalLog(`Target acquired: ${formData.url || formData.urls?.join(', ')}`, 'info')
      addTerminalLog(`Protocol: ${formData.intent?.toUpperCase()} | Stealth: ${formData.stealth ? 'ENABLED' : 'DISABLED'}`, 'info')
      
      // Handle batch mode with progress tracking
      if (formData.urls && formData.urls.length > 1) {
        await handleBatchProcessing(formData)
      } else {
        // Single URL processing
        const result = await callSmartBackend(formData)
        results = result
        
        if (result.status === 'success') {
          addTerminalLog('Neural extraction completed successfully', 'success')
        } else {
          addTerminalLog(`Extraction failed: ${result.error}`, 'error')
        }
      }
    } catch (error) {
      results = {
        status: 'error',
        error: error.message,
        suggestion: 'Check your URL and options, then try again'
      }
      addTerminalLog(`Critical error: ${error.message}`, 'error')
    } finally {
      isProcessing = false
    }
  }
  
  async function handleBatchProcessing(formData) {
    const urls = formData.urls
    const total = urls.length
    let completed = 0
    let failed = 0
    const batchResults = []
    
    batchProgress = {
      total,
      completed: 0,
      current: null,
      failed: 0,
      progress: 0
    }
    
    addTerminalLog(`Batch operation initialized: ${total} targets`, 'info')
    
    for (let i = 0; i < urls.length; i++) {
      const url = urls[i]
      
      // Update progress
      batchProgress = {
        ...batchProgress,
        current: url,
        completed: i,
        progress: (i / total) * 100
      }
      
      addTerminalLog(`Processing target ${i + 1}/${total}: ${url}`, 'info')
      
      try {
        const singleData = { ...formData, url, urls: undefined }
        const result = await callSmartBackend(singleData)
        
        if (result.status === 'success') {
          batchResults.push(result)
          completed++
          addTerminalLog(`✓ Target ${i + 1} extracted successfully`, 'success')
        } else {
          failed++
          batchResults.push(result)
          addTerminalLog(`✗ Target ${i + 1} failed: ${result.error}`, 'error')
        }
      } catch (error) {
        failed++
        addTerminalLog(`✗ Target ${i + 1} error: ${error.message}`, 'error')
      }
      
      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 500))
    }
    
    // Final progress update
    batchProgress = {
      ...batchProgress,
      completed: completed,
      failed: failed,
      progress: 100,
      current: null
    }
    
    results = {
      status: 'success',
      batch_results: batchResults,
      batch_summary: {
        total,
        completed,
        failed,
        success_rate: ((completed / total) * 100).toFixed(1)
      }
    }
    
    addTerminalLog(`Batch operation completed: ${completed}/${total} successful (${failed} failed)`, completed > failed ? 'success' : 'error')
  }
  
  async function callSmartBackend(data) {
    try {
      const response = await fetch('http://localhost:5000/api/smart-crawl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
      
      const result = await response.json()
      
      if (!response.ok || result.status === 'error') {
        return {
          status: 'error',
          error: result.error || `HTTP error! status: ${response.status}`,
          timestamp: result.timestamp || new Date().toISOString()
        }
      }
      
      return {
        status: 'success',
        url: data.url,
        intent: data.intent,
        crawl_type: result.crawl_type || 'standard',
        
        // AI-Enhanced Deep Crawl specific fields
        instruction: result.instruction,
        strategy: result.strategy,
        pages_crawled: result.pages_crawled,
        pages_requested: result.pages_requested,
        max_depth: result.max_depth,
        ai_provider: result.ai_provider,
        ai_synthesis: result.ai_synthesis,
        individual_pages: result.individual_pages,
        total_content_length: result.total_content_length,
        
        // Backward compatibility
        content: result.content || result.ai_synthesis,
        metadata: result.metadata,
        extracted_content: result.extracted_content || result.ai_synthesis,
        ai_analysis: result.ai_analysis || result.ai_synthesis,
        batch_results: result.batch_results,
        media: result.media,
        discovered_urls: result.discovered_urls,
        avg_relevance_score: result.avg_relevance_score,
        timestamp: result.timestamp,
        performance: result.performance,
        
        stealth_features: result.stealth_features || (data.stealth ? [
          '🥷 Anti-detection patterns active',
          '🔄 Random user agent rotation', 
          '⏱️ Human-like delays',
          '🌐 Browser fingerprint masking',
          '🛡️ Behavioral mimicry'
        ] : null)
      }
      
    } catch (error) {
      return {
        status: 'error',
        error: error.message || 'Network error occurred',
        timestamp: new Date().toISOString()
      }
    }
  }
  
  function handleClear() {
    results = null
    batchProgress = null
  }
</script>

<div class="min-h-screen max-w-full overflow-x-hidden relative cyber-scanlines matrix-rain" style="background: #000000 !important; background-color: #000000 !important; max-height: 100vh; overflow-y: auto;">
  <Header />
  
  <div class="max-w-4xl mx-auto px-6 sm:px-8 lg:px-10">
    <SearchInterface 
      {isProcessing} 
      {apiKey}
      onSubmit={handleSubmit}
      onClear={handleClear}
    />
    
    {#if batchProgress}
      <BatchProgress {batchProgress} />
    {/if}
    
    {#if terminalLogs.length > 0}
      <TerminalLogs logs={terminalLogs} onClear={clearLogs} />
    {/if}
    
    {#if results}
      <Results {results} />
    {/if}
  </div>
</div>