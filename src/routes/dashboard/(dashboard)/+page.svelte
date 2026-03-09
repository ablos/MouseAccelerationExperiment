<script>
    import { Mail, Phone, User } from 'lucide-svelte';
    import Button from '$lib/components/ui/button/button.svelte';

    let { data, form } = $props();
</script>

<div class="flex flex-col w-full gap-6 p-6">
    <div class="flex items-center justify-between border-b border-zinc-700 pb-4">
        <h1 class="text-2xl">Overview</h1>
    </div>

    {#if !data.slot}
        <p class="text-zinc-400 text-sm">Today is not a session day.</p>
    {:else}
        <div class="flex flex-col gap-4">
            <div class="flex items-center justify-between">
                <div>
                    <h2 class="text-lg">Session day — slot {data.slot}</h2>
                    <p class="text-zinc-400 text-sm mt-0.5">
                        {#if data.pending.length === 0}
                            All participants have completed their session today.
                        {:else}
                            {data.pending.length} participant{data.pending.length === 1 ? '' : 's'} still pending
                        {/if}
                    </p>
                </div>

                {#if data.pending.length > 0}
                    <form method="POST" action="?/sendReminders">
                        <Button type="submit" variant="outline" class="cursor-pointer flex items-center gap-2">
                            <Mail size={14} />
                            Send reminder to all
                        </Button>
                    </form>
                {/if}
            </div>

            {#if form?.remindersSent != null}
                <p class="text-green-400 text-sm">Sent reminders to {form.remindersSent} participant{form.remindersSent === 1 ? '' : 's'}.</p>
            {/if}

            {#if data.pending.length > 0}
                <div class="flex flex-col border border-zinc-700 rounded-lg overflow-hidden">
                    {#each data.pending as p}
                        <div class="flex items-center justify-between px-4 py-3 border-b border-zinc-700 last:border-0">
                            <div class="flex items-center gap-3">
                                <User size={14} class="text-zinc-500 shrink-0" />
                                <div>
                                    <span class="text-sm">{p.name ?? 'Unknown'}</span>
                                    <span class="font-mono text-xs text-zinc-500 ml-2">{p.code}</span>
                                </div>
                            </div>

                            <div class="flex items-center gap-6 text-sm text-zinc-400">
                                {#if p.email}
                                    <a href="mailto:{p.email}" class="flex items-center gap-1.5 hover:text-zinc-200">
                                        <Mail size={13} />
                                        {p.email}
                                    </a>
                                {/if}
                                {#if p.phone}
                                    <a href="tel:{p.phone}" class="flex items-center gap-1.5 hover:text-zinc-200">
                                        <Phone size={13} />
                                        {p.phone}
                                    </a>
                                {/if}
                                <Button variant="outline" size="sm" href="/dashboard/participants/{p.id}" class="cursor-pointer">
                                    View
                                </Button>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    {/if}
</div>
