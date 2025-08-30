<script>
  import AnalysisDashboard from './AnalysisDashboard.svelte'
  
  let { results } = $props()
  
  const isError = $derived(results?.status === 'error')
  const isBatch = $derived(results?.batch_results && results.batch_results.length > 0)
  const hasStealthFeatures = $derived(results?.stealth_features_v0_7 || results?.stealth_features)
  
  let showDashboard = $state(true)
  let showRawData = $state(false)
</script>

<div class="cyber-card p-10 animate-slide-up">
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
      </div>
    </div>
    
    {#if !isError}
      <div class="flex items-center gap-3">
        <button
          class="px-4 py-2 bg-cyber-dark/50 border border-{showDashboard ? 'neon-cyan' : 'gray-500'}/30 rounded-lg font-mono text-xs text-{showDashboard ? 'neon-cyan' : 'gray-400'} hover:border-neon-cyan/50 hover:text-neon-cyan transition-all duration-200 {showDashboard ? 'bg-neon-cyan/10' : ''}"
          onclick={() => { showDashboard = !showDashboard }}
        >
          📊 ANALYTICS
        </button>
        <button
          class="px-4 py-2 bg-cyber-dark/50 border border-{showRawData ? 'neon-purple' : 'gray-500'}/30 rounded-lg font-mono text-xs text-{showRawData ? 'neon-purple' : 'gray-400'} hover:border-neon-purple/50 hover:text-neon-purple transition-all duration-200 {showRawData ? 'bg-neon-purple/10' : ''}"
          onclick={() => { showRawData = !showRawData }}
        >
          📋 RAW_DATA
        </button>
      </div>
    {/if}
  </div>

  {#if showDashboard}
    <AnalysisDashboard {results} />
  {/if}

  {#if showRawData && isBatch}
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
    
    <!-- Batch Results Grid -->
    <div class="space-y-6">
      {#if results.batch_results.filter(r => r.status === 'success').length > 0}
        {@const successful = results.batch_results.filter(r => r.status === 'success')}
        <div>
          <h4 class="font-bold font-mono text-neon-green mb-4">✓ SUCCESSFUL_EXTRACTIONS ({successful.length})</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            {#each successful.slice(0, 4) as result}
              <div class="bg-cyber-gray/30 border border-neon-green/30 rounded-lg p-5">
                <div class="text-xs font-mono text-neon-green mb-3">{result.url}</div>
                <div class="text-sm font-mono text-gray-300">{result.title || 'No title'}</div>
                <div class="text-xs font-mono text-gray-400 mt-3">
                  Content: {result.content ? result.content.length + ' chars' : 'None'}
                </div>
              </div>
            {/each}
          </div>
          {#if successful.length > 4}
            <div class="text-xs font-mono text-gray-400 mt-3">... and {successful.length - 4} more successful extractions</div>
          {/if}
        </div>
      {/if}
      
      {#if results.batch_results.filter(r => r.status === 'error').length > 0}
        {@const failed = results.batch_results.filter(r => r.status === 'error')}
        <div>
          <h4 class="font-bold font-mono text-neon-red mb-4">✗ FAILED_EXTRACTIONS ({failed.length})</h4>
          <div class="space-y-3">
            {#each failed.slice(0, 3) as result}
              <div class="bg-cyber-gray/30 border border-neon-red/30 rounded-lg p-4">
                <div class="text-xs font-mono text-neon-red mb-2">{result.url}</div>
                <div class="text-xs font-mono text-gray-300">{result.error}</div>
              </div>
            {/each}
          </div>
          {#if failed.length > 3}
            <div class="text-xs font-mono text-gray-400 mt-3">... and {failed.length - 3} more failures</div>
          {/if}
        </div>
      {/if}
    </div>
  {:else if showRawData && isError}
    <div class="bg-cyber-dark/50 border border-neon-red/50 rounded-lg p-8">
      <h4 class="font-bold font-mono text-neon-red mb-4">ERROR_DETAILS:</h4>
      <p class="text-sm font-mono text-gray-300 mb-5">{results.error || 'Unknown system malfunction'}</p>
      {#if results.suggestion}
        <div class="border-t border-neon-red/30 pt-4 mt-4">
          <div class="text-xs font-mono text-neon-red mb-2">RECOVERY_PROTOCOL:</div>
          <p class="text-sm font-mono text-gray-300">{results.suggestion}</p>
        </div>
      {/if}
    </div>
  {:else if showRawData}
    <!-- Success Results -->
    <div class="space-y-8">
      <!-- Enhanced Basic Info with Performance Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-slate-50 rounded-lg p-5">
          <div class="text-sm font-medium text-slate-600 mb-2">URL</div>
          <div class="text-slate-900 break-all">{results.url}</div>
          {#if results.crawl_duration || results.processing_time}
            <div class="mt-3 pt-3 border-t border-slate-200">
              <div class="flex items-center gap-4 text-xs">
                {#if results.crawl_duration}
                  <div class="flex items-center gap-1">
                    <span class="text-slate-500">⏱️ Crawl:</span>
                    <span class="font-mono text-slate-700">{results.crawl_duration}ms</span>
                  </div>
                {/if}
                {#if results.processing_time}
                  <div class="flex items-center gap-1">
                    <span class="text-slate-500">⚙️ Process:</span>
                    <span class="font-mono text-slate-700">{results.processing_time}ms</span>
                  </div>
                {/if}
              </div>
            </div>
          {/if}
        </div>
        <div class="bg-slate-50 rounded-lg p-5">
          <div class="text-sm font-medium text-slate-600 mb-2">Title</div>
          <div class="text-slate-900">{results.title || 'No title'}</div>
          {#if results.metadata}
            <div class="mt-3 pt-3 border-t border-slate-200 space-y-1">
              {#if results.metadata.description}
                <div class="text-xs text-slate-600">
                  <span class="font-medium">Description:</span> {results.metadata.description.slice(0, 100)}{results.metadata.description.length > 100 ? '...' : ''}
                </div>
              {/if}
              {#if results.metadata.keywords}
                <div class="text-xs text-slate-600">
                  <span class="font-medium">Keywords:</span> {results.metadata.keywords.slice(0, 5).join(', ')}
                </div>
              {/if}
            </div>
          {/if}
        </div>
      </div>

      <!-- Content Statistics -->
      {#if results.content || results.statistics}
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
            <div class="text-xs font-medium text-blue-600 mb-1">Content Size</div>
            <div class="text-lg font-bold text-blue-900">{results.content ? `${(results.content.length / 1024).toFixed(1)} KB` : '0 KB'}</div>
          </div>
          {#if results.statistics?.word_count || results.word_count}
            <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
              <div class="text-xs font-medium text-green-600 mb-1">Word Count</div>
              <div class="text-lg font-bold text-green-900">{(results.statistics?.word_count || results.word_count || 0).toLocaleString()}</div>
            </div>
          {/if}
          {#if results.statistics?.paragraph_count || results.paragraph_count}
            <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
              <div class="text-xs font-medium text-purple-600 mb-1">Paragraphs</div>
              <div class="text-lg font-bold text-purple-900">{results.statistics?.paragraph_count || results.paragraph_count || 0}</div>
            </div>
          {/if}
          {#if results.statistics?.readability_score || results.readability_score}
            <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4">
              <div class="text-xs font-medium text-orange-600 mb-1">Readability</div>
              <div class="text-lg font-bold text-orange-900">{results.statistics?.readability_score || results.readability_score || 'N/A'}</div>
            </div>
          {/if}
        </div>
      {/if}

      {#if hasStealthFeatures}
        <!-- Stealth Features -->
        <div class="bg-gradient-to-r from-stealth-50 to-slate-50 border border-stealth-200 rounded-lg p-7">
          <h4 class="font-semibold text-stealth-900 mb-5 flex items-center gap-2">
            🥷 Stealth Features Active
          </h4>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-5 text-sm">
            {#each Object.entries(results.stealth_features_v0_7 || results.stealth_features) as [key, value]}
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full {value ? 'bg-green-500' : 'bg-slate-300'}"></div>
                <span class="text-slate-700">{key.replace(/_/g, ' ')}</span>
              </div>
            {/each}
          </div>
          {#if results.browser_fingerprint}
            <div class="mt-5 pt-5 border-t border-stealth-200">
              <div class="text-sm text-stealth-600">
                <strong>Browser:</strong> {results.browser_fingerprint.user_agent || 'Randomized'}
              </div>
            </div>
          {/if}
        </div>
      {/if}

      <!-- AI Analysis (if available) -->
      {#if results.ai_analysis || results.extracted_content}
        <div>
          <div class="flex items-center justify-between mb-5">
            <h4 class="font-semibold text-slate-900 flex items-center gap-2">
              <span>🤖</span> AI-Extracted Content
            </h4>
            <div class="text-sm text-slate-500">
              {(results.ai_analysis || results.extracted_content) ? `${(results.ai_analysis || results.extracted_content).length} characters` : 'No content'}
            </div>
          </div>
          <div class="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-6 max-h-96 overflow-y-auto">
            <pre class="whitespace-pre-wrap text-sm text-slate-700 font-mono leading-relaxed">
{results.ai_analysis || results.extracted_content || 'No AI analysis available'}
            </pre>
          </div>
        </div>
      {/if}

      <!-- Raw Content -->
      <div>
        <div class="flex items-center justify-between mb-5">
          <h4 class="font-semibold text-slate-900">
            {results.ai_analysis || results.extracted_content ? 'Raw Extracted Content' : 'Extracted Content'}
          </h4>
          <div class="text-sm text-slate-500">
            {results.content ? `${results.content.length} characters` : 'No content'}
          </div>
        </div>
        <div class="bg-slate-50 border border-slate-200 rounded-lg p-6 max-h-96 overflow-y-auto">
          <pre class="whitespace-pre-wrap text-sm text-slate-700 font-mono leading-relaxed">
{results.content || 'No content extracted'}
          </pre>
        </div>
      </div>

      <!-- Additional Data -->
      {#if (results.links?.internal?.length > 0 || results.links?.external?.length > 0 || results.discovered_urls?.length > 0)}
        <div>
          <h4 class="font-semibold text-slate-900 mb-5">
            {results.discovered_urls ? 'Intelligent URL Discovery' : 'Links Found'}
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-{results.discovered_urls ? '3' : '2'} gap-6">
            {#if results.discovered_urls}
              <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-5">
                <div class="font-medium text-indigo-900 mb-3">Discovered URLs</div>
                <div class="text-sm text-indigo-700">
                  {results.discovered_urls.length || 0} high-quality URLs
                </div>
                <div class="text-xs text-indigo-600 mt-2">
                  Avg Score: {results.avg_relevance_score || 'N/A'}
                </div>
              </div>
            {/if}
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-5">
              <div class="font-medium text-blue-900 mb-3">Internal Links</div>
              <div class="text-sm text-blue-700">
                {results.links?.internal?.length || 0} found
              </div>
            </div>
            <div class="bg-green-50 border border-green-200 rounded-lg p-5">
              <div class="font-medium text-green-900 mb-3">External Links</div>
              <div class="text-sm text-green-700">
                {results.links?.external?.length || 0} found
              </div>
            </div>
          </div>
        </div>
      {/if}

      {#if (results.media?.images?.length > 0 || results.media?.videos?.length > 0 || results.media?.audios?.length > 0)}
        <div>
          <h4 class="font-semibold text-slate-900 mb-5 flex items-center gap-2">
            <span>📸</span> Media Detection Analysis
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-gradient-to-br from-pink-50 to-pink-100 border border-pink-200 rounded-lg p-5">
              <div class="flex items-center justify-between mb-3">
                <div class="font-medium text-pink-900">Images</div>
                <span class="text-2xl">🖼️</span>
              </div>
              <div class="text-2xl font-bold text-pink-900 mb-2">
                {results.media.images?.length || 0}
              </div>
              {#if results.media.images?.length > 0}
                <div class="text-xs text-pink-600">
                  {#if results.media.images[0].alt}
                    Sample: "{results.media.images[0].alt.slice(0, 30)}{results.media.images[0].alt.length > 30 ? '...' : ''}"
                  {:else}
                    Various formats detected
                  {/if}
                </div>
              {/if}
            </div>
            <div class="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-5">
              <div class="flex items-center justify-between mb-3">
                <div class="font-medium text-purple-900">Videos</div>
                <span class="text-2xl">🎬</span>
              </div>
              <div class="text-2xl font-bold text-purple-900 mb-2">
                {results.media.videos?.length || 0}
              </div>
              {#if results.media.videos?.length > 0}
                <div class="text-xs text-purple-600">
                  Embedded video content found
                </div>
              {/if}
            </div>
            <div class="bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200 rounded-lg p-5">
              <div class="flex items-center justify-between mb-3">
                <div class="font-medium text-indigo-900">Audio</div>
                <span class="text-2xl">🎵</span>
              </div>
              <div class="text-2xl font-bold text-indigo-900 mb-2">
                {results.media.audios?.length || 0}
              </div>
              {#if results.media.audios?.length > 0}
                <div class="text-xs text-indigo-600">
                  Audio tracks detected
                </div>
              {/if}
            </div>
          </div>
          
          {#if results.media.total_size || results.media.optimized}
            <div class="mt-4 p-3 bg-slate-100 rounded-lg">
              <div class="flex items-center justify-between text-sm">
                {#if results.media.total_size}
                  <div class="text-slate-600">
                    <span class="font-medium">Total Media Size:</span> {(results.media.total_size / 1024 / 1024).toFixed(2)} MB
                  </div>
                {/if}
                {#if results.media.optimized}
                  <div class="text-green-600 font-medium">
                    ✓ Optimized for performance
                  </div>
                {/if}
              </div>
            </div>
          {/if}
        </div>
      {/if}
      
      <!-- Deep Crawl Results (if available) -->
      {#if results.deep_crawl_results}
        <div>
          <h4 class="font-semibold text-slate-900 mb-5 flex items-center gap-2">
            <span>🕷️</span> Deep Crawl Analysis
          </h4>
          <div class="bg-gradient-to-r from-cyan-50 to-blue-50 border border-cyan-200 rounded-lg p-6">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <div class="text-xs font-medium text-cyan-600 mb-1">Pages Crawled</div>
                <div class="text-xl font-bold text-cyan-900">{results.deep_crawl_results.pages_crawled || 0}</div>
              </div>
              <div>
                <div class="text-xs font-medium text-blue-600 mb-1">Max Depth</div>
                <div class="text-xl font-bold text-blue-900">{results.deep_crawl_results.max_depth || 0}</div>
              </div>
              <div>
                <div class="text-xs font-medium text-cyan-600 mb-1">Total Links</div>
                <div class="text-xl font-bold text-cyan-900">{results.deep_crawl_results.total_links || 0}</div>
              </div>
              <div>
                <div class="text-xs font-medium text-blue-600 mb-1">Crawl Time</div>
                <div class="text-xl font-bold text-blue-900">{results.deep_crawl_results.crawl_time || 'N/A'}</div>
              </div>
            </div>
            {#if results.deep_crawl_results.sitemap}
              <div class="mt-4 pt-4 border-t border-cyan-200">
                <div class="text-sm font-medium text-cyan-700 mb-2">Site Structure</div>
                <div class="text-xs text-cyan-600">
                  {results.deep_crawl_results.sitemap.slice(0, 200)}{results.deep_crawl_results.sitemap.length > 200 ? '...' : ''}
                </div>
              </div>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>