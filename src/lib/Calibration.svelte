<script>
    let { oncalibrated } = $props();

    const CARD_WIDTH_MM = 85.6;
    const CARD_ASPECT = 85.6 / 54;

    let rectWidth = $state(300);
    let dragging = false;
    let startX = 0;
    let startWidth = 0;

    function onPointerDown(e) {
        dragging = true;
        startX = e.clientX;
        startWidth = rectWidth;
        e.currentTarget.setPointerCapture(e.pointerId);
    }

    function onPointerMove(e) {
        if (!dragging) return;
        rectWidth = Math.max(100, startWidth + e.clientX - startX);
    }

    function onPointerUp() {
        dragging = false;
    }

    function confirm() {
        const pxPerMm = rectWidth / CARD_WIDTH_MM;
        localStorage.setItem('pxPerMm', String(pxPerMm));
        oncalibrated(pxPerMm);
    }
</script>

<div class="calibration">
    <h1 class="text-2xl font-bold">Screen Calibration</h1>
    <p>Drag the right edge of the rectangle until it matches the width of a credit card held up to your screen, then click Confirm.</p>

    <div class="card-container">
        <div class="card" style:width="{rectWidth}px" style:height="{rectWidth / CARD_ASPECT}px">
            <div
                class="handle"
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

    <button class="confirm-btn" onclick={confirm}>Confirm</button>
</div>

<style>
    .calibration {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2rem;
        padding: 4rem;
        max-width: 600px;
        margin: 0 auto;
        text-align: center;
    }

    .card-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        width: 100%;
        min-height: 120px;
    }

    .card {
        position: relative;
        background: #dde4ff;
        border: 2px solid #5566cc;
        border-radius: 8px;
        flex-shrink: 0;
        touch-action: none;
        user-select: none;
    }

    .handle {
        position: absolute;
        right: 0;
        top: 0;
        bottom: 0;
        width: 12px;
        cursor: ew-resize;
        background: #5566cc;
        border-radius: 0 6px 6px 0;
        touch-action: none;
    }

    .confirm-btn {
        padding: 0.6rem 2rem;
        background: #5566cc;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 1rem;
        cursor: pointer;
    }

    .confirm-btn:hover {
        background: #4455bb;
    }
</style>
