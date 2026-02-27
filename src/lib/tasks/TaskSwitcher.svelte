<script>
    import { getContext } from 'svelte';
    import { TaskType } from '$lib/enums';
    import ClickTask from './ClickTask.svelte';
    import SliderTask from './SliderTask.svelte';
    import DraggingTask from './DraggingTask.svelte';
    import RequestFullscreen from '$lib/RequestFullscreen.svelte';

    let { taskOrder, currentTaskIndex } = $props();
    const { isFullscreen } = getContext('fullscreen');
</script>

{#if isFullscreen}
    {#if taskOrder[currentTaskIndex] === TaskType.CLICKING}
        <ClickTask />
    {:else if taskOrder[currentTaskIndex] === TaskType.SLIDER}
        <SliderTask />
    {:else if taskOrder[currentTaskIndex] === TaskType.DRAGGING}
        <DraggingTask />
    {/if}
{:else}
    <RequestFullscreen />
{/if}