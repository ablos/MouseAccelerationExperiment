<script>
    import Button from "$lib/components/ui/button/button.svelte";
    
    let { children } = $props();
</script>

<div class="flex h-screen w-full">
    <div class="flex flex-col w-65 border-r border-zinc-700 p-2">
    
        <!-- Logout button -->
        <form method="POST" action="/dashboard?/logout" class="mt-auto">
            <Button type="submit" class="w-full cursor-pointer">
                Log Out
            </Button>
        </form>
    </div>
    
    <div class="flex flex-1 overflow-y-auto">
        {@render children()}
    </div>
</div>