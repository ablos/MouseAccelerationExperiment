<script>
    import { onMount, getContext } from 'svelte';
    import SliderTarget from './SliderTarget.svelte';
    import { TaskStatus } from '$lib/enums';
    import { TaskType } from '$lib/enums';
    import { createMouseSampler } from './MouseSampler';
	import { Task, MouseCoordinate } from '$lib/dataTypes';

    const ZONE_WIDTHS = [20, 40, 80];
    const DISTANCES   = [100, 250, 500];

    let trials       = $state([]);
    let currentIndex = $state(0);
    let status       = $state(TaskStatus.IDLE);
    let allowSampling = $state(false);

    let trial = $derived(trials[currentIndex]);

    const { onComplete, debugMode } = getContext('task');

    let currentTask = new Task(TaskType.SLIDER);
    let currentTrialRef = null;

    trials = buildTrials()
    
    function onMouseSample(x, y, timestamp) {
        if(allowSampling && currentTrialRef){
            currentTrialRef.addCoordinate(new MouseCoordinate(x, y, timestamp));
        }
    }

    const sampler = createMouseSampler(onMouseSample);

    
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
    sampler.start()
    // Clean up function for event listeners
    return () => {
        sampler.stop();
    } 
  });

  function nextTrial() {
    
    if (currentIndex + 1 >= trials.length - (debugMode ? 15 : 0)) {
        endTask()
    } else {
        currentIndex++;
    }
  }

  function endTask(){
    currentTask.complete()
    status = TaskStatus.DONE;
    sampler.stop();
    console.log(currentTask)
    onComplete(currentTask)
  }
  function startTask(){
    if(status === TaskStatus.IDLE)
        status = TaskStatus.RUNNING
  }

</script>

<div class="screen" role="button" tabindex="0" onmousedown={startTask} onkeydown={startTask}>

  <!-- {#if status === TaskStatus.RUNNING} -->
    
    <div class="arena">
      {#key currentIndex}
        <SliderTarget
          zoneWidth={trial.size}
          distance={trial.distance}
          enableSampling={() => { allowSampling = true }}
          disableSampling={() => { allowSampling = false }}
          {nextTrial}
          {currentTask}
          onTrialReady={(trial) => { currentTrialRef = trial }}
        />
      {/key}
    </div>
    <!-- {:else if status === TaskStatus.IDLE}
      <div  class="text-2xl font-bold" >Please click anywhere to start the next task</div> -->
  <!-- {/if} -->
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

</style>