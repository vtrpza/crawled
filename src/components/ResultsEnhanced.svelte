<script>
  import { createEventDispatcher } from 'svelte';
  
  let { results, showHistory = false } = $props()
  
  const dispatch = createEventDispatcher();
  
  const isError = $derived(results?.status === 'error')
  const isBatch = $derived(results?.batch_results && results.batch_results.length > 0)
  const hasStealthFeatures = $derived(results?.stealth_features_v0_7 || results?.stealth_features)
  const hasDatabase = $derived(results?.database || results?.result_id)
  
  // Format timestamp for display
  function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    try {
      return new Date(timestamp).toLocaleString();
    } catch (e) {
      return timestamp;
    }
  }
  
  // Format file size
  function formatBytes(bytes) {
    if (bytes === 0 || !bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  // View full result
  function viewFullResult() {
    if (results.result_id || results.database?.result_id) {
      dispatch('viewResult', {
        resultId: results.result_id || results.database.result_id
      });
    }
  }
  
  // View history
  function viewHistory() {
    dispatch('viewHistory');
  }
</script>

<div class="cyber-card p-10 animate-slide-up">
  <!-- Header Section -->
  <div class="flex items-center justify-between mb-8">
    <div class="flex items-center gap-4">
      <span class="text-3xl">{isError ? '💀' : isBatch ? '🚀' : (results.ai_analysis || results.extracted_content) ? '🤖' : '⚡'}</span>
      <div>
        <h3 class="text-xl font-bold font-mono text-neon-cyan">
          {isError ? 'NEURAL_FAILURE' : isBatch ? 'BATCH_COMPLETE' : (results.ai_analysis || results.extracted_content) ? 'AI_EXTRACTION_SUCCESS' : 'EXTRACTION_SUCCESS'}
        </h3>
        <p class="text-sm font-mono text-gray-300 mt-2">
          {isError ? 'Critical system malfunction detected' : isBatch ? `Processed ${results.batch_summary?.total || 0} targets` : (results.ai_analysis || results.extracted_content) ? 'AI-powered data extraction completed' : 'Data successfully harvested from target'}
        </p>
        
        {#if hasDatabase}
          <div class="flex items-center gap-4 mt-2 text-xs font-mono text-neon-green">
            <span>📊 STORED</span>
            {#if results.database?.result_id}
              <span class="text-gray-400">ID: {results.database.result_id.slice(0, 8)}...</span>
            {/if}
            {#if results.database?.stored_at}
              <span class="text-gray-400">{formatTimestamp(results.database.stored_at)}</span>
            {/if}
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="flex gap-2">
      {#if hasDatabase}
        <button 
          on:click={viewFullResult}
          class="px-4 py-2 bg-neon-cyan/20 border border-neon-cyan/30 rounded font-mono text-xs text-neon-cyan hover:bg-neon-cyan/30 transition-colors"
        >
          VIEW_FULL
        </button>
      {/if}
      <button 
        on:click={viewHistory}
        class="px-4 py-2 bg-neon-purple/20 border border-neon-purple/30 rounded font-mono text-xs text-neon-purple hover:bg-neon-purple/30 transition-colors"
      >
        HISTORY
      </button>
    </div>
  </div>

  {#if isBatch}
    <!-- Batch Summary -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-cyber-dark/50 border border-neon-cyan/30 rounded-lg p-6">
        <div class="text-sm font-mono text-neon-cyan mb-2">TOTAL_TARGETS</div>
        <div class="text-2xl font-bold font-mono text-neon-cyan">{results.batch_summary.total}</div>
      </div>
      <div class="bg-cyber-dark/50 border border-neon-green/30 rounded-lg p-6">
        <div class="text-sm font-mono text-neon-green mb-2">SUCCESS_COUNT</div>
        <div class="text-2xl font-bold font-mono text-neon-green">{results.batch_summary.completed}</div>
      </div>
      <div class="bg-cyber-dark/50 border border-neon-red/30 rounded-lg p-6">
        <div class="text-sm font-mono text-neon-red mb-2">FAILURE_COUNT</div>
        <div class="text-2xl font-bold font-mono text-neon-red">{results.batch_summary.failed}</div>
      </div>
      <div class="bg-cyber-dark/50 border border-neon-purple/30 rounded-lg p-6">
        <div class="text-sm font-mono text-neon-purple mb-2">SUCCESS_RATE</div>
        <div class="text-2xl font-bold font-mono text-neon-purple">{results.batch_summary.success_rate}%</div>
      </div>
    </div>
  {/if}

  <!-- Enhanced Metadata Section -->
  {#if !isError}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <!-- Performance Metrics -->
      <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
        <h4 class="font-bold font-mono text-neon-cyan mb-4">⚡ PERFORMANCE</h4>
        <div class="space-y-3 text-sm font-mono">
          {#if results.response_time_ms || results.database?.duration_ms}
            <div class="flex justify-between">
              <span class="text-gray-400">RESPONSE_TIME:</span>
              <span class="text-neon-green">{results.response_time_ms || results.database?.duration_ms || 'N/A'}ms</span>
            </div>
          {/if}
          {#if results.content_length || results.database?.content_length}
            <div class="flex justify-between">
              <span class="text-gray-400">CONTENT_SIZE:</span>
              <span class="text-neon-green">{formatBytes(results.content_length || results.database?.content_length)}</span>
            </div>
          {/if}
          {#if results.pages_crawled}
            <div class="flex justify-between">
              <span class="text-gray-400">PAGES_CRAWLED:</span>
              <span class="text-neon-green">{results.pages_crawled}</span>
            </div>
          {/if}
          {#if results.ai_provider}
            <div class="flex justify-between">
              <span class="text-gray-400">AI_PROVIDER:</span>
              <span class="text-neon-purple">{results.ai_provider}</span>
            </div>
          {/if}
        </div>
      </div>

      <!-- Technical Details -->
      <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-6">
        <h4 class="font-bold font-mono text-neon-cyan mb-4">🔧 TECHNICAL</h4>
        <div class="space-y-3 text-sm font-mono">
          <div class="flex justify-between">
            <span class="text-gray-400">MODE:</span>
            <span class="text-neon-yellow">{results.mode || results.crawl_type || 'UNKNOWN'}</span>
          </div>
          {#if results.stealth_level !== undefined}
            <div class="flex justify-between">
              <span class="text-gray-400">STEALTH_LEVEL:</span>
              <span class="text-neon-red">{results.stealth_level}/5</span>
            </div>
          {/if}
          {#if results.strategy}
            <div class="flex justify-between">
              <span class="text-gray-400">STRATEGY:</span>
              <span class="text-neon-purple">{results.strategy}</span>
            </div>
          {/if}
          {#if results.final_url && results.final_url !== results.url}
            <div class="flex justify-between">
              <span class="text-gray-400">REDIRECTED:</span>
              <span class="text-neon-yellow">YES</span>
            </div>
          {/if}
        </div>
      </div>

      <!-- Database Info -->
      {#if hasDatabase}
        <div class="bg-cyber-dark/30 border border-neon-green/30 rounded-lg p-6">
          <h4 class="font-bold font-mono text-neon-green mb-4">📊 DATABASE</h4>
          <div class="space-y-3 text-sm font-mono">
            {#if results.database?.result_id || results.result_id}
              <div class="flex justify-between">
                <span class="text-gray-400">RESULT_ID:</span>
                <span class="text-neon-green text-xs">{(results.database?.result_id || results.result_id).slice(0, 8)}...</span>
              </div>
            {/if}
            {#if results.database?.session_id}
              <div class="flex justify-between">
                <span class="text-gray-400">SESSION_ID:</span>
                <span class="text-neon-green text-xs">{results.database.session_id.slice(0, 8)}...</span>
              </div>
            {/if}
            <div class="flex justify-between">
              <span class="text-gray-400">PERSISTENT:</span>
              <span class="text-neon-green">YES</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">SEARCHABLE:</span>
              <span class="text-neon-green">YES</span>
            </div>
          </div>
        </div>
      {/if}
    </div>
  {/if}

  <!-- AI Analysis Section -->
  {#if results.ai_analysis || results.ai_synthesis || results.extracted_content}
    <div class="bg-gradient-to-br from-neon-purple/10 to-neon-cyan/10 border border-neon-purple/30 rounded-lg p-8 mb-8">
      <h4 class="font-bold font-mono text-neon-purple mb-6">🤖 AI_ANALYSIS</h4>
      <div class="bg-black/50 border border-gray-700 rounded-lg p-6">
        <pre class="whitespace-pre-wrap text-sm text-gray-300 font-mono max-h-80 overflow-y-auto">{results.ai_analysis || results.ai_synthesis || results.extracted_content}</pre>
      </div>
    </div>
  {/if}

  <!-- Content Preview -->
  {#if results.content && !results.ai_analysis && !results.ai_synthesis}
    <div class="bg-cyber-dark/30 border border-gray-700 rounded-lg p-8 mb-8">
      <h4 class="font-bold font-mono text-neon-cyan mb-6">📄 CONTENT_PREVIEW</h4>
      <div class="bg-black/50 border border-gray-700 rounded-lg p-6">
        <pre class="whitespace-pre-wrap text-sm text-gray-300 font-mono max-h-60 overflow-y-auto">{results.content.slice(0, 2000)}{results.content.length > 2000 ? '\n\n... [TRUNCATED - Use VIEW_FULL to see complete content]' : ''}</pre>
      </div>
    </div>
  {/if}

  <!-- Stealth Features (if present) -->
  {#if hasStealthFeatures}
    {@const stealthFeatures = results.stealth_features_v0_7 || results.stealth_features}
    <div class="bg-gradient-to-br from-neon-red/10 to-cyber-dark/50 border border-neon-red/30 rounded-lg p-8 mb-8">
      <h4 class="font-bold font-mono text-neon-red mb-6">🥷 STEALTH_FEATURES</h4>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {#each Object.entries(stealthFeatures) as [key, value]}
          <div class="bg-black/30 border border-gray-700 rounded p-4">
            <div class="text-xs font-mono text-gray-400 mb-1">{key.toUpperCase()}</div>
            <div class="text-sm font-mono {value ? 'text-neon-green' : 'text-neon-red'}">{value ? '✓' : '✗'}</div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Error Display -->
  {#if isError}
    <div class="bg-gradient-to-br from-neon-red/10 to-cyber-dark/50 border border-neon-red/30 rounded-lg p-8">
      <h4 class="font-bold font-mono text-neon-red mb-4">❌ ERROR_ANALYSIS</h4>
      <div class="bg-black/50 border border-gray-700 rounded-lg p-6">
        <pre class="text-neon-red font-mono text-sm whitespace-pre-wrap">{results.error}</pre>
      </div>
      
      {#if results.attempted_config}
        <div class="mt-6">
          <h5 class="font-mono text-gray-400 mb-3">ATTEMPTED_CONFIG:</h5>
          <div class="bg-black/30 border border-gray-700 rounded p-4">
            <pre class="text-gray-300 font-mono text-xs">{JSON.stringify(results.attempted_config, null, 2)}</pre>
          </div>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Batch Results (if applicable) -->
  {#if isBatch && results.batch_results}
    <div class="space-y-6">
      {#if results.batch_results.filter(r => r.status === 'success').length > 0}
        {@const successful = results.batch_results.filter(r => r.status === 'success')}
        <div>
          <h4 class="font-bold font-mono text-neon-green mb-4">✓ SUCCESSFUL_EXTRACTIONS ({successful.length})</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            {#each successful.slice(0, 4) as result}
              <div class="bg-neon-green/5 border border-neon-green/20 rounded-lg p-6">
                <div class="font-mono text-sm text-neon-green mb-3">🎯 {result.url}</div>
                <div class="text-xs font-mono text-gray-400 mb-2">
                  CONTENT: {formatBytes(result.content_size || 0)} | LINKS: {result.links_found || 0} | TIME: {result.duration || 0}ms
                </div>
                {#if result.preview}
                  <div class="text-sm text-gray-300 font-mono bg-black/30 border border-gray-700 rounded p-3 max-h-32 overflow-hidden">
                    {result.preview}
                  </div>
                {/if}
              </div>
            {/each}
          </div>
          {#if successful.length > 4}
            <div class="text-center mt-4">
              <span class="text-xs font-mono text-gray-400">... and {successful.length - 4} more results</span>
            </div>
          {/if}
        </div>
      {/if}

      {#if results.batch_results.filter(r => r.status === 'error').length > 0}
        {@const failed = results.batch_results.filter(r => r.status === 'error')}
        <div>
          <h4 class="font-bold font-mono text-neon-red mb-4">❌ FAILED_EXTRACTIONS ({failed.length})</h4>
          <div class="space-y-3">
            {#each failed.slice(0, 3) as result}
              <div class="bg-neon-red/5 border border-neon-red/20 rounded-lg p-4">
                <div class="font-mono text-sm text-neon-red mb-2">💀 {result.url}</div>
                <div class="text-xs font-mono text-gray-400">ERROR: {result.error}</div>
              </div>
            {/each}
          </div>
          {#if failed.length > 3}
            <div class="text-center mt-4">
              <span class="text-xs font-mono text-gray-400">... and {failed.length - 3} more failures</span>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .animate-slide-up {
    animation: slideUp 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
  }

  @keyframes slideUp {
    0% {
      transform: translateY(100px);
      opacity: 0;
    }
    100% {
      transform: translateY(0);
      opacity: 1;
    }
  }
</style>