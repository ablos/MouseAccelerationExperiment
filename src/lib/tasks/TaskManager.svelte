<script>
	import { TaskType } from "$lib/enums";
    import RequestFullscreen from '$lib/RequestFullscreen.svelte';
    import { onMount, setContext } from "svelte";
    import ClickTask from "./ClickTask.svelte";
	import DraggingTask from "./DraggingTask.svelte";
	import SliderTask from "./SliderTask.svelte";
    
    let { pxPerMm } = $props();

    const taskOrder = [TaskType.CLICKING, TaskType.SLIDER, TaskType.DRAGGING]

    let screenWidth = $state(0);
    let screenHeight = $state(0);

    let currentTaskIndex = $state(0)
    let isFullscreen = $state(false);

    
    function onComplete(taskType) {
        currentTaskIndex++;
    }

        // handles fullscreen change
    function handleFullscreenChange() {
        isFullscreen = !!document.fullscreenElement;
        console.log("B"+isFullscreen)
        // center target
        setTimeout(() => {
            screenWidth = window.innerWidth;
            screenHeight = window.innerHeight;
            
        }, 100);
    }

    function toggleFullscreen(){
        document.documentElement.requestFullscreen();
        isFullscreen = !isFullscreen
    }

    onMount(()=>{
        // Detect fullscreen state
        isFullscreen = !!document.fullscreenElement;
        console.log("A"+isFullscreen)
        handleFullscreenChange();
        document.addEventListener('fullscreenchange', handleFullscreenChange);

        return () => {
            document.removeEventListener('fullscreenchange', handleFullscreenChange)
        }
    })

    setContext('task', {
        get pxPerMm() { return pxPerMm },
        get isFullscreen() {return isFullscreen},
        get screenWidth() {return screenWidth},
        get screenHeight() {return screenHeight},
        onComplete,
        toggleFullscreen,
    })

</script>
{#if isFullscreen}
    {#if taskOrder[currentTaskIndex] === TaskType.CLICKING}
        <ClickTask />
    {:else if taskOrder[currentTaskIndex] === TaskType.SLIDER }
        <SliderTask />
    {:else if taskOrder[currentTaskIndex] === TaskType.DRAGGING }
        <DraggingTask />
    {:else}
        <div>Task not found</div>
    {/if}
{:else}
    <RequestFullscreen />
{/if}

