<script>
    import Input from "$lib/components/ui/input/input.svelte";
    import Button from "$lib/components/ui/button/button.svelte";
    import Label from "$lib/components/ui/label/label.svelte";
    import { ToggleGroup, ToggleGroupItem } from "$lib/components/ui/toggle-group/index.js";
    import * as Card from "$lib/components/ui/card";
    import Slider from "$lib/components/ui/slider/slider.svelte";
    
    let hrsPerWeek = $state(0);
    let sex = $state(undefined);
    let handedness = $state(undefined);
    let gamingExperience = $state(undefined);

    let canSubmit = $derived(sex && handedness && gamingExperience);
</script>

<Card.Root class="-my-4 w-full max-w-sm">
    <Card.Header>
        <Card.Title>Before we begin</Card.Title>
        <Card.Description>A quick survey to help contextualise your results.</Card.Description>
    </Card.Header>
    <Card.Content>
        <form id="survey-form" class="flex flex-col gap-2" method="POST">
            <input type="hidden" name="sex" value={sex} />
            <input type="hidden" name="handedness" value={handedness} />
            <input type="hidden" name="gaming-experience" value={gamingExperience} />
            <input type="hidden" name="hrs-per-week" value={hrsPerWeek} />

            <Label for="age">Age</Label>
            <Input class="mb-2" type="number" id="age" name="age" min="16" max="99" required />
            
            <Label for="sex">Sex</Label>
            <ToggleGroup variant="outline" type="single" class="w-full mb-2" bind:value={sex}>
                <ToggleGroupItem value="male" class="grow">Male</ToggleGroupItem>
                <ToggleGroupItem value="female" class="grow">Female</ToggleGroupItem>
                <ToggleGroupItem value="other" class="grow">Prefer not to say</ToggleGroupItem>
            </ToggleGroup>
            
            <Label for="handedness">Handedness</Label>
            <ToggleGroup variant="outline" type="single" class="w-full mb-2" bind:value={handedness}>
                <ToggleGroupItem value="left" class="grow">Left-Handed</ToggleGroupItem>
                <ToggleGroupItem value="right" class="grow">Right-Handed</ToggleGroupItem>
            </ToggleGroup>
            
            <Label for="hrs-per-week">Weekly computer use (this device)</Label>
            <div class="flex gap-2 justify-between items-center">
                <span class="text-sm">0</span>
                <Slider class="flex-1" type="single" bind:value={hrsPerWeek} max={71} step={1} />
                <span class="text-sm">70</span>
            </div>
            <span class="text-sm text-muted-foreground mx-auto mb-2">
                {#if hrsPerWeek > 70}
                    ~70+ hours / week
                {:else}
                    ~{hrsPerWeek} hours / week
                {/if}
            </span>
            
            <Label for="gaming-experience">Gaming experience</Label>
            <ToggleGroup variant="outline" type="single" class="w-full mb-2" bind:value={gamingExperience}>
                <ToggleGroupItem value="none" class="grow">None</ToggleGroupItem>
                <ToggleGroupItem value="casual" class="grow">Casual</ToggleGroupItem>
                <ToggleGroupItem value="intermediate" class="grow">Intermediate</ToggleGroupItem>
                <ToggleGroupItem value="hardcore" class="grow">Hardcore</ToggleGroupItem>
            </ToggleGroup>
        </form>
    </Card.Content>
    <Card.Footer>
        <Button form="survey-form" type="submit" class="w-full cursor-pointer" disabled={!canSubmit}>Continue</Button>
    </Card.Footer>
</Card.Root>

