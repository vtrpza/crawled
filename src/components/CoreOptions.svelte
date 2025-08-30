<script>
  let { 
    intent, 
    aiModel = $bindable('groq'),  // Default to Groq for AI-first experience
    outputFormat = $bindable('markdown'),
    enableCache = $bindable(true),
    includeMedia = $bindable(false),
    batchUrls = $bindable(''),
    concurrent = $bindable(5),
    
    // AI-First Deep Crawl parameters
    maxPages = $bindable(5),
    maxDepth = $bindable(2),
    crawlStrategy = $bindable('bfs')
  } = $props()
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
  <!-- AI & Processing -->
  <div class="space-y-5">
    <div>
      <label for="ai-model-select" class="block text-sm font-mono text-neon-lime mb-3">AI_MODEL (MANDATORY):</label>
      <select id="ai-model-select" bind:value={aiModel} class="cyber-input border-neon-lime/50">
        <option value="groq">GROQ_FAST ⚡ (RECOMMENDED)</option>
        <option value="gpt-4">GPT-4</option>
        <option value="claude-3">CLAUDE-3</option>
        <option value="gemini-pro">GEMINI-PRO</option>
        <option value="ollama">OLLAMA_FREE</option>
      </select>
      <div class="text-xs font-mono text-neon-lime/70 mt-2">🤖 AI processing is mandatory - no opt-out</div>
    </div>
    
    <div class="flex items-center gap-4">
      <input 
        type="checkbox" 
        id="enable-cache"
        bind:checked={enableCache}
        class="w-4 h-4 accent-neon-cyan"
      />
      <label for="enable-cache" class="text-sm font-mono text-gray-300">NEURAL_CACHE</label>
    </div>
  </div>

  <!-- Output & Media -->
  <div class="space-y-5">
    <div>
      <label for="output-format-select" class="block text-sm font-mono text-gray-300 mb-3">OUTPUT_FORMAT:</label>
      <select id="output-format-select" bind:value={outputFormat} class="cyber-input">
        <option value="markdown">MARKDOWN</option>
        <option value="html">HTML_RAW</option>
        <option value="json">JSON_STRUCT</option>
      </select>
    </div>
    
    <div class="flex items-center gap-4">
      <input 
        type="checkbox" 
        id="include-media"
        bind:checked={includeMedia}
        class="w-4 h-4 accent-neon-lime"
      />
      <label for="include-media" class="text-sm font-mono text-gray-300">MEDIA_EXTRACTION</label>
    </div>
  </div>
</div>

<!-- AI-First Deep Crawl Options (Always Visible) -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 p-6 bg-neon-cyan/5 border border-neon-cyan/20 rounded-lg">
  <div class="md:col-span-3 mb-2">
    <div class="text-sm font-mono text-neon-cyan mb-2 flex items-center gap-2">
      <span class="text-neon-lime">🤖</span> AI_DEEP_CRAWL_SETTINGS:
    </div>
    <div class="text-xs font-mono text-gray-400">AI analyzes multiple pages automatically for comprehensive insights</div>
  </div>
  
  <div>
    <label for="max-pages-input" class="block text-sm font-mono text-gray-300 mb-3">MAX_PAGES:</label>
    <input 
      id="max-pages-input"
      type="number" 
      bind:value={maxPages}
      class="cyber-input" 
      min="1" 
      max="20"
      placeholder="5"
    />
    <div class="text-xs font-mono text-gray-400 mt-1">Pages to crawl (1-20)</div>
  </div>
  
  <div>
    <label for="max-depth-input" class="block text-sm font-mono text-gray-300 mb-3">MAX_DEPTH:</label>
    <input 
      id="max-depth-input"
      type="number" 
      bind:value={maxDepth}
      class="cyber-input" 
      min="1" 
      max="5"
      placeholder="2"
    />
    <div class="text-xs font-mono text-gray-400 mt-1">Link depth (1-5)</div>
  </div>
  
  <div>
    <label for="strategy-select" class="block text-sm font-mono text-gray-300 mb-3">STRATEGY:</label>
    <select id="strategy-select" bind:value={crawlStrategy} class="cyber-input">
      <option value="bfs">BFS_BREADTH_FIRST</option>
      <option value="dfs">DFS_DEPTH_FIRST</option>
    </select>
    <div class="text-xs font-mono text-gray-400 mt-1">Crawl pattern</div>
  </div>
</div>

<!-- Batch Mode (when applicable) -->
{#if intent?.type === 'batch'}
  <div class="mt-8 pt-6 border-t border-neon-cyan/20">
    <div class="space-y-5">
      <div>
        <label class="block text-sm font-mono text-gray-300 mb-3">BATCH_URLS:</label>
        <textarea 
          bind:value={batchUrls}
          class="cyber-input resize-none" 
          rows="4" 
          placeholder="https://target1.com&#10;https://target2.com&#10;https://target3.com"
        ></textarea>
        <div class="text-xs font-mono text-gray-400 mt-2">One URL per line</div>
      </div>
      
      <div class="w-52">
        <label class="block text-sm font-mono text-gray-300 mb-3">CONCURRENT_LIMIT:</label>
        <input 
          type="number" 
          bind:value={concurrent}
          class="cyber-input" 
          min="1" 
          max="25"
        />
      </div>
    </div>
  </div>
{/if}