<script>
    import { untrack } from "svelte";
    import Button from "$lib/components/ui/button/button.svelte";
    import Input from "$lib/components/ui/input/input.svelte";
    import Label from "$lib/components/ui/label/label.svelte";
    import { addDays, generateSlots, formatDate } from '$lib/utils/studySchedule.js';

    let { data, form } = $props();
    
    let errorDismissed = $state(false);
    
    let startDate = $state(untrack(() => data.config?.startDate ?? undefined));
    let endDate = $state(untrack(() => data.config?.endDate ?? undefined));
    let dayInterval = $state(untrack(() => data.config?.dayInterval ?? 2));
    let gracePeriod = $state(untrack(() => data.config?.gracePeriod ?? 1));
    
    const today = new Date().toISOString().slice(0, 10);
    
    let status = $derived.by(() => 
    {
        const c = data.config;
        if (!data.config) return 'not-configured';
        if (today < c.startDate) return 'configured';
        if (today <= c.endDate) return 'active';
        return 'ended';
    });
    
</script>

<div class="flex flex-col w-full gap-3">
    <!-- Top bar -->
    <div class="flex w-full border-b border-zinc-700 items-center p-4 justify-start gap-5">
        <h1 class="text-2xl">Schedule</h1>
        
        <span class="px-2 py-1.5 rounded text-sm {
            status === 'not-configured' ? 'bg-zinc-700 text-zinc-300' :
            status === 'configured'     ? 'bg-amber-900 text-amber-300' :
            status === 'active'         ? 'bg-green-900 text-green-300' :
                                        'bg-red-900 text-red-300'
        }">
            {status === 'not-configured' ? 'Not configured' :
            status === 'configured'     ? 'Configured' :
            status === 'active'         ? 'Active' : 'Ended'}
        </span>
    </div>
    
    <!-- Two column body -->
    <div class="grid grid-cols-2 gap-8 p-6">
        <!-- Left form -->
        <div class="flex flex-col gap-5">
            <h2 class="text-sm text-zinc-400 uppercase tracking-wider">Config</h2>
            
            <form method="POST" action="?/save" class="flex flex-col gap-4">
                <div class="grid grid-cols-2 gap-4">
                    <div class="flex flex-col gap-1.5">
                        <Label>Start date</Label>
                        <Input type="date" name="startDate" bind:value={startDate} />
                    </div>
                    
                    <div class="flex flex-col gap-1.5">
                        <Label>End date</Label>
                        <Input type="date" name="endDate" bind:value={endDate} />
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <div class="flex flex-col gap-1.5">
                        <Label>Day interval</Label>
                        <Input type="number" name="dayInterval" min="1" bind:value={dayInterval} />
                    </div>
                    
                    <div class="flex flex-col gap-1.5">
                        <Label>Grace period</Label>
                        <Input type="number" name="gracePeriod" min="0" bind:value={gracePeriod} />
                    </div>
                </div>
                
                <div class="flex flex-col items-center justify-center mt-2 gap-5">
                    {#if form?.error && !errorDismissed}
                        <div class="w-full mx-4 px-4 py-2.5 bg-red-900/30 border border-red-800 text-red-300 rounded-lg text-sm">
                            {form.error}
                        </div>
                    {/if}
                    <Button class="px-10" type="submit">Save</Button>
                </div>
            </form>
        </div>
        
        <!-- Right preview -->
        <div class="flex flex-col gap-3">
            <h2 class="text-sm text-zinc-400 uppercase tracking-wider">Preview</h2>
            
            {#if startDate && endDate && dayInterval && gracePeriod !== null}
                {#each generateSlots({ startDate, endDate, dayInterval, gracePeriod }) as slot}
                    {@const isToday = today >= slot.start && today <= slot.end}
                    <div class="grid grid-cols-[2rem_1fr_auto_1fr] items-center gap-3 py-2 px-3 rounded 
                    {isToday ? 'bg-green-900/20 border border-green-800/50' : ''}">
                        <span class="text-xs text-zinc-500 font-mono">{slot.slotIndex}</span>
                        <span class="text-sm {isToday ? 'text-green-300' : 'text-zinc-200'}">{formatDate(slot.start)}</span>
                        {#if slot.start !== slot.end}
                            <span class="text-zinc-600 text-xs">→</span>
                            <span class="text-sm text-zinc-400">{formatDate(slot.end)}</span>
                        {/if}
                    </div>
                {/each}
            {:else}
                <p class="text-sm text-muted-foreground">Fill in all values first.</p>
            {/if}
        </div>
    </div>
</div>