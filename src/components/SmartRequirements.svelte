<script>
  import { smartRequirements } from '../lib/config.js'
  import { untrack } from 'svelte'
  
  let { intent, requirementsData = $bindable({}) } = $props()
  
  let initialized = false
  
  $effect(() => {
    // Only initialize once when intent changes
    const currentIntentType = intent?.type
    
    // Use untrack to read requirementsData without triggering the effect
    untrack(() => {
      const requirements = smartRequirements[currentIntentType] || smartRequirements.general || []
      const needsUpdate = requirements.some(req => 
        requirementsData[req.setting.key] === undefined
      )
      
      if (needsUpdate) {
        const newData = { ...requirementsData }
        requirements.forEach(req => {
          if (newData[req.setting.key] === undefined) {
            newData[req.setting.key] = req.setting.defaultValue
          }
        })
        requirementsData = newData
      }
    })
  })
  
  function getRequirements() {
    return smartRequirements[intent?.type] || smartRequirements.general || []
  }
  
  function handleToggle(key, value) {
    requirementsData[key] = value
  }
  
  function handleSelect(key, value) {
    requirementsData[key] = value
  }
  
  function handleNumber(key, value) {
    requirementsData[key] = parseInt(value)
  }
  
  function handleRange(key, value) {
    requirementsData[key] = parseInt(value)
  }
</script>

<div class="pt-6 border-t border-neon-cyan/30">
  <div class="text-sm font-mono text-neon-cyan mb-5 flex items-center gap-2">
    <span class="text-neon-pink">»</span> SMART_REQUIREMENTS_FOR_{intent?.type?.toUpperCase() || 'GENERAL'}:
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
    {#each getRequirements() as req}
      <div class="bg-cyber-dark/30 border border-neon-{req.color}/30 rounded-lg p-5 hover:border-neon-{req.color}/50 transition-colors">
        <div class="flex items-start gap-4">
          <div class="text-lg mt-1">{req.icon}</div>
          <div class="flex-1 min-w-0">
            <h4 class="font-bold font-mono text-neon-{req.color} text-sm mb-3">{req.title}</h4>
            <p class="text-xs text-gray-300 font-mono leading-relaxed mb-4">{req.description}</p>
            
            {#if req.setting}
              <div class="space-y-3">
                {#if req.setting.type === 'toggle'}
                  <div class="flex items-center gap-2">
                    <input 
                      type="checkbox" 
                      id={req.id}
                      checked={requirementsData[req.setting.key]}
                      onchange={(e) => handleToggle(req.setting.key, e.target.checked)}
                      class="w-4 h-4 accent-neon-cyan"
                    />
                    <label for={req.id} class="text-xs font-mono text-gray-300">ENABLED</label>
                  </div>
                {:else if req.setting.type === 'select'}
                  <select 
                    id={req.id}
                    value={requirementsData[req.setting.key]}
                    onchange={(e) => handleSelect(req.setting.key, e.target.value)}
                    class="cyber-input text-xs py-1"
                  >
                    {#each req.setting.options as option}
                      <option value={option}>{option.toUpperCase()}</option>
                    {/each}
                  </select>
                {:else if req.setting.type === 'number'}
                  <input 
                    type="number" 
                    id={req.id}
                    value={requirementsData[req.setting.key]}
                    onchange={(e) => handleNumber(req.setting.key, e.target.value)}
                    min={req.setting.min} 
                    max={req.setting.max}
                    class="cyber-input text-xs py-1 w-20"
                  />
                {:else if req.setting.type === 'range'}
                  <div class="flex items-center gap-2">
                    <input 
                      type="range" 
                      id={req.id}
                      value={requirementsData[req.setting.key]}
                      oninput={(e) => handleRange(req.setting.key, e.target.value)}
                      min={req.setting.min} 
                      max={req.setting.max}
                      class="flex-1 accent-neon-cyan"
                    />
                    <span class="text-xs font-mono text-neon-cyan w-6">
                      {requirementsData[req.setting.key]}s
                    </span>
                  </div>
                {/if}
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>