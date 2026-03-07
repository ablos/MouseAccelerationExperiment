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

<div class="flex flex-col justify-center items-center max-w-200 gap-3">
    <h1 class="text-3xl">Welcome to the experiment!</h1>
    <p>
        Some explanation about the experiment.  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vitae rhoncus tortor, ut lobortis dui. Donec eu molestie odio. Maecenas faucibus condimentum sapien, at semper enim tincidunt at. Aenean risus mi, vestibulum et nisl in, molestie sodales elit. Cras placerat dictum augue, varius rutrum magna facilisis at. Vivamus venenatis massa risus, sit amet elementum turpis gravida et. Vestibulum luctus tempor eros, at rutrum magna pellentesque ut. Etiam eget consequat sem. Ut viverra sit amet neque vel tincidunt.     Etiam placerat tincidunt ante, at scelerisque ex maximus et. Nullam quis laoreet massa, quis suscipit metus. Donec neque nibh, vestibulum ut est nec, venenatis imperdiet dolor. Praesent quis hendrerit dui. In sed mattis augue. Donec pulvinar viverra lectus. Vestibulum eget massa luctus, efficitur purus sit amet, maximus ex. Pellentesque ut sollicitudin libero. Nam quis diam luctus, pulvinar nunc nec, iaculis eros. Ut ut mi viverra, cursus nibh a, sodales neque. Vivamus egestas arcu sit amet libero varius rutrum. Mauris mollis leo ut urna malesuada, vitae bibendum turpis pharetra. Aliquam varius tellus quis posuere dapibus.    Sed vel nunc eget ipsum maximus auctor. Morbi nec consequat quam. Nulla eleifend gravida nibh, nec volutpat est cursus nec. Proin laoreet id est vel finibus. Fusce tempus efficitur auctor. Aliquam euismod id magna efficitur elementum. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Cras sed erat id nunc blandit gravida id ut libero. Vivamus eleifend metus vel orci ultrices, vitae fermentum odio tempor. Nunc rhoncus nec mi eget interdum. Integer vel orci lorem. Etiam fermentum viverra eros ut dapibus. Morbi urna quam, tempor vitae commodo id, tincidunt at est. Aenean eget felis non libero molestie vulputate. Aliquam auctor laoreet molestie. Vivamus interdum ex non tristique congue.
    </p>
    
    <Button href="/session" class="cursor-pointer" data-sveltekit-reload>Continue to experiment</Button>
</div>
