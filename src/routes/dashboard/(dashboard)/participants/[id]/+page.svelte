<script>
    import { ChevronLeft, X, ChevronDown, ChevronUp } from "lucide-svelte";
    import { goto } from "$app/navigation";
    import Button from "$lib/components/ui/button/button.svelte";
    import * as Dialog from "$lib/components/ui/dialog";
    import { Label } from "$lib/components/ui/label";
    import Input from "$lib/components/ui/input/input.svelte";
    import Textarea from "$lib/components/ui/textarea/textarea.svelte";
    import * as Tooltip from '$lib/components/ui/tooltip';
    import { generateSlots } from '$lib/utils/studySchedule.js';
    import { getParticipantStatus } from '$lib/utils/participants.js';
    import { getSessionMetrics } from "$lib/utils/metrics";
    import { UAParser } from 'ua-parser-js';

    let { data, form } = $props();
    let totalSlots = $derived(generateSlots(data.config).length || 0);
    let status = $derived(getParticipantStatus(data.participant, data.sessions.length, totalSlots));
    let messageDismissed = $state(false);
    
    let avgHoursBetweenSessions = $derived.by(() => 
    {
        const relevant = data.sessions.filter(s => s.slot > 1 && s.hoursSinceLastSession !== null);
        if (!relevant.length) return '-';
        const avg = relevant.reduce((sum, s) => sum + s.hoursSinceLastSession, 0) / relevant.length;
        return avg.toFixed(1);
    });
    
    let openSessions = $state(new Set());
    let showPercent = $state(true);
    let baselineMetrics = $derived.by(() => {
        const baseline = data.sessions.find(s => s.slot === 1);
        if (!baseline) return null;
        return getSessionMetrics(baseline, data.tasks, data.trials, data.mouseCoordinates);
    });

    function toggleSession(id)
    {
        const next = new Set(openSessions);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        openSessions = next;
    }

    function formatVal(value, decimals) {
        if (value === null) return '-';
        return value.toFixed(decimals);
    }

    function formatDelta(value, baseline, decimals) {
        if (value === null || baseline === null || baseline === 0) return '-';
        if (showPercent) {
            const pct = ((value - baseline) / baseline) * 100;
            return (pct >= 0 ? '+' : '') + pct.toFixed(1) + '%';
        }
        const diff = value - baseline;
        return (diff >= 0 ? '+' : '') + diff.toFixed(decimals);
    }

    function deltaClass(value, baseline) {
        if (value === null || baseline === null || baseline === 0) return 'text-zinc-400';
        const diff = value - baseline;
        if (Math.abs(diff / baseline) < 0.001) return 'text-zinc-400';
        return diff < 0 ? 'text-green-400' : 'text-red-400';
    }
</script>

{#snippet stat(label, value, tooltip, suffix = null)}
    <Tooltip.Root>
        <Tooltip.Trigger>
            <div class="flex flex-col items-center cursor-default">
                <span class="text-xs text-zinc-400">{label}</span>
                <span class="text-sm capitalize">
                    {value}{#if suffix}<span class="text-zinc-600"> {suffix}</span>{/if}
                </span>
            </div>
        </Tooltip.Trigger>
        <Tooltip.Content class="bg-zinc-800 text-zinc-200 border border-zinc-700" arrowClasses="bg-zinc-800">
            <p>{tooltip}</p>
        </Tooltip.Content>
    </Tooltip.Root>
{/snippet}

<div class="flex flex-col w-full gap-3">
    <!-- Top bar -->
    <div class="flex w-full border-b border-zinc-700 items-center p-4 justify-between">
        <div class="flex justify-start gap-4 items-center">
            <ChevronLeft class="cursor-pointer shrink-0" onclick={() => goto("/dashboard/participants")} />
        
            <h1 class="text-2xl">Participant</h1>
            
            <!-- Code -->
            <span class="font-mono bg-zinc-800 px-2 py-0.5 rounded">{data.participant.code}</span>
            
            <!-- Status -->
            <span class="px-2 py-0.5 text-center w-3/4 rounded {
                status === 'Invited' ? 'bg-zinc-700 text-zinc-300' :
                status === 'Needs Assignment' ? 'bg-amber-900 text-amber-300' :
                status === 'Active' ? 'bg-green-900 text-green-300' :
                'bg-violet-900 text-violet-300'
            }">{status}</span>
        </div>
        
        <div class="flex items-center gap-2">
            {#if data.participant.group && data.contact?.email}
                <form method="POST" action="?/resendAssignmentEmail">
                    <Button type="submit" variant="outline" class="cursor-pointer">Resend Assignment Email</Button>
                </form>
            {/if}

        <!-- Contact info dialog -->
        <Dialog.Root>
            <Dialog.Trigger>
                {#snippet child({ props })}
                    <Button {...props} class="cursor-pointer">Contact Info</Button>
                {/snippet}
            </Dialog.Trigger>
            
            <Dialog.Content>
                <Dialog.Header>
                    <Dialog.Title>Contact Info for {data.participant.code}</Dialog.Title>
                    <Dialog.Description>
                        {#if data.contact}
                            This data is only meant for contact regarding the study.
                        {:else}
                            There is no known data about this participant.
                        {/if}
                    </Dialog.Description>
                </Dialog.Header>
                
                <form id="participant-contact-form" method="POST" action="?/updateContact" class="flex flex-col w-full gap-2">
                    <input hidden name="participant-id" value={data.participant.id} />
                
                    <Label for="name">Name<span class="text-red-600">*</span></Label>
                    <Input name="name" id="name" type="text" value={data.contact?.name ?? ""} required />
                    
                    <Label for="email">Email<span class="text-red-600">*</span></Label>
                    <Input name="email" id="email" type="email" value={data.contact?.email ?? ""} required />
                    
                    <Label for="phone">Phone</Label>
                    <Input name="phone" id="phone" type="tel" value={data.contact?.phone ?? ""} />
                    
                    <Label for="notes">Notes</Label>
                    <Textarea name="notes" id="notes" value={data.contact?.notes ?? ""} />
                </form>
                
                <Dialog.Footer class="flex justify-center sm:justify-center">
                    <Dialog.Close>
                        {#snippet child({ props })}
                            <Button {...props} variant="outline" class="cursor-pointer flex-1">Cancel</Button>
                        {/snippet}
                    </Dialog.Close>
                    
                    <Button type="submit" form="participant-contact-form" class="cursor-pointer flex-1">Update Contact</Button>
                </Dialog.Footer>
            </Dialog.Content>
        </Dialog.Root>
        </div>
    </div>

    <!-- Participant invite success message -->
    {#if form?.success && !messageDismissed}
        <div class="mx-4 px-4 py-2.5 bg-green-900/30 border border-green-800 text-green-300 rounded-lg text-sm flex items-center justify-between gap-4">
            <span>Contact info updated successfully.</span>
            <button onclick={() => messageDismissed = true} class="text-green-600 hover:text-green-400 cursor-pointer shrink-0">
                <X size={14} />
            </button>
        </div>
    {/if}
    
    <!-- Assignment email resent message -->
    {#if form?.emailResent && !messageDismissed}
        <div class="mx-4 px-4 py-2.5 bg-green-900/30 border border-green-800 text-green-300 rounded-lg text-sm flex items-center justify-between gap-4">
            <span>Assignment email resent successfully.</span>
            <button onclick={() => messageDismissed = true} class="text-green-600 hover:text-green-400 cursor-pointer shrink-0">
                <X size={14} />
            </button>
        </div>
    {/if}

    <!-- Participant contact update error message -->
    {#if form?.error && !messageDismissed}
        <div class="mx-4 px-4 py-2.5 bg-red-900/30 border border-red-800 text-red-300 rounded-lg text-sm flex items-center justify-between gap-4">
            {form.error}
            <button onclick={() => messageDismissed = true} class="text-red-600 hover:text-red-400 cursor-pointer shrink-0">
                <X size={14} />
            </button>
        </div>
    {/if}
    
    <!-- Info strip -->
    <Tooltip.Provider>
        <div class="grid grid-cols-8 gap-3 px-10 pb-4 w-full border-b border-zinc-700">
            <!-- Row 1 -->
            {@render stat('Group', data.participant?.group ?? "Unassigned", 'Participant Group')}
            {@render stat('Age', data.participant?.age ?? "-", 'Participant Age')}
            {@render stat('Sex', data.participant?.sex ?? "-", 'Participant Sex')}
            {@render stat('Handedness', data.participant?.handedness ?? "-", "Left or Right handed")}
            {@render stat('Hours per Week', data.participant?.hoursPerWeek ?? '-', 'Self-reported average hours per week')}
            {@render stat('Gaming Experience', data.participant?.gamingExperience ?? '-', 'Self-reported gaming experience')}
            {@render stat('Avg. hours between sessions', avgHoursBetweenSessions, 'Average computer use between sessions')}
            {@render stat('Sessions done', data.sessions.length, 'Sessions done by participant', ' / ' + totalSlots)}
            
        </div>
    </Tooltip.Provider>
    
    <!-- Session list -->
    <div class="flex flex-col px-10 mt-5">
        <div class="grid grid-cols-[0.5fr_1fr_1fr_1fr_1fr_1fr_1fr_0.5fr] w-full py-2 justify-items-center text-xs text-zinc-500">
            <span>Session</span>
            <span>Date</span>
            <span>Duration</span>
            <span>Avg. Time</span>
            <span>Accuracy</span>
            <span>PLR</span>
            <span>Submovements</span>
            <button onclick={() => showPercent = !showPercent} class="px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 hover:text-zinc-200 cursor-pointer">
                {showPercent ? '%' : 'Δ'}
            </button>
        </div>
        <div class="mx-4 mb-1 h-0.5 bg-zinc-700 rounded-full"></div>
    
        {#if !data.sessions.length}
            <div class="flex flex-col items-center justify-center py-16 text-zinc-500">
                <span class="text-sm">No sessions yet.</span>
            </div>
        {/if}

        {#each data.sessions.toSorted((a, b) => a.slot - b.slot) as session}
            {@const isOpen = openSessions.has(session.id)}
            {@const isBaseline = session.slot === 1}
            {@const metrics = getSessionMetrics(session, data.tasks, data.trials, data.mouseCoordinates)}
            
            <button
                onclick={() => toggleSession(session.id)}
                class="grid grid-cols-[0.5fr_1fr_1fr_1fr_1fr_1fr_1fr_0.5fr] w-full py-3 items-center justify-items-center text-zinc-200 border-b border-zinc-700 hover:bg-zinc-800/50 cursor-pointer"
            >
                <!-- Slot -->
                <div class="flex items-center gap-2">
                    <span class="font-mono bg-zinc-800 px-2 py-0.5 rounded text-sm">#{session.slot}</span>
                    {#if isBaseline}<span class="text-xs text-zinc-500">Baseline</span>{/if}
                </div>
                
                <!-- Date -->
                <span class="text-sm text-zinc-400">{session.startTime.toLocaleDateString()}</span>
                
                <!-- Duration -->
                {#if session.endTime}
                    {@const totalSec = Math.round((session.endTime - session.startTime) / 1000)}
                    <span class="text-sm text-zinc-400">{Math.floor(totalSec / 60)}m {totalSec % 60}s</span>
                {:else}
                    <span class="text-sm text-zinc-500 italic">In progress</span>
                {/if}
                
                <!-- Metrics -->
                {#each [
                    { value: metrics.combined.time, bval: baselineMetrics?.combined.time, unit: 'ms', decimals: 0 },
                    { value: metrics.combined.accuracy, bval: baselineMetrics?.combined.accuracy, unit: 'px', decimals: 1 },
                    { value: metrics.combined.plr, bval: baselineMetrics?.combined.plr, unit: '', decimals: 2 },
                    { value: metrics.combined.submovements, bval: baselineMetrics?.combined.submovements, unit: '', decimals: 1 }
                ] as m}
                    <div class="flex flex-col items-center">
                        <span class="text-sm tabular-nums">{m.value !== null ? m.value.toFixed(m.decimals) + (m.unit ? ' ' + m.unit : '') : '-'}</span>
                        {#if !isBaseline && baselineMetrics}
                            <span class="text-xs tabular-nums {deltaClass(m.value, m.bval)}">{formatDelta(m.value, m.bval, m.decimals)}</span>
                        {/if}
                    </div>
                {/each}
                
                <!-- Chevron -->
                {#if isOpen}<ChevronUp size={16} class="text-zinc-400" />{:else}<ChevronDown size={16} class="text-zinc-400" />{/if}
            </button>
            
            {#if isOpen}
                {@const ua = new UAParser(session.userAgent).getResult()}
                <div class="flex gap-6 p-4 border-b border-zinc-700 bg-zinc-900/30">
                    <!-- Left sidebar -->
                    <div class="flex flex-col gap-1.5 w-64 shrink-0 text-sm border-r border-zinc-700 pr-6">

                        {#snippet detail(label, value)}
                            <div class="flex justify-between gap-4">
                                <span class="text-zinc-500">{label}</span>
                                <span class="text-zinc-300 text-right">{value}</span>
                            </div>
                        {/snippet}

                        {@render detail('Start', session.startTime.toLocaleTimeString())}
                        {@render detail('End', session.endTime?.toLocaleTimeString() ?? '-')}
                        {@render detail('Since last', session.slot === 1 ? 'First session' : (session.hoursSinceLastSession?.toFixed(1) ?? '-') + 'h')}
                        <div class="my-1 h-px bg-zinc-800"></div>
                        {@render detail('Screen', `${session.screenResX} × ${session.screenResY}`)}
                        {@render detail('px/mm', session.screenPxPerMm.toFixed(2))}
                        {@render detail('DPR', session.devicePixelRatio)}
                        <div class="my-1 h-px bg-zinc-800"></div>
                        {@render detail('Browser', [ua.browser.name, ua.browser.major].filter(Boolean).join(' '))}
                        {@render detail('OS', [ua.os.name, ua.os.version].filter(Boolean).join(' '))}
                    </div>

                    <!-- Right: metrics table -->
                    <div class="flex-1 flex flex-col text-sm overflow-x-auto">
                        <div class="flex items-center gap-3 mb-2">
                            <span class="text-xs text-zinc-500">Avg. metrics per trial</span>
                            {#if !isBaseline && baselineMetrics}
                                <button onclick={() => showPercent = !showPercent} class="text-xs px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 hover:text-zinc-200 cursor-pointer">
                                    {showPercent ? '%' : 'Δ'}
                                </button>
                            {/if}
                        </div>
                        <table class="w-full">
                            <thead>
                                <tr class="text-xs text-zinc-500">
                                    <th class="text-left font-normal pb-1 pr-6">Type</th>
                                    <th colspan="2" class="text-center font-normal pb-1 px-3">Time (ms)</th>
                                    <th colspan="2" class="text-center font-normal pb-1 px-3">Accuracy (px)</th>
                                    <th colspan="2" class="text-center font-normal pb-1 px-3">PLR</th>
                                    <th colspan="2" class="text-center font-normal pb-1 pl-3">Sub movements</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each [
                                    { label: 'Clicking', key: 'clicking' },
                                    { label: 'Sliding', key: 'sliding' },
                                    { label: 'Dragging', key: 'dragging' },
                                    { label: 'Combined', key: 'combined' }
                                ] as row}
                                    {@const bm = baselineMetrics?.[row.key]}
                                    <tr class="text-zinc-300 {row.key === 'combined' ? 'border-t border-zinc-700' : ''}">
                                        <td class="text-left text-zinc-500 py-1 pr-6">{row.label}</td>
                                        {#each [
                                            { val: metrics[row.key].time, bval: bm?.time, dec: 0 },
                                            { val: metrics[row.key].accuracy, bval: bm?.accuracy, dec: 1 },
                                            { val: metrics[row.key].plr, bval: bm?.plr, dec: 2 },
                                            { val: metrics[row.key].submovements, bval: bm?.submovements, dec: 1 }
                                        ] as c}
                                            <td class="text-right tabular-nums py-1 pl-3 pr-1">{formatVal(c.val, c.dec)}</td>
                                            <td class="text-left tabular-nums py-1 pr-3 w-16">
                                                {#if !isBaseline && bm}
                                                    <span class="text-xs {deltaClass(c.val, c.bval)}">({formatDelta(c.val, c.bval, c.dec)})</span>
                                                {/if}
                                            </td>
                                        {/each}
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                </div>
            {/if}
        {/each}
    </div>
</div>