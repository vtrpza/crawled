<script>
  import { intelligentSuggestions } from '../lib/config.js'
  
  let { intent, extractionQuery = $bindable('') } = $props()
  
  function getSuggestions() {
    return intelligentSuggestions[intent?.type] || intelligentSuggestions.general || []
  }
  
  function handleSuggestionClick(suggestion) {
    extractionQuery = suggestion
  }
</script>

<div class="mb-4">
  <div class="relative mb-6">
    <input 
      type="text" 
      bind:value={extractionQuery}
      class="cyber-input w-full pr-4 py-4 text-sm font-mono" 
      placeholder="// Describe what specific data you want to extract..."
    />
    <div class="absolute inset-y-0 right-0 pr-5 flex items-center">
      <span class="text-xs font-mono text-neon-cyan/70">AI_POWERED</span>
    </div>
  </div>
  
  <div class="mb-6">
    <div class="text-xs font-mono text-gray-400 mb-3">
      SUGGESTED_QUERIES_FOR_{intent?.type?.toUpperCase() || 'GENERAL'}:
    </div>
    <div class="flex flex-wrap gap-3">
      {#each getSuggestions() as suggestion}
        <button 
          onclick={() => handleSuggestionClick(suggestion)}
          class="px-3 py-1.5 bg-cyber-gray hover:bg-neon-{intent?.color || 'cyan'}/20 border border-neon-{intent?.color || 'cyan'}/30 hover:border-neon-{intent?.color || 'cyan'}/70 rounded text-xs font-mono text-neon-{intent?.color || 'cyan'} hover:text-neon-{intent?.color || 'cyan'} transition-all duration-200 hover:shadow-cyber-glow cursor-pointer"
        >
          {suggestion}
        </button>
      {/each}
    </div>
  </div>
</div>