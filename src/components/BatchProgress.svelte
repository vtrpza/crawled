<script>
  let { batchProgress } = $props()
  
  const { total, completed, current, failed, progress } = $derived(batchProgress || {})
</script>

{#if batchProgress}
  <div class="cyber-card p-8 mb-10 animate-scale-in">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <div class="text-2xl animate-pulse">🚀</div>
        <div>
          <h3 class="font-bold font-mono text-neon-cyan text-lg">BATCH_OPERATION</h3>
          <p class="text-sm font-mono text-gray-300 mt-1">Processing {total} targets</p>
        </div>
      </div>
      <div class="text-right">
        <div class="font-mono text-neon-cyan text-lg">{completed}/{total}</div>
        <div class="text-sm font-mono text-gray-400 mt-1">
          {failed > 0 ? `${failed} failed` : 'No failures'}
        </div>
      </div>
    </div>
    
    <!-- Progress Bar -->
    <div class="relative h-3 bg-cyber-dark rounded-full overflow-hidden mb-6">
      <div 
        class="absolute left-0 top-0 h-full bg-gradient-to-r from-neon-cyan to-neon-lime transition-all duration-500 animate-pulse" 
        style="width: {progress}%"
      ></div>
      <div 
        class="absolute left-0 top-0 h-full bg-neon-red transition-all duration-500" 
        style="width: {(failed/total)*100}%; left: {progress}%"
      ></div>
    </div>
    
    <!-- Current Processing -->
    {#if current}
      <div class="flex items-center gap-3 text-sm font-mono">
        <span class="text-neon-cyan animate-pulse">»</span>
        <span class="text-gray-300">PROCESSING:</span>
        <span class="text-neon-lime truncate">{current}</span>
      </div>
    {/if}
  </div>
{/if}