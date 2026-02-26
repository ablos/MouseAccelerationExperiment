<script>
    import { onMount } from 'svelte';
    import ClickTask from "$lib/ClickTask.svelte";
    import Calibration from "$lib/Calibration.svelte";

    let pxPerMm = $state(null);

    onMount(() => {
        const stored = localStorage.getItem('pxPerMm');
        if (stored) pxPerMm = Number(stored);
    });
</script>

{#if pxPerMm === null}
    <Calibration oncalibrated={(value) => pxPerMm = value} />
{:else}
    <ClickTask {pxPerMm} />
{/if}
