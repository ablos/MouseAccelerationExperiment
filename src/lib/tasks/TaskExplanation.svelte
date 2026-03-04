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
        
        <p class="text-center">
            {#if taskType === TaskType.CLICKING}
                In this task you have to click the target as fast and as accurately as possible. Clicks outside the target still count and are allowed.
            {:else if taskType === TaskType.SLIDER}
                In this task you have to drag the handle towards the target as fast and as accurately as possible. Dragging outside the target is allowed. Note that your performance is measured only while dragging. The time needed to click the handle is indifferent.
            {:else}
               In this task you have to drag and drop the file icon into the folder as fast and accurately as possible. The file is a blue icon and the folder a grey one.  Note that your performance is measured only while dragging. The time needed to click the file is indifferent.
            {/if}
        </p>
        
        <Button class="w-50 cursor-pointer" onclick={onstart}>
            Start Task
        </Button>
    </div>
</div>