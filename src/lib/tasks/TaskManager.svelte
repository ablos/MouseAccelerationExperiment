<script>
	import { TaskType } from "$lib/enums";
    import ClickTask from "./ClickTask.svelte";
	import DraggingTask from "./DraggingTask.svelte";
	import SliderTask from "./SliderTask.svelte";
    let { pxPerMm } = $props();

    let currentTaskType = $state(TaskType.CLICKING);
    
    function changeTaskType(taskType) {
        currentTaskType = taskType;
    }
</script>

{#if currentTaskType === TaskType.CLICKING}
    <ClickTask {pxPerMm} {changeTaskType} />
{:else if currentTaskType === TaskType.SLIDER }
    <SliderTask {pxPerMm} {changeTaskType}/>
{:else if currentTaskType === TaskType.DRAGGING }
    <DraggingTask />
{:else}
    <div>Task not found</div>
{/if}

