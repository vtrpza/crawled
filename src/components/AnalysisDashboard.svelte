<script>
  import { onMount } from 'svelte'
  
  let { results } = $props()
  
  // Computed dashboard metrics
  const dashboardMetrics = $derived(() => {
    if (!results || results.status !== 'success') return null
    
    const metrics = {
      // Basic extraction metrics
      contentLength: results.content?.length || 0,
      aiContentLength: results.ai_analysis?.length || results.extracted_content?.length || 0,
      title: results.title || 'No title',
      url: results.url,
      timestamp: results.timestamp,
      
      // Link analysis
      internalLinks: results.links?.internal?.length || 0,
      externalLinks: results.links?.external?.length || 0,
      discoveredUrls: results.discovered_urls?.length || 0,
      avgRelevanceScore: parseFloat(results.avg_relevance_score) || 0,
      
      // Media analysis
      images: results.media?.images?.length || 0,
      videos: results.media?.videos?.length || 0,
      audios: results.media?.audios?.length || 0,
      
      // Performance and quality metrics
      crawlType: results.crawl_type || 'standard',
      aiProvider: results.ai_provider,
      processingTime: results.performance?.total_time || 0,
      
      // Content quality indicators
      contentQuality: calculateContentQuality(results),
      extractionType: results.ai_analysis || results.extracted_content ? 'AI-Enhanced' : 'Standard',
      
      // Stealth features
      stealthActive: results.stealth_features?.length > 0 || Object.keys(results.stealth_features_v0_7 || {}).length > 0
    }
    
    return metrics
  })
  
  // Batch processing metrics
  const batchMetrics = $derived(() => {
    if (!results?.batch_results) return null
    
    const successful = results.batch_results.filter(r => r.status === 'success')
    const failed = results.batch_results.filter(r => r.status === 'error')
    
    return {
      total: results.batch_summary?.total || results.batch_results.length,
      successful: successful.length,
      failed: failed.length,
      successRate: parseFloat(results.batch_summary?.success_rate) || 0,
      
      // Aggregate content metrics
      totalContentExtracted: successful.reduce((sum, r) => sum + (r.content?.length || 0), 0),
      totalAiContent: successful.reduce((sum, r) => sum + (r.ai_analysis?.length || r.extracted_content?.length || 0), 0),
      avgProcessingTime: successful.reduce((sum, r) => sum + (r.performance?.total_time || 0), 0) / successful.length || 0,
      
      // Link discovery across batch
      totalLinksFound: successful.reduce((sum, r) => 
        sum + (r.links?.internal?.length || 0) + (r.links?.external?.length || 0), 0),
      totalMediaFound: successful.reduce((sum, r) => 
        sum + (r.media?.images?.length || 0) + (r.media?.videos?.length || 0), 0)
    }
  })
  
  function calculateContentQuality(result) {
    let score = 50 // Base score
    
    // AI analysis bonus
    if (result.ai_analysis || result.extracted_content) score += 20
    
    // Content length bonus
    const contentLength = result.content?.length || 0
    if (contentLength > 5000) score += 15
    else if (contentLength > 2000) score += 10
    else if (contentLength > 500) score += 5
    
    // Media discovery bonus
    const mediaCount = (result.media?.images?.length || 0) + (result.media?.videos?.length || 0)
    if (mediaCount > 10) score += 10
    else if (mediaCount > 3) score += 5
    
    // Link discovery bonus
    const linkCount = (result.links?.internal?.length || 0) + (result.links?.external?.length || 0)
    if (linkCount > 20) score += 10
    else if (linkCount > 5) score += 5
    
    // Relevance score bonus
    if (result.avg_relevance_score && parseFloat(result.avg_relevance_score) > 0.8) score += 15
    
    return Math.min(100, Math.max(0, score))
  }
  
  function formatBytes(bytes) {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }
  
  function formatDuration(ms) {
    if (!ms || ms < 1000) return `${Math.round(ms || 0)}ms`
    const seconds = (ms / 1000).toFixed(1)
    return `${seconds}s`
  }
  
  function getQualityColor(score) {
    if (score >= 80) return 'neon-green'
    if (score >= 60) return 'neon-cyan'
    if (score >= 40) return 'neon-purple'
    return 'neon-red'
  }
  
  function getSuccessRateColor(rate) {
    if (rate >= 90) return 'neon-green'
    if (rate >= 70) return 'neon-cyan'
    if (rate >= 50) return 'neon-purple'
    return 'neon-red'
  }
  
  // Chart data for visualization
  const contentDistribution = $derived(() => {
    if (!dashboardMetrics) return []
    
    return [
      { label: 'Raw Content', value: dashboardMetrics.contentLength, color: 'neon-cyan' },
      { label: 'AI Analysis', value: dashboardMetrics.aiContentLength, color: 'neon-purple' }
    ].filter(item => item.value > 0)
  })
  
  const mediaBreakdown = $derived(() => {
    if (!dashboardMetrics) return []
    
    return [
      { label: 'Images', value: dashboardMetrics.images, color: 'neon-green', icon: '🖼️' },
      { label: 'Videos', value: dashboardMetrics.videos, color: 'neon-purple', icon: '🎥' },
      { label: 'Audio', value: dashboardMetrics.audios, color: 'neon-cyan', icon: '🔊' }
    ].filter(item => item.value > 0)
  })
  
  const linkAnalysis = $derived(() => {
    if (!dashboardMetrics) return []
    
    return [
      { label: 'Internal', value: dashboardMetrics.internalLinks, color: 'neon-blue', icon: '🔗' },
      { label: 'External', value: dashboardMetrics.externalLinks, color: 'neon-green', icon: '🌐' },
      { label: 'Discovered', value: dashboardMetrics.discoveredUrls, color: 'neon-purple', icon: '🎯' }
    ].filter(item => item.value > 0)
  })
</script>

<div class="cyber-card p-8 animate-slide-up">
  <div class="flex items-center gap-4 mb-8">
    <span class="text-3xl">📊</span>
    <div>
      <h3 class="text-2xl font-bold font-mono text-neon-cyan">ANALYSIS_DASHBOARD</h3>
      <p class="text-sm font-mono text-gray-300 mt-2">
        Advanced metrics and insights from crawl operations
      </p>
    </div>
  </div>

  {#if results?.status === 'error'}
    <div class="bg-cyber-dark/50 border border-neon-red/50 rounded-lg p-6">
      <h4 class="font-bold font-mono text-neon-red mb-3">ANALYSIS_UNAVAILABLE</h4>
      <p class="text-sm font-mono text-gray-300">Cannot generate dashboard for failed operations</p>
    </div>
  {:else if batchMetrics}
    <!-- Batch Analysis Dashboard -->
    <div class="space-y-8">
      <!-- Batch Overview KPIs -->
      <div>
        <h4 class="font-bold font-mono text-neon-cyan mb-4 flex items-center gap-2">
          🚀 BATCH_OPERATION_OVERVIEW
        </h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-cyber-dark/30 border border-neon-cyan/30 rounded-lg p-4">
            <div class="text-xs font-mono text-neon-cyan mb-1">TOTAL_PROCESSED</div>
            <div class="text-2xl font-bold font-mono text-neon-cyan">{batchMetrics.total}</div>
          </div>
          <div class="bg-cyber-dark/30 border border-neon-green/30 rounded-lg p-4">
            <div class="text-xs font-mono text-neon-green mb-1">SUCCESSFUL</div>
            <div class="text-2xl font-bold font-mono text-neon-green">{batchMetrics.successful}</div>
          </div>
          <div class="bg-cyber-dark/30 border border-neon-red/30 rounded-lg p-4">
            <div class="text-xs font-mono text-neon-red mb-1">FAILED</div>
            <div class="text-2xl font-bold font-mono text-neon-red">{batchMetrics.failed}</div>
          </div>
          <div class="bg-cyber-dark/30 border border-{getSuccessRateColor(batchMetrics.successRate)}/30 rounded-lg p-4">
            <div class="text-xs font-mono text-{getSuccessRateColor(batchMetrics.successRate)} mb-1">SUCCESS_RATE</div>
            <div class="text-2xl font-bold font-mono text-{getSuccessRateColor(batchMetrics.successRate)}">{batchMetrics.successRate.toFixed(1)}%</div>
          </div>
        </div>
      </div>

      <!-- Batch Content Analysis -->
      <div>
        <h4 class="font-bold font-mono text-neon-purple mb-4 flex items-center gap-2">
          📈 AGGREGATE_CONTENT_METRICS
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-gradient-to-br from-cyber-dark/40 to-cyber-gray/20 border border-neon-cyan/30 rounded-lg p-6">
            <div class="text-sm font-mono text-neon-cyan mb-2">TOTAL_CONTENT_EXTRACTED</div>
            <div class="text-xl font-bold font-mono text-neon-cyan">{formatBytes(batchMetrics.totalContentExtracted)}</div>
            <div class="text-xs font-mono text-gray-400 mt-2">Raw HTML/text content</div>
          </div>
          <div class="bg-gradient-to-br from-cyber-dark/40 to-cyber-gray/20 border border-neon-purple/30 rounded-lg p-6">
            <div class="text-sm font-mono text-neon-purple mb-2">AI_PROCESSED_CONTENT</div>
            <div class="text-xl font-bold font-mono text-neon-purple">{formatBytes(batchMetrics.totalAiContent)}</div>
            <div class="text-xs font-mono text-gray-400 mt-2">Enhanced extraction</div>
          </div>
          <div class="bg-gradient-to-br from-cyber-dark/40 to-cyber-gray/20 border border-neon-green/30 rounded-lg p-6">
            <div class="text-sm font-mono text-neon-green mb-2">AVG_PROCESSING_TIME</div>
            <div class="text-xl font-bold font-mono text-neon-green">{formatDuration(batchMetrics.avgProcessingTime)}</div>
            <div class="text-xs font-mono text-gray-400 mt-2">Per page average</div>
          </div>
        </div>
      </div>

      <!-- Batch Discovery Metrics -->
      <div>
        <h4 class="font-bold font-mono text-neon-yellow mb-4 flex items-center gap-2">
          🔍 DISCOVERY_ANALYTICS
        </h4>
        <div class="grid grid-cols-2 gap-6">
          <div class="bg-cyber-dark/30 border border-neon-blue/30 rounded-lg p-5">
            <div class="text-sm font-mono text-neon-blue mb-3 flex items-center gap-2">
              🔗 TOTAL_LINKS_DISCOVERED
            </div>
            <div class="text-3xl font-bold font-mono text-neon-blue mb-2">{batchMetrics.totalLinksFound}</div>
            <div class="text-xs font-mono text-gray-400">Internal + External links</div>
          </div>
          <div class="bg-cyber-dark/30 border border-neon-pink/30 rounded-lg p-5">
            <div class="text-sm font-mono text-neon-pink mb-3 flex items-center gap-2">
              🎭 TOTAL_MEDIA_FOUND
            </div>
            <div class="text-3xl font-bold font-mono text-neon-pink mb-2">{batchMetrics.totalMediaFound}</div>
            <div class="text-xs font-mono text-gray-400">Images, videos & audio</div>
          </div>
        </div>
      </div>
    </div>
  {:else if dashboardMetrics}
    <!-- Single Page Analysis Dashboard -->
    <div class="space-y-8">
      <!-- Page Overview -->
      <div>
        <h4 class="font-bold font-mono text-neon-cyan mb-4 flex items-center gap-2">
          🎯 PAGE_ANALYSIS_OVERVIEW
        </h4>
        <div class="bg-cyber-dark/20 border border-neon-cyan/20 rounded-lg p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div class="text-sm font-mono text-neon-cyan mb-2">TARGET_URL</div>
              <div class="text-sm font-mono text-gray-300 break-all bg-cyber-gray/30 p-3 rounded">
                {dashboardMetrics.url}
              </div>
            </div>
            <div>
              <div class="text-sm font-mono text-neon-cyan mb-2">PAGE_TITLE</div>
              <div class="text-sm font-mono text-gray-300 bg-cyber-gray/30 p-3 rounded">
                {dashboardMetrics.title}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quality & Performance KPIs -->
      <div>
        <h4 class="font-bold font-mono text-neon-purple mb-4 flex items-center gap-2">
          📊 QUALITY_&_PERFORMANCE_METRICS
        </h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-cyber-dark/30 border border-{getQualityColor(dashboardMetrics.contentQuality)}/30 rounded-lg p-4 text-center">
            <div class="text-xs font-mono text-{getQualityColor(dashboardMetrics.contentQuality)} mb-1">QUALITY_SCORE</div>
            <div class="text-2xl font-bold font-mono text-{getQualityColor(dashboardMetrics.contentQuality)}">{dashboardMetrics.contentQuality}/100</div>
          </div>
          <div class="bg-cyber-dark/30 border border-neon-cyan/30 rounded-lg p-4 text-center">
            <div class="text-xs font-mono text-neon-cyan mb-1">EXTRACTION_TYPE</div>
            <div class="text-sm font-bold font-mono text-neon-cyan">{dashboardMetrics.extractionType}</div>
          </div>
          <div class="bg-cyber-dark/30 border border-neon-green/30 rounded-lg p-4 text-center">
            <div class="text-xs font-mono text-neon-green mb-1">PROCESSING_TIME</div>
            <div class="text-sm font-bold font-mono text-neon-green">{formatDuration(dashboardMetrics.processingTime)}</div>
          </div>
          <div class="bg-cyber-dark/30 border border-{dashboardMetrics.stealthActive ? 'neon-purple' : 'gray-500'}/30 rounded-lg p-4 text-center">
            <div class="text-xs font-mono text-{dashboardMetrics.stealthActive ? 'neon-purple' : 'gray-500'} mb-1">STEALTH_MODE</div>
            <div class="text-sm font-bold font-mono text-{dashboardMetrics.stealthActive ? 'neon-purple' : 'gray-500'}">
              {dashboardMetrics.stealthActive ? 'ACTIVE' : 'DISABLED'}
            </div>
          </div>
        </div>
      </div>

      <!-- Content Analysis Visualization -->
      {#if contentDistribution.length > 0}
        <div>
          <h4 class="font-bold font-mono text-neon-cyan mb-4 flex items-center gap-2">
            📄 CONTENT_DISTRIBUTION_ANALYSIS
          </h4>
          <div class="bg-cyber-dark/20 border border-neon-cyan/20 rounded-lg p-6">
            <div class="space-y-4">
              {#each contentDistribution as item}
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 rounded-full bg-{item.color}"></div>
                    <span class="text-sm font-mono text-{item.color}">{item.label}</span>
                  </div>
                  <div class="text-sm font-mono text-gray-300">{formatBytes(item.value)}</div>
                </div>
                <div class="w-full bg-cyber-gray/30 rounded-full h-2">
                  <div class="bg-{item.color} h-2 rounded-full" style="width: {(item.value / Math.max(...contentDistribution.map(c => c.value))) * 100}%"></div>
                </div>
              {/each}
            </div>
          </div>
        </div>
      {/if}

      <!-- Link Discovery Analysis -->
      {#if linkAnalysis.length > 0}
        <div>
          <h4 class="font-bold font-mono text-neon-blue mb-4 flex items-center gap-2">
            🔗 LINK_DISCOVERY_MATRIX
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            {#each linkAnalysis as link}
              <div class="bg-gradient-to-br from-cyber-dark/40 to-cyber-gray/20 border border-{link.color}/30 rounded-lg p-5 text-center">
                <div class="text-2xl mb-2">{link.icon}</div>
                <div class="text-xs font-mono text-{link.color} mb-2">{link.label.toUpperCase()}_LINKS</div>
                <div class="text-2xl font-bold font-mono text-{link.color}">{link.value}</div>
              </div>
            {/each}
          </div>
          
          {#if dashboardMetrics.avgRelevanceScore > 0}
            <div class="mt-4 bg-cyber-dark/30 border border-neon-purple/30 rounded-lg p-4">
              <div class="text-sm font-mono text-neon-purple mb-2">AVERAGE_RELEVANCE_SCORE</div>
              <div class="flex items-center gap-3">
                <div class="flex-1 bg-cyber-gray/30 rounded-full h-3">
                  <div class="bg-neon-purple h-3 rounded-full" style="width: {dashboardMetrics.avgRelevanceScore * 100}%"></div>
                </div>
                <div class="text-lg font-bold font-mono text-neon-purple">{(dashboardMetrics.avgRelevanceScore * 100).toFixed(1)}%</div>
              </div>
            </div>
          {/if}
        </div>
      {/if}

      <!-- Media Discovery Analysis -->
      {#if mediaBreakdown.length > 0}
        <div>
          <h4 class="font-bold font-mono text-neon-pink mb-4 flex items-center gap-2">
            🎭 MEDIA_DISCOVERY_BREAKDOWN
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            {#each mediaBreakdown as media}
              <div class="bg-gradient-to-br from-cyber-dark/40 to-cyber-gray/20 border border-{media.color}/30 rounded-lg p-5 text-center">
                <div class="text-3xl mb-3">{media.icon}</div>
                <div class="text-xs font-mono text-{media.color} mb-2">{media.label.toUpperCase()}_COUNT</div>
                <div class="text-2xl font-bold font-mono text-{media.color}">{media.value}</div>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Technical Details -->
      <div>
        <h4 class="font-bold font-mono text-neon-yellow mb-4 flex items-center gap-2">
          ⚙️ TECHNICAL_DETAILS
        </h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-cyber-dark/30 border border-neon-cyan/20 rounded-lg p-4">
            <div class="text-xs font-mono text-neon-cyan mb-2">CRAWL_TYPE</div>
            <div class="text-sm font-mono text-gray-300">{dashboardMetrics.crawlType.toUpperCase()}</div>
          </div>
          {#if dashboardMetrics.aiProvider}
            <div class="bg-cyber-dark/30 border border-neon-purple/20 rounded-lg p-4">
              <div class="text-xs font-mono text-neon-purple mb-2">AI_PROVIDER</div>
              <div class="text-sm font-mono text-gray-300">{dashboardMetrics.aiProvider}</div>
            </div>
          {/if}
          {#if dashboardMetrics.timestamp}
            <div class="bg-cyber-dark/30 border border-neon-green/20 rounded-lg p-4">
              <div class="text-xs font-mono text-neon-green mb-2">TIMESTAMP</div>
              <div class="text-xs font-mono text-gray-300">{new Date(dashboardMetrics.timestamp).toLocaleString()}</div>
            </div>
          {/if}
          <div class="bg-cyber-dark/30 border border-neon-blue/20 rounded-lg p-4">
            <div class="text-xs font-mono text-neon-blue mb-2">CONTENT_SIZE</div>
            <div class="text-sm font-mono text-gray-300">{formatBytes(dashboardMetrics.contentLength)}</div>
          </div>
        </div>
      </div>
    </div>
  {:else}
    <div class="bg-cyber-dark/30 border border-gray-500/30 rounded-lg p-6 text-center">
      <div class="text-4xl mb-4">⏳</div>
      <div class="text-lg font-mono text-gray-400 mb-2">AWAITING_DATA</div>
      <div class="text-sm font-mono text-gray-500">Start a crawl operation to view analysis dashboard</div>
    </div>
  {/if}
</div>

<style>
  .cyber-card {
    background: linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(17, 17, 17, 0.9));
    border: 1px solid rgba(0, 255, 255, 0.3);
    backdrop-filter: blur(10px);
  }
  
  .animate-slide-up {
    animation: slideUp 0.6s ease-out;
  }
  
  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>