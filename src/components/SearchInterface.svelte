<script>
  import SmartRequirements from './SmartRequirements.svelte'
  import ExtractionIntelligence from './ExtractionIntelligence.svelte'
  import CoreOptions from './CoreOptions.svelte'
  import { quickActions, patterns, intelligentSuggestions, smartRequirements } from '../lib/config.js'
  
  let { isProcessing = false, apiKey = null, onSubmit, onClear } = $props()
  
  let currentUrl = $state('')
  let extractionQuery = $state('')
  let aiModel = $state('groq')  // Default to Groq for AI-first experience
  let outputFormat = $state('markdown')
  let enableCache = $state(true)
  let includeMedia = $state(false)
  let batchUrls = $state('')
  let concurrent = $state(5)
  let smartRequirementsData = $state({})
  
  // AI-First Deep Crawl parameters (new)
  let maxPages = $state(5)
  let maxDepth = $state(2)
  let crawlStrategy = $state('bfs')
  
  // Use derived for computed values to avoid infinite loops
  const detectedIntent = $derived(currentUrl ? detectIntent(currentUrl) : null)
  const suggestions = $derived(
    currentUrl && detectedIntent 
      ? generateSuggestions(currentUrl, detectedIntent) 
      : []
  )
  
  function detectIntent(url) {
    if (!url) return null
    
    for (const [type, pattern] of Object.entries(patterns)) {
      if (pattern.test(url)) {
        const action = Object.values(quickActions).find(a => a.settings.intent === type)
        return {
          type,
          icon: action?.icon || '🌐',
          color: action?.color || 'blue',
          confidence: 0.8
        }
      }
    }
    
    return {
      type: 'general',
      icon: '🌐', 
      color: 'blue',
      confidence: 0.5
    }
  }
  
  function generateSuggestions(url, intent) {
    if (!url || !intent) return []
    
    const suggestions = []
    
    switch (intent.type) {
      case 'article':
        suggestions.push(
          'Extract main article content',
          'Get author and publication date',
          'Find related articles'
        )
        break
      case 'social':
        suggestions.push(
          'Capture infinite scroll content',
          'Extract post metadata',
          'Get user profiles'
        )
        break
      case 'ecommerce':
        suggestions.push(
          'Extract product information',
          'Get pricing and availability',
          'Find customer reviews'
        )
        break
      default:
        suggestions.push(
          'Extract all text content',
          'Find downloadable resources',
          'Get page structure'
        )
    }
    
    return suggestions.slice(0, 3)
  }
  
  function handleSubmit() {
    if (!currentUrl) return
    
    const intent = detectedIntent || { type: 'general' }
    const currentIntent = intent.type
    
    // Base data
    const data = {
      url: currentUrl,
      mode: 'intelligent',
      intent: currentIntent,
      detected_intent: intent,
      urls: undefined,
      smart_requirements: smartRequirementsData
    }
    
    // AI is now MANDATORY - always enabled
    let finalAiModel = aiModel || 'groq'  // Default to Groq if somehow not set
    
    // Stealth is always enabled at high level
    data.stealth = true
    data.stealth_level = currentIntent === 'stealth' ? 8 : 4
    data.timeout = 30
    data.enable_cache = enableCache
    data.extraction_query = extractionQuery || `Extract and analyze comprehensive information about ${currentIntent}. Provide detailed insights and actionable information.`
    data.output_format = outputFormat
    data.include_media = includeMedia
    
    // AI-First Deep Crawl parameters (MANDATORY)
    data.max_pages = maxPages
    data.max_depth = maxDepth
    data.strategy = crawlStrategy
    
    // AI Integration - MANDATORY, always enabled
    data.ai_extraction = {
      api_key: apiKey,
      model: finalAiModel,
      query: data.extraction_query,
      enabled: true  // Always enabled
    }
    
    console.log(`🤖 AI-First Deep Crawl: model=${finalAiModel}, pages=${maxPages}, depth=${maxDepth}, strategy=${crawlStrategy.toUpperCase()}`)
    console.log(`📝 Extraction query: "${data.extraction_query}"`)
    
    if (finalAiModel === 'ollama' && !apiKey) {
      console.log('Using Ollama (local AI) - no API key required')
    } else if (!apiKey && finalAiModel !== 'ollama') {
      console.log('⚠️ No API key provided - will attempt free tier or fallback')
    }
    
    // Handle batch mode specially
    if (currentIntent === 'batch') {
      const urls = batchUrls.split('\n').filter(url => url.trim()).map(url => url.trim())
      data.urls = urls
      data.concurrent = concurrent
    }
    
    onSubmit(data)
  }
  
  function handleClear() {
    currentUrl = ''
    // detectedIntent and suggestions are derived, will auto-update when currentUrl changes
    extractionQuery = ''
    aiModel = ''
    outputFormat = 'markdown'
    enableCache = true
    includeMedia = false
    batchUrls = ''
    concurrent = 5
    smartRequirementsData = {}
    
    if (onClear) onClear()
  }
  
  function handleKeyDown(event) {
    if (event.key === 'Enter') {
      event.preventDefault()
      handleSubmit()
    }
  }
</script>

<div class="cyber-card p-10 mb-10 animate-scale-in relative">
  <div class="absolute top-3 left-6 text-xs font-mono text-neon-cyan/70">
    [ NEURAL SEARCH MODULE ]
  </div>
  
  <div class="relative mb-8 mt-6">
    <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
      <span class="text-2xl filter drop-shadow-lg">{detectedIntent?.icon || '🌐'}</span>
    </div>
    <input 
      type="url" 
      placeholder="// INSERT TARGET URL FOR NEURAL EXTRACTION..." 
      bind:value={currentUrl}
      onkeydown={handleKeyDown}
      class="cyber-input w-full pl-16 pr-4 py-4 text-lg font-mono"
    />
    {#if currentUrl && detectedIntent}
      <div class="absolute inset-y-0 right-0 pr-4 flex items-center">
        <span class="px-2 py-1 bg-neon-{detectedIntent.color}/20 text-neon-{detectedIntent.color} text-xs font-mono border border-neon-{detectedIntent.color}/50 rounded animate-pulse">
          {detectedIntent.type.toUpperCase()}_DETECTED
        </span>
      </div>
    {/if}
  </div>
  
  
  {#if currentUrl && detectedIntent}
    <SmartRequirements 
      intent={detectedIntent} 
      bind:requirementsData={smartRequirementsData}
    />
  {/if}
  
  <div class="pt-6 {currentUrl && detectedIntent ? '' : 'border-t border-neon-cyan/30'}">
    <div class="text-sm font-mono text-neon-cyan mb-4 flex items-center gap-2">
      <span class="text-neon-lime">»</span> EXTRACTION_INTELLIGENCE:
    </div>
    <ExtractionIntelligence 
      intent={detectedIntent || { type: 'general' }}
      bind:extractionQuery
    />
  </div>
  
  <div class="pt-6 border-t border-neon-cyan/30">
    <div class="text-sm font-mono text-neon-cyan mb-5 flex items-center gap-2">
      <span class="text-neon-pink">»</span> CORE_OPTIONS:
    </div>
    <CoreOptions 
      intent={detectedIntent || { type: 'general' }}
      bind:aiModel
      bind:outputFormat
      bind:enableCache
      bind:includeMedia
      bind:batchUrls
      bind:concurrent
      bind:maxPages
      bind:maxDepth
      bind:crawlStrategy
    />
  </div>
  
  <div class="flex items-center justify-end pt-6 border-t border-neon-cyan/30">
    <div class="flex gap-4">
      <button 
        type="button" 
        onclick={handleClear}
        class="cyber-btn-secondary px-8 py-3 font-mono"
      >
        PURGE
      </button>
      <button 
        type="submit" 
        onclick={handleSubmit}
        class="cyber-btn-primary px-10 py-3 font-mono {isProcessing ? 'opacity-50 cursor-not-allowed' : ''}"
        disabled={isProcessing}
      >
        {#if isProcessing}
          <span class="inline-flex items-center gap-2">
            <div class="w-4 h-4 border-2 border-neon-cyan/30 border-t-neon-cyan rounded-full animate-spin"></div>
            PROCESSING...
          </span>
        {:else}
          <span class="inline-flex items-center gap-2">🚀 INITIATE_CRAWL</span>
        {/if}
      </button>
    </div>
  </div>
</div>