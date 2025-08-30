<script>
  import { createEventDispatcher, onMount } from 'svelte';
  
  let { visible = false, resultId = null } = $props();
  
  const dispatch = createEventDispatcher();
  
  let loading = $state(false);
  let error = $state(null);
  let result = $state(null);
  let activeTab = $state('overview');
  
  // Fetch result details
  async function fetchResult(id) {
    if (!id) return;
    
    loading = true;
    error = null;
    
    try {
      const response = await fetch(`/api/results/${id}?include_content=true`);
      const data = await response.json();
      
      if (data.status === 'success') {
        result = data.result;
      } else {
        throw new Error(data.error || 'Failed to fetch result');
      }
    } catch (e) {
      error = e.message;
      console.error('Result fetch error:', e);
    } finally {
      loading = false;
    }
  }
  
  // Load result when component becomes visible
  $effect(() => {
    if (visible && resultId) {
      fetchResult(resultId);
    }
  });
  
  // Close result viewer
  function closeViewer() {
    dispatch('close');
  }
  
  // Format timestamp
  function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    try {
      return new Date(timestamp).toLocaleString();
    } catch (e) {
      return timestamp;
    }
  }
  
  // Format bytes
  function formatBytes(bytes) {
    if (!bytes) return 'N/A';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  // Get status color
  function getStatusColor(status) {
    switch (status) {
      case 'completed': return 'text-neon-green';
      case 'failed': return 'text-neon-red';
      case 'in_progress': return 'text-neon-yellow';
      case 'pending': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  }
  
  // Copy to clipboard
  function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      // Could add a toast notification here
      console.log('Copied to clipboard');
    });
  }
  
  // Download content
  function downloadContent(content, filename) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
</script>

{#if visible}
  <div class="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-cyber-dark border border-neon-cyan/30 rounded-lg w-full max-w-7xl h-full max-h-[95vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-700">
        <div class="flex items-center gap-4">
          <h2 class="text-2xl font-bold font-mono text-neon-cyan">🔍 RESULT_VIEWER</h2>
          {#if result}
            <div class="flex items-center gap-3">
              <span class={`font-mono text-sm px-3 py-1 rounded border ${getStatusColor(result.status)}`}>
                {result.status?.toUpperCase()}
              </span>
              <span class="font-mono text-sm text-gray-400">
                {result.mode?.toUpperCase()}
              </span>
              {#if result.stealth_level > 0}
                <span class="font-mono text-sm text-neon-red">🥷 L{result.stealth_level}</span>
              {/if}
            </div>
          {/if}
        </div>
        
        <button 
          on:click={closeViewer}
          class="text-gray-400 hover:text-neon-red text-2xl font-mono transition-colors"
        >
          ✕
        </button>
      </div>
      
      {#if loading}
        <div class="flex items-center justify-center h-64">
          <div class="text-neon-cyan font-mono">⏳ LOADING_RESULT...</div>
        </div>
      {:else if error}
        <div class="flex items-center justify-center h-64">
          <div class="text-neon-red font-mono">❌ ERROR: {error}</div>
        </div>
      {:else if result}
        <!-- Tabs -->
        <div class="flex border-b border-gray-700">
          {#each [
            { id: 'overview', label: 'OVERVIEW', icon: '📊' },
            { id: 'content', label: 'CONTENT', icon: '📄' },
            { id: 'metadata', label: 'METADATA', icon: '🔧' },
            { id: 'raw', label: 'RAW_DATA', icon: '💾' }
          ] as tab}
            <button 
              on:click={() => activeTab = tab.id}
              class={`flex items-center gap-2 px-6 py-3 font-mono text-sm transition-colors border-b-2 ${
                activeTab === tab.id 
                  ? 'text-neon-cyan border-neon-cyan bg-cyber-dark/50' 
                  : 'text-gray-400 border-transparent hover:text-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          {/each}
        </div>
        
        <!-- Tab Content -->
        <div class="flex-1 overflow-y-auto p-6">
          {#if activeTab === 'overview'}
            <!-- Overview Tab -->
            <div class="space-y-6">
              <!-- Basic Info -->
              <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                <h3 class="font-bold font-mono text-neon-cyan mb-4">📋 BASIC_INFO</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-3">
                    <div class="flex justify-between">
                      <span class="text-gray-400 font-mono text-sm">URL:</span>
                      <span class="text-gray-300 font-mono text-sm break-all">{result.url}</span>
                    </div>
                    {#if result.title}
                      <div class="flex justify-between">
                        <span class="text-gray-400 font-mono text-sm">TITLE:</span>
                        <span class="text-gray-300 font-mono text-sm">{result.title}</span>
                      </div>
                    {/if}
                    {#if result.final_url && result.final_url !== result.url}
                      <div class="flex justify-between">
                        <span class="text-gray-400 font-mono text-sm">FINAL_URL:</span>
                        <span class="text-gray-300 font-mono text-sm break-all">{result.final_url}</span>
                      </div>
                    {/if}
                    <div class="flex justify-between">
                      <span class="text-gray-400 font-mono text-sm">DOMAIN:</span>
                      <span class="text-gray-300 font-mono text-sm">{result.domain || 'N/A'}</span>
                    </div>
                  </div>
                  <div class="space-y-3">
                    <div class="flex justify-between">
                      <span class="text-gray-400 font-mono text-sm">REQUESTED:</span>
                      <span class="text-gray-300 font-mono text-sm">{formatTimestamp(result.requested_at)}</span>
                    </div>
                    {#if result.started_at}
                      <div class="flex justify-between">
                        <span class="text-gray-400 font-mono text-sm">STARTED:</span>
                        <span class="text-gray-300 font-mono text-sm">{formatTimestamp(result.started_at)}</span>
                      </div>
                    {/if}
                    {#if result.completed_at}
                      <div class="flex justify-between">
                        <span class="text-gray-400 font-mono text-sm">COMPLETED:</span>
                        <span class="text-gray-300 font-mono text-sm">{formatTimestamp(result.completed_at)}</span>
                      </div>
                    {/if}
                    {#if result.duration_ms}
                      <div class="flex justify-between">
                        <span class="text-gray-400 font-mono text-sm">DURATION:</span>
                        <span class="text-gray-300 font-mono text-sm">{result.duration_ms}ms</span>
                      </div>
                    {/if}
                  </div>
                </div>
              </div>
              
              <!-- Performance Metrics -->
              <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                <h3 class="font-bold font-mono text-neon-cyan mb-4">⚡ PERFORMANCE</h3>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div class="bg-black/30 rounded p-4 text-center">
                    <div class="text-xs font-mono text-gray-400 mb-1">RESPONSE_TIME</div>
                    <div class="text-lg font-mono text-neon-green">{result.response_time_ms || 'N/A'}ms</div>
                  </div>
                  <div class="bg-black/30 rounded p-4 text-center">
                    <div class="text-xs font-mono text-gray-400 mb-1">CONTENT_SIZE</div>
                    <div class="text-lg font-mono text-neon-green">{formatBytes(result.content_length)}</div>
                  </div>
                  <div class="bg-black/30 rounded p-4 text-center">
                    <div class="text-xs font-mono text-gray-400 mb-1">STATUS_CODE</div>
                    <div class="text-lg font-mono text-neon-green">{result.status_code || 'N/A'}</div>
                  </div>
                  <div class="bg-black/30 rounded p-4 text-center">
                    <div class="text-xs font-mono text-gray-400 mb-1">LINKS_FOUND</div>
                    <div class="text-lg font-mono text-neon-green">
                      {(result.internal_links?.length || 0) + (result.external_links?.length || 0)}
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Configuration -->
              {#if result.extraction_query || result.custom_config}
                <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                  <h3 class="font-bold font-mono text-neon-cyan mb-4">⚙️ CONFIGURATION</h3>
                  {#if result.extraction_query}
                    <div class="mb-4">
                      <div class="text-sm font-mono text-gray-400 mb-2">EXTRACTION_QUERY:</div>
                      <div class="bg-black/30 border border-gray-700 rounded p-3 font-mono text-sm text-neon-purple">
                        {result.extraction_query}
                      </div>
                    </div>
                  {/if}
                  {#if result.custom_user_agent}
                    <div class="mb-4">
                      <div class="text-sm font-mono text-gray-400 mb-2">USER_AGENT:</div>
                      <div class="bg-black/30 border border-gray-700 rounded p-3 font-mono text-xs text-gray-300">
                        {result.custom_user_agent}
                      </div>
                    </div>
                  {/if}
                </div>
              {/if}
              
              <!-- Error Info -->
              {#if result.error_message}
                <div class="bg-gradient-to-br from-neon-red/10 to-cyber-dark/50 border border-neon-red/30 rounded-lg p-6">
                  <h3 class="font-bold font-mono text-neon-red mb-4">❌ ERROR_INFO</h3>
                  <div class="bg-black/30 border border-gray-700 rounded p-3 font-mono text-sm text-neon-red">
                    {result.error_message}
                  </div>
                  {#if result.error_details}
                    <div class="mt-4">
                      <div class="text-sm font-mono text-gray-400 mb-2">ERROR_DETAILS:</div>
                      <div class="bg-black/30 border border-gray-700 rounded p-3 font-mono text-xs text-gray-300">
                        <pre>{JSON.stringify(result.error_details, null, 2)}</pre>
                      </div>
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
            
          {:else if activeTab === 'content'}
            <!-- Content Tab -->
            <div class="space-y-6">
              {#if result.ai_analysis}
                <div class="bg-gradient-to-br from-neon-purple/10 to-cyber-dark/50 border border-neon-purple/30 rounded-lg p-6">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="font-bold font-mono text-neon-purple">🤖 AI_ANALYSIS</h3>
                    <div class="flex gap-2">
                      <button 
                        on:click={() => copyToClipboard(result.ai_analysis)}
                        class="px-3 py-1 bg-neon-purple/20 border border-neon-purple/30 rounded font-mono text-xs text-neon-purple hover:bg-neon-purple/30 transition-colors"
                      >
                        COPY
                      </button>
                      <button 
                        on:click={() => downloadContent(result.ai_analysis, `ai_analysis_${result.id.slice(0, 8)}.txt`)}
                        class="px-3 py-1 bg-neon-purple/20 border border-neon-purple/30 rounded font-mono text-xs text-neon-purple hover:bg-neon-purple/30 transition-colors"
                      >
                        DOWNLOAD
                      </button>
                    </div>
                  </div>
                  <div class="bg-black/30 border border-gray-700 rounded p-4 max-h-96 overflow-y-auto">
                    <pre class="whitespace-pre-wrap text-sm text-gray-300 font-mono">{result.ai_analysis}</pre>
                  </div>
                </div>
              {/if}
              
              {#if result.extracted_content}
                <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="font-bold font-mono text-neon-cyan">🎯 EXTRACTED_CONTENT</h3>
                    <div class="flex gap-2">
                      <button 
                        on:click={() => copyToClipboard(result.extracted_content)}
                        class="px-3 py-1 bg-neon-cyan/20 border border-neon-cyan/30 rounded font-mono text-xs text-neon-cyan hover:bg-neon-cyan/30 transition-colors"
                      >
                        COPY
                      </button>
                      <button 
                        on:click={() => downloadContent(result.extracted_content, `extracted_${result.id.slice(0, 8)}.txt`)}
                        class="px-3 py-1 bg-neon-cyan/20 border border-neon-cyan/30 rounded font-mono text-xs text-neon-cyan hover:bg-neon-cyan/30 transition-colors"
                      >
                        DOWNLOAD
                      </button>
                    </div>
                  </div>
                  <div class="bg-black/30 border border-gray-700 rounded p-4 max-h-96 overflow-y-auto">
                    <pre class="whitespace-pre-wrap text-sm text-gray-300 font-mono">{result.extracted_content}</pre>
                  </div>
                </div>
              {/if}
              
              {#if result.content && !result.ai_analysis && !result.extracted_content}
                <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="font-bold font-mono text-neon-cyan">📄 RAW_CONTENT</h3>
                    <div class="flex gap-2">
                      <button 
                        on:click={() => copyToClipboard(result.content)}
                        class="px-3 py-1 bg-neon-cyan/20 border border-neon-cyan/30 rounded font-mono text-xs text-neon-cyan hover:bg-neon-cyan/30 transition-colors"
                      >
                        COPY
                      </button>
                      <button 
                        on:click={() => downloadContent(result.content, `content_${result.id.slice(0, 8)}.txt`)}
                        class="px-3 py-1 bg-neon-cyan/20 border border-neon-cyan/30 rounded font-mono text-xs text-neon-cyan hover:bg-neon-cyan/30 transition-colors"
                      >
                        DOWNLOAD
                      </button>
                    </div>
                  </div>
                  <div class="bg-black/30 border border-gray-700 rounded p-4 max-h-96 overflow-y-auto">
                    <pre class="whitespace-pre-wrap text-sm text-gray-300 font-mono">{result.content}</pre>
                  </div>
                </div>
              {/if}
              
              {#if result.markdown_content}
                <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="font-bold font-mono text-neon-cyan">📝 MARKDOWN</h3>
                    <button 
                      on:click={() => downloadContent(result.markdown_content, `markdown_${result.id.slice(0, 8)}.md`)}
                      class="px-3 py-1 bg-neon-cyan/20 border border-neon-cyan/30 rounded font-mono text-xs text-neon-cyan hover:bg-neon-cyan/30 transition-colors"
                    >
                      DOWNLOAD
                    </button>
                  </div>
                  <div class="bg-black/30 border border-gray-700 rounded p-4 max-h-96 overflow-y-auto">
                    <pre class="whitespace-pre-wrap text-sm text-gray-300 font-mono">{result.markdown_content}</pre>
                  </div>
                </div>
              {/if}
            </div>
            
          {:else if activeTab === 'metadata'}
            <!-- Metadata Tab -->
            <div class="space-y-6">
              <!-- Links -->
              {#if result.internal_links?.length > 0 || result.external_links?.length > 0}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {#if result.internal_links?.length > 0}
                    <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                      <h3 class="font-bold font-mono text-neon-green mb-4">🔗 INTERNAL_LINKS ({result.internal_links.length})</h3>
                      <div class="space-y-2 max-h-64 overflow-y-auto">
                        {#each result.internal_links.slice(0, 20) as link}
                          <div class="text-sm font-mono text-gray-300 break-all">{link}</div>
                        {/each}
                        {#if result.internal_links.length > 20}
                          <div class="text-xs font-mono text-gray-500">... and {result.internal_links.length - 20} more</div>
                        {/if}
                      </div>
                    </div>
                  {/if}
                  
                  {#if result.external_links?.length > 0}
                    <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                      <h3 class="font-bold font-mono text-neon-yellow mb-4">🌐 EXTERNAL_LINKS ({result.external_links.length})</h3>
                      <div class="space-y-2 max-h-64 overflow-y-auto">
                        {#each result.external_links.slice(0, 20) as link}
                          <div class="text-sm font-mono text-gray-300 break-all">{link}</div>
                        {/each}
                        {#if result.external_links.length > 20}
                          <div class="text-xs font-mono text-gray-500">... and {result.external_links.length - 20} more</div>
                        {/if}
                      </div>
                    </div>
                  {/if}
                </div>
              {/if}
              
              <!-- Media -->
              {#if result.images?.length > 0 || result.videos?.length > 0}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {#if result.images?.length > 0}
                    <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                      <h3 class="font-bold font-mono text-neon-purple mb-4">📸 IMAGES ({result.images.length})</h3>
                      <div class="space-y-2 max-h-64 overflow-y-auto">
                        {#each result.images.slice(0, 10) as image}
                          <div class="text-sm font-mono text-gray-300 break-all">{image}</div>
                        {/each}
                        {#if result.images.length > 10}
                          <div class="text-xs font-mono text-gray-500">... and {result.images.length - 10} more</div>
                        {/if}
                      </div>
                    </div>
                  {/if}
                  
                  {#if result.videos?.length > 0}
                    <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                      <h3 class="font-bold font-mono text-neon-red mb-4">🎥 VIDEOS ({result.videos.length})</h3>
                      <div class="space-y-2 max-h-64 overflow-y-auto">
                        {#each result.videos.slice(0, 10) as video}
                          <div class="text-sm font-mono text-gray-300 break-all">{video}</div>
                        {/each}
                        {#if result.videos.length > 10}
                          <div class="text-xs font-mono text-gray-500">... and {result.videos.length - 10} more</div>
                        {/if}
                      </div>
                    </div>
                  {/if}
                </div>
              {/if}
              
              <!-- Stealth Features -->
              {#if result.stealth_features && Object.keys(result.stealth_features).length > 0}
                <div class="bg-gradient-to-br from-neon-red/10 to-cyber-dark/50 border border-neon-red/30 rounded-lg p-6">
                  <h3 class="font-bold font-mono text-neon-red mb-4">🥷 STEALTH_FEATURES</h3>
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {#each Object.entries(result.stealth_features) as [key, value]}
                      <div class="bg-black/30 border border-gray-700 rounded p-3">
                        <div class="text-xs font-mono text-gray-400 mb-1">{key.toUpperCase()}</div>
                        <div class="text-sm font-mono {value ? 'text-neon-green' : 'text-neon-red'}">{value ? '✓' : '✗'}</div>
                      </div>
                    {/each}
                  </div>
                </div>
              {/if}
              
              <!-- Performance Metrics -->
              {#if result.performance_metrics && Object.keys(result.performance_metrics).length > 0}
                <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
                  <h3 class="font-bold font-mono text-neon-cyan mb-4">📊 PERFORMANCE_METRICS</h3>
                  <div class="bg-black/30 border border-gray-700 rounded p-4">
                    <pre class="text-sm text-gray-300 font-mono">{JSON.stringify(result.performance_metrics, null, 2)}</pre>
                  </div>
                </div>
              {/if}
            </div>
            
          {:else if activeTab === 'raw'}
            <!-- Raw Data Tab -->
            <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="font-bold font-mono text-neon-cyan">💾 RAW_JSON_DATA</h3>
                <div class="flex gap-2">
                  <button 
                    on:click={() => copyToClipboard(JSON.stringify(result, null, 2))}
                    class="px-3 py-1 bg-neon-cyan/20 border border-neon-cyan/30 rounded font-mono text-xs text-neon-cyan hover:bg-neon-cyan/30 transition-colors"
                  >
                    COPY
                  </button>
                  <button 
                    on:click={() => downloadContent(JSON.stringify(result, null, 2), `result_${result.id.slice(0, 8)}.json`)}
                    class="px-3 py-1 bg-neon-cyan/20 border border-neon-cyan/30 rounded font-mono text-xs text-neon-cyan hover:bg-neon-cyan/30 transition-colors"
                  >
                    DOWNLOAD
                  </button>
                </div>
              </div>
              <div class="bg-black/30 border border-gray-700 rounded p-4 max-h-[60vh] overflow-auto">
                <pre class="text-xs text-gray-300 font-mono">{JSON.stringify(result, null, 2)}</pre>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </div>
{/if}