<script>
    import Button from "$lib/components/ui/button/button.svelte";
    import * as Dialog from "$lib/components/ui/dialog";
    import { page } from '$app/stores';
    import { replaceState } from "$app/navigation";
    
    let dialogOpen = $state(!!$page.data.reason);
    
    function closeDialog() 
    {
        dialogOpen = false;
        replaceState('/', {});
    }
    
    function formatDate(isoString) 
    {
        if (!isoString) return "Unknown";
    
        const [year, month, day] = isoString.split('-').map(Number);
        
        return new Intl.DateTimeFormat('en-US', 
        {
            weekday: 'long',
            month: 'long',
            day: 'numeric'
        }).format(new Date(year, month - 1, day));
    }
</script>

<Dialog.Root bind:open={dialogOpen}>
    <Dialog.Content>
        <Dialog.Header>
            <Dialog.Title>
                {#if $page.data.reason === "no-slot"}
                    No session today
                {:else if $page.data.reason === "slot-done"}
                    Session already completed
                {:else if $page.data.reason === "study-ended"}
                    Study complete
                {:else if $page.data.reason === "study-not-started"}
                    Study not started
                {:else if $page.data.reason === "no-group"}
                    Group not yet assigned
                {:else}
                    Unknown
                {/if}
            </Dialog.Title>
        </Dialog.Header>

        {#if $page.data.reason === "no-slot"}
            <p>Your next session is scheduled for:</p>
            <p class="text-2xl font-semibold text-center">{formatDate($page.data.next)}</p>
        {:else if $page.data.reason === "slot-done"}
            <p>You've already completed today's session. Your next session is on:</p>
            <p class="text-2xl font-semibold text-center">{formatDate($page.data.next)}</p>
        {:else if $page.data.reason === "study-ended"}
            <p>You've completed all your sessions. Thanks for participating!</p>
        {:else if $page.data.reason === "study-not-started"}
            <p>The study has not started yet. Please come back later.</p>
        {:else if $page.data.reason === "no-group"}
            <p>You haven't been assigned to a group yet. Please wait and try again later.</p>
        {:else}
            Unknown
        {/if}
        
        <Dialog.Footer>
            <Button class="mx-auto" onclick={closeDialog}>
                Got it
            </Button>
        </Dialog.Footer>
    </Dialog.Content>
</Dialog.Root>

<form method="POST" action="?/logout">
    <Button type="submit" class="absolute top-2 right-2 cursor-pointer">
        Log out
    </Button>
</form>

<div class="flex flex-col justify-center items-center max-w-xl gap-4">
    {#if $page.data.isFirstSession}
        <h1 class="text-3xl">Welcome!</h1>
        <p>
            This is the web application for the <strong>Disabling Mouse Acceleration</strong> study.
            Over the next two weeks, you'll complete a short daily session of mouse-based tasks,
            helping us understand how mouse acceleration settings affect pointing speed and accuracy over time.
        </p>
        <p>
            Today is your <strong>baseline session</strong>. Your mouse settings don't need to change yet —
            just complete the tasks with your current setup. After this session, you will be assigned to one of two groups:
        </p>
        <ul class="list-disc list-inside space-y-1 self-start">
            <li>The <strong>control group</strong>, where you keep mouse acceleration enabled as usual.</li>
            <li>The <strong>experimental group</strong>, where you will be asked to disable mouse acceleration for the remainder of the study. Clear instructions will be provided on how to do this.</li>
        </ul>
        <p>
            Whichever group you're assigned to, it's important that you <strong>don't change your pointer sensitivity or DPI settings</strong>
            at any point during the study, and that you use the <strong>same mouse and screen</strong> for every session.
        </p>
        <p>Each session takes around 2 to 5 minutes. Press Start when you're ready.</p>
    {:else}
        <h1 class="text-3xl">Welcome back!</h1>
        <p>
            As a reminder, this study is investigating how mouse acceleration settings affect pointing speed and accuracy over time.
        </p>
        <p>
            Depending on your group, you should currently have mouse acceleration either <strong>enabled or disabled</strong>.
            Please make sure your settings haven't changed since your last session, and that you're using the <strong>same mouse and screen</strong> as before.
        </p>
        <p>Today's session will take around 2 to 5 minutes. Press Start when you're ready.</p>
    {/if}

    <Button href="/session" class="cursor-pointer mt-2" data-sveltekit-reload>Start</Button>
</div>
