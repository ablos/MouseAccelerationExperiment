<script>
    import Button from "$lib/components/ui/button/button.svelte";
    import { TaskType } from "$lib/enums";
    
    let { taskType, onstart } = $props();
</script>

<div class="flex h-screen w-full justify-center items-center">
    <div class="flex flex-col max-w-200 gap-3 justify-center items-center">
        <h1 class="text-3xl font-semibold">
            {#if taskType === TaskType.CLICKING}
                Clicking task
            {:else if taskType === TaskType.SLIDER}
                Sliding Task
            {:else}
                Dragging Task
            {/if}
        </h1>
        
        <p>
            {#if taskType === TaskType.CLICKING}
                This is the clicking task, very nice explanation.
            {:else if taskType === TaskType.SLIDER}
                This is the sliding task, very nice explanation.
            {:else}
                This is the dragging task, very nice explanation.
            {/if}
        </p>
        
        <Button class="w-50 cursor-pointer" onclick={onstart}>
            Start Task
        </Button>
    </div>
</div>