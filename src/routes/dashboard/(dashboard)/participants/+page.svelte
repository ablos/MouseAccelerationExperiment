<script>
    import Button from "$lib/components/ui/button/button.svelte";
    import { Label } from "$lib/components/ui/label";
    import Input from "$lib/components/ui/input/input.svelte";
    import Textarea from "$lib/components/ui/textarea/textarea.svelte";
    import { Mars, Venus, Asterisk, X } from 'lucide-svelte';
    import * as Dialog from '$lib/components/ui/dialog';
    import * as Tooltip from '$lib/components/ui/tooltip';
    
    let { data, form } = $props();
    
    let messageDismissed = $state(false);
    
    
    
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

{#snippet stat(label, value, tooltip)}
    <Tooltip.Root>
        <Tooltip.Trigger>
            <div class="flex flex-col items-center cursor-default">
                <span class="text-xs text-zinc-400">{label}</span>
                <span class="text-sm">{value}</span>
            </div>
        </Tooltip.Trigger>
        <Tooltip.Content class="bg-zinc-800 text-zinc-200 border border-zinc-700" arrowClasses="bg-zinc-800">
            <p>{tooltip}</p>
        </Tooltip.Content>
    </Tooltip.Root>
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
        <Button variant="outline" href="/dashboard/participants/{participant.id}" class="w-1/2 cursor-pointer">
            View
        </Button>
    </div>
{/snippet}

<div class="flex flex-col w-full gap-3">
    <!-- Top bar -->
    <div class="flex w-full border-b border-zinc-700 items-center py-4 px-4 justify-between">
        <h1 class="text-2xl">Participants</h1>
        
        <!-- Stats -->
        <Tooltip.Provider>
            {@render stat('Enrolled', `${withSession} / ${totalParticipants}`, '>1 session / Total invited')}
            {@render stat('Groups', `${controlCount}c / ${experimentalCount}e / ${unassignedCount}u`, 'Control / Experimental / Unassigned')}
            {@render stat('Avg. Age', `${avgAge}`, 'Average age of participants')}
            {@render stat('Handedness', `${rightCount}r / ${leftCount}l`, 'Right-handed / Left-handed')}
            {@render stat('Gender', `${maleCount}m / ${femaleCount}f / ${otherCount}o`, 'Male / Female / Other')}
        </Tooltip.Provider>
        
        <!-- New Participant Dialog -->
        <Dialog.Root>
            <Dialog.Trigger>
                {#snippet child({ props })}
                    <Button {...props} class="cursor-pointer">+ New Participant</Button>
                {/snippet}
            </Dialog.Trigger>
            
            <Dialog.Content>
                <Dialog.Header>
                    <Dialog.Title>Add new participant</Dialog.Title>
                    <Dialog.Description>
                        This will send an invite to the participant. This data is stored in a separate database that will be deleted after the study and is for contact purposes only.
                        <br><br>
                        Note: The name you enter here will be used in the invitation email.
                    </Dialog.Description>
                </Dialog.Header>
                
                <form id="new-participant-form" method="POST" action="?/createParticipant" class="flex flex-col w-full gap-2">
                    <Label for="name">Name<span class="text-red-600">*</span></Label>
                    <Input name="name" id="name" type="text" required />
                    
                    <Label for="email">Email<span class="text-red-600">*</span></Label>
                    <Input name="email" id="email" type="email" required />
                    
                    <Label for="phone">Phone</Label>
                    <Input name="phone" id="phone" type="tel" />
                    
                    <Label for="notes">Notes</Label>
                    <Textarea name="notes" id="notes" />
                </form>
                
                <Dialog.Footer class="flex justify-center sm:justify-center">
                    <Dialog.Close>
                        {#snippet child({ props })}
                            <Button {...props} variant="outline" class="cursor-pointer flex-1">Cancel</Button>
                        {/snippet}
                    </Dialog.Close>
                    
                    <Button type="submit" form="new-participant-form" class="cursor-pointer flex-1">Send Invitation</Button>
                </Dialog.Footer>
            </Dialog.Content>
        </Dialog.Root>
    </div>
    
    <!-- Participant invite success message -->
    {#if form?.code && !form?.error && !messageDismissed}
        <div class="mx-4 px-4 py-2.5 bg-green-900/30 border border-green-800 text-green-300 rounded-lg text-sm flex items-center justify-between gap-4">
            <span>Invitation sent successfully. Participant code: <span class="font-mono text-zinc-200 bg-zinc-800 px-1.5 py-0.5 rounded">{form.code}</span></span>
            <button onclick={() => messageDismissed = true} class="text-green-600 hover:text-green-400 cursor-pointer shrink-0">
                <X size={14} />
            </button>
        </div>
    {/if}
    
    <!-- Participant invite error message -->
    {#if form?.error && !messageDismissed}
        <div class="mx-4 px-4 py-2.5 bg-red-900/30 border border-red-800 text-red-300 rounded-lg text-sm">
            {form.error}
            {#if form.participantId}
                <a href="/dashboard/participants/{form.participantId}" class="text-zinc-200 underline ml-1">
                    View participant {form.code}
                </a>
            {/if}
        </div>
    {/if}
    
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