<script>
    import Button from "$lib/components/ui/button/button.svelte";
    import { Mars, Venus, Asterisk } from 'lucide-svelte';
    
    let { data } = $props();
    
    let totalParticipants = $derived(data.participants.length);
    let withSession = $derived(new Set(data.sessions.map(s => s.participantId)).size);
    
    let controlCount = $derived(data.participants.filter(p => p.group === 'control').length);
    let experimentalCount = $derived(data.participants.filter(p => p.group === 'experimental').length);
    let unassignedCount = $derived(data.participants.filter(p => !p.group).length);
    
    let avgAge = $derived.by(() => 
    {
        const withAge = data.participants.filter(p => p.age);
        if (!withAge.length) return '-';
        return Math.round(withAge.reduce((sum, p) => sum + p.age, 0) / withAge.length);
    });
    
    let rightCount = $derived(data.participants.filter(p => p.handedness === 'right').length);
    let leftCount = $derived(data.participants.filter(p => p.handedness === 'left').length);
    
    let maleCount = $derived(data.participants.filter(p => p.gender === 'male').length);
    let femaleCount = $derived(data.participants.filter(p => p.gender === 'female').length);
    let otherCount = $derived(data.participants.filter(p => p.gender && p.gender !== 'male' && p.gender !== 'female').length);
    
    function getStatus(participant, sessionCount) 
    {
        if (sessionCount === 0) return 'Invited';
        if (sessionCount >= 7) return 'Complete';
        if (!participant.group) return 'Needs Assignment';
        return 'Active';
    }
</script>

{#snippet stat(label, value)}
    <div class="flex flex-col items-center">
        <span class="text-xs text-zinc-400">{label}</span>
        <span class="text-sm">{value}</span>
    </div>
{/snippet}

{#snippet row(participant, sessionCount)}
    {@const status = getStatus(participant, sessionCount)}
    
    <div class="grid grid-cols-[1fr_1.5fr_1.5fr_0.75fr_0.75fr_0.75fr_0.75fr_1fr] mx-4 py-3 items-center justify-items-center text-zinc-200 border-b border-zinc-700 last:border-0">
        <!-- Code -->
        <span class="font-mono bg-zinc-800 px-2 py-0.5 rounded">{participant.code}</span>
        
        <!-- Status -->
        <span class="px-2 py-0.5 text-center w-3/4 rounded {
            status === 'Invited' ? 'bg-zinc-700 text-zinc-300' :
            status === 'Needs Assignment' ? 'bg-amber-900 text-amber-300' :
            status === 'Active' ? 'bg-green-900 text-green-300' :
            'bg-violet-900 text-violet-300'
        }">{status}</span>
        
        <!-- Group -->
        <span class="px-2 py-0.5 rounded capitalize {
            participant.group === 'control' ? ' text-cyan-300' :
            participant.group === 'experimental' ? ' text-red-300' :
            'text-zinc-200'
        }">{participant.group ?? 'Unassigned'}</span>
        
        <!-- Session count -->
        <span>{sessionCount}<span class="text-zinc-600">&nbsp;/ 7</span></span>
        
        <!-- Age -->
        <span>{participant.age ?? '-'}</span>
        
        <!-- Handedness -->
        <span class="{participant.handedness === 'right' ? 'text-teal-300' : participant.handedness === 'left' ? 'text-yellow-400' : ''}">
            {participant.handedness === 'right' ? 'R' : participant.handedness === 'left' ? 'L' : '-'}
        </span>
        
        <!-- Gender -->
        {#if participant.gender === 'male'}
            <Mars size={16} class='text-sky-300' />
        {:else if participant.gender === 'female'}
            <Venus size={16} class='text-rose-300' />
        {:else if participant.gender}
            <Asterisk size={16} class='text-purple-300' />
        {:else}
            <span>-</span>
        {/if}
        
        <!-- View button -->
        <Button variant="outline" href="/dashboard/participant/{participant.id}" class="w-1/2 cursor-pointer">
            View
        </Button>
    </div>
{/snippet}

<div class="flex flex-col w-full gap-3">
    <!-- Top bar -->
    <div class="flex w-full border-b border-zinc-700 items-center py-4 px-4 justify-between">
        <h1 class="text-2xl">Participants</h1>
        
        {@render stat('Enrolled', `${withSession} / ${totalParticipants}`)}
        {@render stat('Groups', `${controlCount}c / ${experimentalCount}e / ${unassignedCount}u`)}
        {@render stat('Avg. Age', `${avgAge}`)}
        {@render stat('Handedness', `${rightCount}r / ${leftCount}l`)}
        {@render stat('Gender', `${maleCount}m / ${femaleCount}f / ${otherCount}o`)}
    
        <Button class="cursor-pointer">
            + New Participant
        </Button>
    </div>
    
    <!-- Participant list -->
    <div class="flex flex-col">
        <div class="grid grid-cols-[1fr_1.5fr_1.5fr_0.75fr_0.75fr_0.75fr_0.75fr_1fr] mx-4 py-2 items-center justify-items-center text-zinc-400">
            <span>Code</span>
            <span>Status</span>
            <span>Group</span>
            <span>Session #</span>
            <span>Age</span>
            <span>Handedness</span>
            <span>Gender</span>
        </div>
        
        <div class="mx-4 mb-3 h-0.75 bg-zinc-700 rounded-full"></div>
    
        {#each data.participants as participant}
            {@render row(participant, data.sessions.filter(s => s.participantId === participant.id).length)}
        {/each}
    </div>
</div>