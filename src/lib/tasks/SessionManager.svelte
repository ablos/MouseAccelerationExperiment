<script>
	import { TaskType } from "$lib/enums";
	import { onMount, setContext } from "svelte";
    import ClickTask from "./ClickTask.svelte";
	import DraggingTask from "./DraggingTask.svelte";
	import SliderTask from "./SliderTask.svelte";
	import TaskExplanation from "./TaskExplanation.svelte";
	import { goto } from "$app/navigation";
	import Button from "$lib/components/ui/button/button.svelte";
	import * as Card from "$lib/components/ui/card";
	import Checkbox from "$lib/components/ui/checkbox/checkbox.svelte";
	import Label from "$lib/components/ui/label/label.svelte";
	import Slider from "$lib/components/ui/slider/slider.svelte";
    
    let { pxPerMm, isFirstSession, slot, group } = $props();
    
    let didCheck = $state(false);
    let samePC = $state(false);
    let sameSetting = $state(false);
    let sameMouse = $state(false);
    let hoursSinceLastSession = $state(0);

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
                pxPerMm,
                devicePixelRatio: window.devicePixelRatio,
                userAgent: navigator.userAgent,
                hoursSinceLastSession,
                slot
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

    onMount(() =>
    {
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
<div bind:this={container} class="w-screen h-screen bg-background text-foreground">
    {#if !didCheck && !isFirstSession}
        <div class="flex w-full h-full justify-center items-center">
            <Card.Root class="-my-4 w-full max-w-sm">
                <Card.Header>
                    <Card.Title>Before we begin</Card.Title>
                    <Card.Description>Confirm your setup is the same as your previous session.</Card.Description>
                </Card.Header>
                
                <Card.Content class="flex flex-col gap-3">
                    <div class="flex items-start gap-3">
                        <Checkbox id="same-pc" bind:checked={samePC} />
                        <Label for="same-pc">This PC is the same as previous sessions.</Label>
                    </div>
                    
                    <div class="flex items-start gap-3">
                        <Checkbox id="same-setting" bind:checked={sameSetting} />
                        <div class="flex flex-col gap-1">
                            <Label for="same-setting">
                                {#if group === 'control'}
                                    My mouse acceleration setting is <strong>ON</strong>.
                                {:else if group === 'experimental'}
                                    My mouse acceleration setting is <strong>OFF</strong>.
                                {:else}
                                    My mouse acceleration setting is the assigned setting.
                                {/if}
                            </Label>
                            <p class="text-xs text-muted-foreground">
                                Need help finding this setting?
                                <a href="/tutorials/windows.pdf" target="_blank" class="underline">Windows</a>
                                /
                                <a href="/tutorials/macos.pdf" target="_blank" class="underline">macOS</a>
                            </p>
                        </div>
                    </div>
                    
                    <div class="flex items-start gap-3 mb-6">
                        <Checkbox id="same-mouse" bind:checked={sameMouse} />
                        <Label for="same-mouse">I use the same mouse (not a trackpad) as previous sessions.</Label>
                    </div>
                    
                    <Label>Approximately how many hours did you use this computer since last session?</Label>
                    <div class="flex gap-2 justify-between items-center">
                        <span class="text-sm">0</span>
                        <Slider class="flex-1" type="single" bind:value={hoursSinceLastSession} max={48} step={1} />
                        <span class="text-sm">48</span>
                    </div>
                    
                    <span class="text-sm text-muted-foreground mx-auto mb-2">~{hoursSinceLastSession} hours since last session</span>
                </Card.Content>
                
                <Card.Footer>
                    <Button class="w-full" disabled={!samePC || !sameMouse || !sameSetting || hoursSinceLastSession == 0} onclick={() => didCheck = true}>Start</Button>
                </Card.Footer>
            </Card.Root>
        </div>
    {:else}
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
            <TaskExplanation taskType={taskOrder[currentTaskIndex]} onstart={async () => { if (!sessionId) await onStart(); taskExplained = true; }} />
        {:else if taskOrder[currentTaskIndex] === TaskType.CLICKING}
            <ClickTask />
        {:else if taskOrder[currentTaskIndex] === TaskType.SLIDER }
            <SliderTask />
        {:else if taskOrder[currentTaskIndex] === TaskType.DRAGGING }
            <DraggingTask />
        {:else}
            <div>Task not found</div>
        {/if}
    {/if}
</div>




