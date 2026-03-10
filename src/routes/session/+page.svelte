<script>
    import { onMount } from 'svelte';
    import ClickTask from "$lib/tasks/ClickTask.svelte";
	import SessionManager from '$lib/tasks/SessionManager.svelte';
	import { goto } from '$app/navigation';

    let { data } = $props();
    let pxPerMm = $state(null);

    onMount(() => {
        const stored = localStorage.getItem('pxPerMm');
        
        if (!stored) 
        {
            goto('/calibration');
            return;
        }
        
        pxPerMm = Number(stored);
    });
</script>

{#if pxPerMm}
    <SessionManager {pxPerMm} isFirstSession={data.isFirstSession} slot={data.slot} group={data.group} />
{/if}
