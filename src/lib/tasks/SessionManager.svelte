<script>
	import { TaskType } from "$lib/enums";
	import { onMount, setContext } from "svelte";
    import ClickTask from "./ClickTask.svelte";
	import DraggingTask from "./DraggingTask.svelte";
	import SliderTask from "./SliderTask.svelte";
    
    let { pxPerMm } = $props();

    const taskOrder = [TaskType.CLICKING, TaskType.SLIDER, TaskType.DRAGGING]
    let currentTaskIndex = $state(0);
    // let screenWidth = $state(0);
    // let screenHeight = $state(0);
    let isFullscreen = $state(false);
    let sessionId = null;

    async function onStart() {
        // TODO: Remove this in production obviously
        const participantResult = await fetch('/api/create-participant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({

            })
        });
        const { participantId } = await participantResult.json();

        // Create session in DB
        const sessionResult = await fetch('/api/create-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                participantId,
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
            currentTaskIndex++;
    }

    // Runs on client after page load
    onMount(onStart);
    setContext('task', {
        get pxPerMm() { return pxPerMm },
        get isFullscreen() {return isFullscreen},
        // get screenWidth() {return screenWidth},
        // get screenHeight() {return screenHeight},
        setIsFullscreen: (val) => {isFullscreen = val},
        onComplete,
    })
</script>

{#if taskOrder[currentTaskIndex] === TaskType.CLICKING}
    <ClickTask />
{:else if taskOrder[currentTaskIndex] === TaskType.SLIDER }
    <SliderTask />
{:else if taskOrder[currentTaskIndex] === TaskType.DRAGGING }
    <DraggingTask />
{:else}
    <div>Task not found</div>
{/if}

