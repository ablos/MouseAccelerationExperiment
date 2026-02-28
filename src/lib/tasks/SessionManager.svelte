<script>
	import { TaskType } from "$lib/enums";
	import { onMount, setContext } from "svelte";
    import ClickTask from "./ClickTask.svelte";
	import DraggingTask from "./DraggingTask.svelte";
	import SliderTask from "./SliderTask.svelte";
	import RequestFullscreen from "$lib/RequestFullscreen.svelte";
	import TaskExplanation from "./TaskExplanation.svelte";
	import { goto } from "$app/navigation";
    
    let { pxPerMm } = $props();

    const taskOrder = [TaskType.CLICKING, TaskType.SLIDER, TaskType.DRAGGING]
    let currentTaskIndex = $state(0);
    let isFullscreen = $state(false);
    let sessionId = null;
    let container = $state(null);
    let taskExplained = $state(false);

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
    function enterFullscreen() {
        container.requestFullscreen();
        isFullscreen = true;
    }

    // Runs on client after page load
    onMount(onStart);
    setContext('task', {
        get pxPerMm() { return pxPerMm },
        get isFullscreen() {return isFullscreen},
        setIsFullscreen: (val) => {isFullscreen = val},
        onComplete: onTaskComplete,
    });
</script>

<!-- wrapper element should be referenced to keep fullscreen mode throughout the application -->
<div bind:this={container} class="w-screen h-screen bg-white">
    {#if !isFullscreen}
        <RequestFullscreen {enterFullscreen} />
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




