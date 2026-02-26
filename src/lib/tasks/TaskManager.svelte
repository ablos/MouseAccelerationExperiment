<script>
	import { TaskType } from "$lib/enums";
    import ClickTask from "./ClickTask.svelte";
	import DraggingTask from "./DraggingTask.svelte";
	import SliderTask from "./SliderTask.svelte";
    
    let { pxPerMm } = $props();

    const taskOrder = [TaskType.CLICKING, TaskType.SLIDER, TaskType.DRAGGING]
    let currentTaskIndex = $state(0)
    
    function onComplete(taskType) {
        currentTaskIndex++;
    }
</script>

{#if taskOrder[currentTaskIndex] === TaskType.CLICKING}
    <ClickTask {pxPerMm} {onComplete} />
{:else if taskOrder[currentTaskIndex] === TaskType.SLIDER }
    <SliderTask {pxPerMm} {onComplete}/>
{:else if taskOrder[currentTaskIndex] === TaskType.DRAGGING }
    <DraggingTask {pxPerMm} {onComplete} />
{:else}
    <div>Task not found</div>
{/if}

