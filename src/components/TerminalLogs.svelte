<script>
  let { logs = [], onClear } = $props()
</script>

<div class="cyber-card p-8 mb-10 animate-scale-in">
  <div class="flex items-center gap-4 mb-6">
    <div class="text-2xl">💻</div>
    <h3 class="font-bold font-mono text-neon-green text-lg">TERMINAL_LOG</h3>
    <button 
      onclick={onClear}
      class="ml-auto text-xs font-mono text-gray-400 hover:text-neon-cyan transition-colors"
    >
      CLEAR_LOG
    </button>
  </div>
  
  <!-- Terminal Display -->
  <div class="bg-cyber-black border border-neon-green/30 rounded-lg p-5 font-mono text-sm max-h-64 overflow-y-auto">
    <div class="text-neon-green mb-3">CRAWLED@neural-crawler:~$</div>
    {#each logs as log}
      <div class="mb-2">
        <span class="text-gray-500">[{log.timestamp}]</span>
        <span class="text-{log.level === 'error' ? 'neon-red' : log.level === 'success' ? 'neon-green' : 'neon-cyan'} ml-2">
          {log.message}
        </span>
      </div>
    {/each}
    <div class="text-neon-green animate-pulse mt-2">█</div>
  </div>
</div>