<script>
    import Input from "$lib/components/ui/input/input.svelte";
    import Button from "$lib/components/ui/button/button.svelte";
    import Label from "$lib/components/ui/label/label.svelte";
</script>

<h1 class="text-3xl">A small survey</h1>
<p>We need to know some information, so please fill this in:</p>

<form class="flex flex-col gap-2 w-100" method="POST">
    <Label for="age">Age</Label>
    <Input type="number" id="age" name="age" min="16" max="99" required />
    
    <Button type="submit cursor-pointer" class="w-full mt-4">Continue</Button>
</form>