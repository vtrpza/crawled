<script>
  import { createEventDispatcher, onMount } from 'svelte';
  
  let { visible = false } = $props();
  
  const dispatch = createEventDispatcher();
  
  let loading = $state(false);
  let error = $state(null);
  let results = $state([]);
  let statistics = $state(null);
  let currentPage = $state(1);
  let totalPages = $state(1);
  let searchQuery = $state('');
  let selectedMode = $state('');
  let selectedStatus = $state('');
  
  // Fetch crawl history
  async function fetchHistory(page = 1, query = '', mode = '', status = '') {
    loading = true;
    error = null;
    
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '10',
        include_content: 'false'
      });
      
      if (query) params.append('query', query);
      if (mode) params.append('mode', mode);
      if (status) params.append('status', status);
      
      const response = await fetch(`/api/results?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        results = data.results;
        currentPage = data.pagination.page;
        totalPages = data.pagination.pages;
      } else {
        throw new Error(data.error || 'Failed to fetch history');
      }
    } catch (e) {
      error = e.message;
      console.error('History fetch error:', e);
    } finally {
      loading = false;
    }
  }
  
  // Fetch statistics
  async function fetchStatistics() {
    try {
      const response = await fetch('/api/statistics');
      const data = await response.json();
      
      if (data.status === 'success') {
        statistics = data.statistics;
      }
    } catch (e) {
      console.error('Statistics fetch error:', e);
    }
  }
  
  // Load data when component becomes visible
  $effect(() => {
    if (visible) {
      fetchHistory();
      fetchStatistics();
    }
  });
  
  // Handle search
  function handleSearch() {
    fetchHistory(1, searchQuery, selectedMode, selectedStatus);
  }
  
  // Handle pagination
  function goToPage(page) {
    fetchHistory(page, searchQuery, selectedMode, selectedStatus);
  }
  
  // View specific result
  function viewResult(resultId) {
    dispatch('viewResult', { resultId });
  }
  
  // Close history view
  function closeHistory() {
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
  
  // Format duration
  function formatDuration(ms) {
    if (!ms) return 'N/A';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
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
  
  // Get mode icon
  function getModeIcon(mode) {
    switch (mode) {
      case 'simple': return '⚡';
      case 'advanced': return '🚀';
      case 'extract': return '🎯';
      case 'batch': return '📦';
      case 'media': return '📸';
      case 'interactive': return '🤖';
      case 'ai': return '🧠';
      case 'stealth': return '🥷';
      case 'smart': return '🤖';
      default: return '📄';
    }
  }
</script>

{#if visible}
  <div class="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-cyber-dark border border-neon-cyan/30 rounded-lg w-full max-w-7xl h-full max-h-[90vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-700">
        <div class="flex items-center gap-4">
          <h2 class="text-2xl font-bold font-mono text-neon-cyan">📊 CRAWL_HISTORY</h2>
          {#if statistics?.overall}
            <div class="flex items-center gap-4 text-sm font-mono">
              <span class="text-neon-green">✓ {statistics.overall.successful_crawls}</span>
              <span class="text-neon-red">✗ {statistics.overall.failed_crawls}</span>
              <span class="text-gray-400">Total: {statistics.overall.total_crawls}</span>
            </div>
          {/if}
        </div>
        
        <button 
          on:click={closeHistory}
          class="text-gray-400 hover:text-neon-red text-2xl font-mono transition-colors"
        >
          ✕
        </button>
      </div>
      
      <!-- Statistics Panel (if available) -->
      {#if statistics}
        <div class="p-6 border-b border-gray-700">
          <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div class="bg-cyber-dark/50 border border-neon-cyan/30 rounded p-4">
              <div class="text-xs font-mono text-neon-cyan mb-1">TOTAL</div>
              <div class="text-xl font-bold font-mono text-neon-cyan">{statistics.overall.total_crawls}</div>
            </div>
            <div class="bg-cyber-dark/50 border border-neon-green/30 rounded p-4">
              <div class="text-xs font-mono text-neon-green mb-1">SUCCESS</div>
              <div class="text-xl font-bold font-mono text-neon-green">{statistics.overall.successful_crawls}</div>
            </div>
            <div class="bg-cyber-dark/50 border border-neon-red/30 rounded p-4">
              <div class="text-xs font-mono text-neon-red mb-1">FAILED</div>
              <div class="text-xl font-bold font-mono text-neon-red">{statistics.overall.failed_crawls}</div>
            </div>
            <div class="bg-cyber-dark/50 border border-neon-yellow/30 rounded p-4">
              <div class="text-xs font-mono text-neon-yellow mb-1">IN_PROGRESS</div>
              <div class="text-xl font-bold font-mono text-neon-yellow">{statistics.overall.in_progress_crawls}</div>
            </div>
            <div class="bg-cyber-dark/50 border border-neon-purple/30 rounded p-4">
              <div class="text-xs font-mono text-neon-purple mb-1">SUCCESS_RATE</div>
              <div class="text-xl font-bold font-mono text-neon-purple">{(statistics.overall.success_rate * 100).toFixed(1)}%</div>
            </div>
          </div>
        </div>
      {/if}
      
      <!-- Filters -->
      <div class="p-6 border-b border-gray-700">
        <div class="flex flex-wrap gap-4 items-center">
          <div class="flex-1 min-w-64">
            <input
              bind:value={searchQuery}
              placeholder="Search crawl results..."
              class="w-full bg-black/50 border border-gray-700 rounded px-4 py-2 font-mono text-sm text-gray-300 placeholder-gray-500 focus:border-neon-cyan/50 focus:outline-none"
              on:keypress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          
          <select 
            bind:value={selectedMode}
            class="bg-black/50 border border-gray-700 rounded px-4 py-2 font-mono text-sm text-gray-300 focus:border-neon-cyan/50 focus:outline-none"
          >
            <option value="">All Modes</option>
            <option value="simple">Simple</option>
            <option value="advanced">Advanced</option>
            <option value="extract">Extract</option>
            <option value="batch">Batch</option>
            <option value="media">Media</option>
            <option value="interactive">Interactive</option>
            <option value="ai">AI</option>
            <option value="stealth">Stealth</option>
            <option value="smart">Smart</option>
          </select>
          
          <select 
            bind:value={selectedStatus}
            class="bg-black/50 border border-gray-700 rounded px-4 py-2 font-mono text-sm text-gray-300 focus:border-neon-cyan/50 focus:outline-none"
          >
            <option value="">All Status</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="in_progress">In Progress</option>
            <option value="pending">Pending</option>
          </select>
          
          <button 
            on:click={handleSearch}
            class="px-6 py-2 bg-neon-cyan/20 border border-neon-cyan/30 rounded font-mono text-sm text-neon-cyan hover:bg-neon-cyan/30 transition-colors"
          >
            SEARCH
          </button>
        </div>
      </div>
      
      <!-- Results List -->
      <div class="flex-1 overflow-y-auto p-6">
        {#if loading}
          <div class="flex items-center justify-center h-64">
            <div class="text-neon-cyan font-mono">⏳ LOADING_HISTORY...</div>
          </div>
        {:else if error}
          <div class="flex items-center justify-center h-64">
            <div class="text-neon-red font-mono">❌ ERROR: {error}</div>
          </div>
        {:else if results.length === 0}
          <div class="flex items-center justify-center h-64">
            <div class="text-gray-400 font-mono">📭 NO_RESULTS_FOUND</div>
          </div>
        {:else}
          <div class="space-y-4">
            {#each results as result}
              <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6 hover:border-neon-cyan/30 transition-colors cursor-pointer"
                   on:click={() => viewResult(result.id)}>
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <!-- Header -->
                    <div class="flex items-center gap-3 mb-3">
                      <span class="text-lg">{getModeIcon(result.mode)}</span>
                      <span class="font-mono text-sm text-neon-cyan font-bold">{result.mode?.toUpperCase() || 'UNKNOWN'}</span>
                      <span class={`font-mono text-xs px-2 py-1 rounded ${getStatusColor(result.status)} border border-current`}>
                        {result.status?.toUpperCase() || 'UNKNOWN'}
                      </span>
                      {#if result.stealth_level > 0}
                        <span class="font-mono text-xs text-neon-red">🥷 L{result.stealth_level}</span>
                      {/if}
                    </div>
                    
                    <!-- URL -->
                    <div class="font-mono text-sm text-gray-300 mb-2 truncate">
                      🎯 {result.url}
                    </div>
                    
                    <!-- Title -->
                    {#if result.title}
                      <div class="font-mono text-sm text-neon-green mb-2 truncate">
                        📄 {result.title}
                      </div>
                    {/if}
                    
                    <!-- Metadata -->
                    <div class="flex flex-wrap gap-4 text-xs font-mono text-gray-400">
                      <span>⏰ {formatTimestamp(result.requested_at)}</span>
                      {#if result.response_time_ms}
                        <span>⚡ {formatDuration(result.response_time_ms)}</span>
                      {/if}
                      {#if result.content_length}
                        <span>📊 {formatBytes(result.content_length)}</span>
                      {/if}
                      {#if result.domain}
                        <span>🌐 {result.domain}</span>
                      {/if}
                    </div>
                    
                    <!-- Error Message -->
                    {#if result.error_message}
                      <div class="mt-2 text-xs font-mono text-neon-red">
                        ❌ {result.error_message}
                      </div>
                    {/if}
                    
                    <!-- Extraction Query -->
                    {#if result.extraction_query}
                      <div class="mt-2 text-xs font-mono text-neon-purple">
                        🤖 {result.extraction_query}
                      </div>
                    {/if}
                  </div>
                  
                  <!-- Action Button -->
                  <div class="flex-shrink-0">
                    <button class="px-3 py-1 bg-neon-cyan/20 border border-neon-cyan/30 rounded font-mono text-xs text-neon-cyan hover:bg-neon-cyan/30 transition-colors">
                      VIEW
                    </button>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
      
      <!-- Pagination -->
      {#if totalPages > 1}
        <div class="p-6 border-t border-gray-700">
          <div class="flex items-center justify-between">
            <div class="text-sm font-mono text-gray-400">
              Page {currentPage} of {totalPages}
            </div>
            
            <div class="flex items-center gap-2">
              <button 
                on:click={() => goToPage(currentPage - 1)}
                disabled={currentPage <= 1}
                class="px-3 py-1 bg-gray-700 border border-gray-600 rounded font-mono text-xs text-gray-300 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                ◀ PREV
              </button>
              
              <!-- Page numbers -->
              {#each Array.from({length: Math.min(5, totalPages)}, (_, i) => {
                const startPage = Math.max(1, currentPage - 2);
                return startPage + i;
              }).filter(p => p <= totalPages) as page}
                <button 
                  on:click={() => goToPage(page)}
                  class={`px-3 py-1 border rounded font-mono text-xs transition-colors ${
                    page === currentPage 
                      ? 'bg-neon-cyan/20 border-neon-cyan/30 text-neon-cyan' 
                      : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {page}
                </button>
              {/each}
              
              <button 
                on:click={() => goToPage(currentPage + 1)}
                disabled={currentPage >= totalPages}
                class="px-3 py-1 bg-gray-700 border border-gray-600 rounded font-mono text-xs text-gray-300 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                NEXT ▶
              </button>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
{/if}