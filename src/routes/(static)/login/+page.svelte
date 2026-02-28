<script>
    import Input from "$lib/components/ui/input/input.svelte";
    import Button from "$lib/components/ui/button/button.svelte";
</script>

<form method="POST" class="flex flex-col w-100 items-center gap-2">
    <h1 class="text-4xl font-bold pb-2">Hello there!</h1>

    <Input class="w-full" type="text" name="code" placeholder="Participant Code" />
    <Button class="w-full" type="submit">Log In</Button>
</form>