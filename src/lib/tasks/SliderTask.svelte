<script>
  import { onMount } from 'svelte';
  import SliderTarget from './SliderTarget.svelte';
	import { TaskStatus } from '$lib/enums';
  import { TaskType } from '$lib/enums';

  const ZONE_WIDTHS = [20, 40, 80];
  const DISTANCES   = [100, 250, 500];

  let screenWidth  = $state(1920);
  let screenHeight = $state(1080);

  let trials       = $state([]);
  let currentIndex = $state(0);
  let results      = $state([]);
  let status       = $state(TaskStatus.IDLE);

  let trial = $derived(trials[currentIndex]);

  let {pxPerMm, changeTaskType} = $props();

  function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function buildTrials() {
    const combos = ZONE_WIDTHS.flatMap(size =>
      DISTANCES.map(distance => ({ size, distance }))
    );
    return shuffle([...combos, ...combos]);
  }

  onMount(() => {
    screenWidth  = window.screen.width;
    screenHeight = window.screen.height;
    
    trials = buildTrials();
    status = TaskStatus.RUNNING
  });

  function handleCommit(result) {
    results = [...results, {
      trial:        currentIndex + 1,
      zoneWidth:    trial.size,
      distance:     trial.distance,
      ...result,
    }];

    // Short delay so user sees the zone highlight before advancing
    setTimeout(() => {
      // -15 only for debugging
      if (currentIndex + 1 >= trials.length - 15) {
        status = TaskStatus.DONE;
        changeTaskType(TaskType.DRAGGING)
        
      } else {
        currentIndex++;
      }
    }, 200);
  }

</script>

<div class="screen">
  {#if status === TaskStatus.DONE}
    <div class="done">
      <div class="score">THANKS. TBC</div>
      
    </div>

  {:else if status == TaskStatus.RUNNING}
    
    <div class="arena">
      {#key currentIndex}
        <SliderTarget
          zoneWidth={trial.size}
          distance={trial.distance}
          onCommit={handleCommit}
        />
      {/key}
    </div>
  {/if}
</div>

<style>
  .screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: #f0f0f0;
    color: black;
    font-family: system-ui, sans-serif;
    gap: 2rem;
    padding: 2rem;
  }


  .arena {
    background: white;
    border: 1px solid #2a2a35;
    border-radius: 12px;
    padding: 4rem 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: min(900px, 95vw);
  }

  .done {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }

  .score {
    font-size: 5rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    line-height: 1;
  }

  .btn {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.65rem 1.4rem;
    border-radius: 6px;
    border: 1.5px solid #2a2a35;
    background: transparent;
    color: #f0f0f0;
    cursor: pointer;
    transition: all 0.15s;
  }

  .btn:hover {
    border-color: #e8ff5a;
    color: #e8ff5a;
  }
</style>