<script>
    import { setContext } from 'svelte';
    let { children } = $props();
    let el = $state(null);
    let isFullscreen = $state(false);

    $effect(() => {
        function onChange() {
            isFullscreen = !!document.fullscreenElement;
        }
        document.addEventListener('fullscreenchange', onChange);
        return () => document.removeEventListener('fullscreenchange', onChange);
    });

    function enter() { el.requestFullscreen(); }
    function exit() { document.exitFullscreen(); }
    function toggle() { isFullscreen ? exit() : enter(); }

    setContext('fullscreen', {
        get isFullscreen() { return isFullscreen },
        enter,
        exit,
        toggle
    });
</script>

<!-- svelte-ignore slot_element_deprecated -->
<div bind:this={el} class="container" >
    {@render children()}
</div>

<style>
    .container{
        width: 100%;
        height: 100%;
        background-color: white;

    }
</style>