<script>
    let { children } = $props();
</script>

<div class="flex flex-col h-screen w-full justify-center items-center gap-3">
    {@render children()}
</div>