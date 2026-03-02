<script>
    import { onMount } from 'svelte';

    let { children } = $props();

    onMount(() => {
        document.documentElement.classList.add('dark');
        return () => document.documentElement.classList.remove('dark');
    });
</script>

<div class="dark min-h-screen bg-zinc-900 text-zinc-100">
    {@render children()}
</div>