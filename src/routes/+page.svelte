<script>
    import { onMount } from 'svelte';
    import ClickTask from "$lib/tasks/ClickTask.svelte";
    import Calibration from "$lib/Calibration.svelte";
	import SessionManager from '$lib/tasks/SessionManager.svelte';

    let pxPerMm = $state(null);

    onMount(() => {
        const stored = localStorage.getItem('pxPerMm');
        if (stored) pxPerMm = Number(stored);
    });
</script>

{#if pxPerMm === null}
    <Calibration oncalibrated={(value) => pxPerMm = value} />
{:else}
    <SessionManager {pxPerMm} />
{/if}
