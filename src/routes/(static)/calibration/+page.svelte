<script>
    import { goto } from '$app/navigation';
    import Button from '$lib/components/ui/button/button.svelte';
	import { onMount } from 'svelte';

    const CARD_WIDTH_MM = 85.6;
    const CARD_ASPECT = 85.6 / 54;

    let rectWidth = $state(300);
    let dragging = false;
    let startX = 0;
    let startWidth = 0;
    let containerWidth = $state(600);

    function onPointerDown(e) {
        dragging = true;
        startX = e.clientX;
        startWidth = rectWidth;
        e.currentTarget.setPointerCapture(e.pointerId);
    }

    function onPointerMove(e) {
        if (!dragging) return;
        rectWidth = Math.max(100, Math.min(containerWidth, startWidth + e.clientX - startX));
    }

    function onPointerUp() {
        dragging = false;
    }

    function confirm() {
        const pxPerMm = rectWidth / CARD_WIDTH_MM;
        localStorage.setItem('pxPerMm', String(pxPerMm));
        goto('/session');
    }
</script>

<div class="flex flex-col items-center gap-6 w-full max-w-2xl">
    <div class="max-w-lg text-center">
        <h1 class="text-2xl font-bold">Screen Calibration</h1>
        <p class="text-muted-foreground mt-2">
            In order to make sure the tasks are identical for everyone we need to do a screen calibration to find your
            screen's pixel density. This is a one-time setup for this computer.
        </p>
    </div>

    <div class="w-full rounded-lg border bg-card p-6 flex flex-col gap-4">
        <p class="text-sm max-w-lg text-center mx-auto">
            Hold a credit card (or any bank card) up to your screen. Drag the right
            edge of the rectangle below until it matches the width of your card.
        </p>

        <div
            class="w-full relative"
            style:height="{containerWidth / CARD_ASPECT}px"
            bind:clientWidth={containerWidth}
        >
            <div
                class="absolute top-0 left-0 rounded-lg border-2 border-primary bg-primary/10 select-none touch-none"
                style:width="{rectWidth}px"
                style:height="{rectWidth / CARD_ASPECT}px"
            >
                <div
                    class="absolute right-0 top-0 bottom-0 w-3 cursor-ew-resize bg-primary rounded-r-md touch-none"
                    role="separator"
                    aria-label="Drag to resize"
                    aria-orientation="vertical"
                    onpointerdown={onPointerDown}
                    onpointermove={onPointerMove}
                    onpointerup={onPointerUp}
                    onpointercancel={onPointerUp}
                ></div>
            </div>
        </div>
    </div>

    <Button onclick={confirm} class="w-full cursor-pointer">Confirm &amp; Continue</Button>
</div>
