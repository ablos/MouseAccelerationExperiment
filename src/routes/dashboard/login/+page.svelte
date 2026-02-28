<script>
    import Button from "$lib/components/ui/button/button.svelte";
    import Input from "$lib/components/ui/input/input.svelte";
    
    let { form } = $props();
</script>

<div class="flex h-screen w-full justify-center items-center">
    <form method="POST" class="flex flex-col w-100 items-center gap-2">
        <h1 class="text-4xl font-bold pb-2">Dashboard Login</h1>
        
        <Input class="w-full" type="password" name="password" placeholder="Password" />
        
        <Button class="w-full cursor-pointer" type="submit">Log In</Button>
        
        {#if form?.error}
            <p class="text-red-500 text-sm">{form.error}</p>
        {/if}
    </form>
</div>
