<script>
    let { data } = $props();
    
    function formatDate(iso) 
    {
        return new Date(iso).toLocaleDateString('en-GB', { dateStyle: 'full' });
    }
</script>

<h1 class="text-6xl">Done!</h1>
<p>
    The session is done. Thanks for participating!
</p>

{#if data.nextSlotDate}
    <p>Your next session is on:</p>
    <p><strong>{formatDate(data.nextSlotDate)}</strong></p>
{/if}