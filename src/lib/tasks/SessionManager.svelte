<script>
	import { TaskType } from "$lib/enums";
	import { onMount, setContext } from "svelte";
    import ClickTask from "./ClickTask.svelte";
	import DraggingTask from "./DraggingTask.svelte";
	import SliderTask from "./SliderTask.svelte";
	import TaskExplanation from "./TaskExplanation.svelte";
	import { goto } from "$app/navigation";
	import Button from "$lib/components/ui/button/button.svelte";
    
    let { pxPerMm } = $props();

    const taskOrder = [TaskType.CLICKING, TaskType.SLIDER, TaskType.DRAGGING]
    let currentTaskIndex = $state(0);
    let isFullscreen = $state(false);
    let sessionId = null;
    let container = $state(null);
    let taskExplained = $state(false);
    let wasInterrupted = $state(false);
    
    let debugMode = $state(false);

    async function onStart() {
        // Create session in DB
        const sessionResult = await fetch('/api/create-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                screenResX: window.screen.width,
                screenResY: window.screen.height,
                pxPerMm
            })
        });

        const data = await sessionResult.json();
        sessionId = data.sessionId;
    }
    
    async function onComplete() {
        // Close session on DB
        await fetch(`/api/close-session/${sessionId}`, { method: 'PATCH' });
        goto('/done');
    }

    async function onTaskComplete(task) {
        // Set session id
        task.sessionId = sessionId;

        // Send task to DB
        await fetch('/api/save-task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(task)
        });

        // Check if done or go to next
        if (currentTaskIndex >= taskOrder.length - 1)
            onComplete();
        else 
        {
            taskExplained = false;
            currentTaskIndex++;
        }
    }
    
    function onFullscreenChange() 
    {
        isFullscreen = !!document.fullscreenElement;
        
        if (!isFullscreen && taskExplained) 
        {
            wasInterrupted = true;
            taskExplained = false;
        }
        
        if (isFullscreen)
            wasInterrupted = false;
    }

    // Runs on client after page load
    onMount(() => 
    {
        onStart();
        
        // Listen for fullscreen event
        container.addEventListener('fullscreenchange', onFullscreenChange);
        return () => container.removeEventListener('fullscreenchange', onFullscreenChange);
    });
    
    setContext('task', {
        get pxPerMm() { return pxPerMm },
        get debugMode() { return debugMode },
        onComplete: onTaskComplete,
    });
</script>

<!-- wrapper element should be referenced to keep fullscreen mode throughout the application -->
<div bind:this={container} class="w-screen h-screen">
    {#if !isFullscreen}
        <div class="flex flex-col items-center justify-center w-screen h-screen gap-4">
            <h1 class="text-2xl font-bold">Please go into fullcreen by clicking the button below</h1>
            
            {#if wasInterrupted}
                <p class="text-sm text-muted-foreground">You exited fullscreen. The current task will restart from the beginning.</p>
            {/if}
            
            <Button onclick={() => container.requestFullscreen()}>
                Enable Fullscreen
            </Button>
        </div>
    {:else if !taskExplained}
        <TaskExplanation taskType={taskOrder[currentTaskIndex]} onstart={() => taskExplained = true} />
    {:else if taskOrder[currentTaskIndex] === TaskType.CLICKING}
        <ClickTask />
    {:else if taskOrder[currentTaskIndex] === TaskType.SLIDER }
        <SliderTask />
    {:else if taskOrder[currentTaskIndex] === TaskType.DRAGGING }
        <DraggingTask />
    {:else}
        <div>Task not found</div>
    {/if}
</div>




