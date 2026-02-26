<script>
    let { currentX, currentY, screenWidth, screenHeight, distance, r } = $props();
</script>

<!-- DEBUG: remove this component and its usage in ClickTask.svelte when done -->
<svg class="debug-overlay" width={screenWidth} height={screenHeight}>
    <!-- Valid bounds for target center (inset by r on all sides) -->
    <rect
        x={r} y={r}
        width={screenWidth - 2 * r} height={screenHeight - 2 * r}
        fill="none"
        stroke="rgba(0, 220, 0, 0.7)"
        stroke-width="1.5"
        stroke-dasharray="6,4"
    />

    <!-- Circle of possible next positions (radius = distance from current center) -->
    <circle
        cx={currentX} cy={currentY} r={distance}
        fill="none"
        stroke="rgba(255, 140, 0, 0.7)"
        stroke-width="1.5"
    />

    <!-- Marker at current target center -->
    <circle cx={currentX} cy={currentY} r="4" fill="rgba(255, 140, 0, 0.9)" />
    <line x1={currentX - 8} y1={currentY} x2={currentX + 8} y2={currentY} stroke="rgba(255,140,0,0.9)" stroke-width="1" />
    <line x1={currentX} y1={currentY - 8} x2={currentX} y2={currentY + 8} stroke="rgba(255,140,0,0.9)" stroke-width="1" />
</svg>

<style>
    .debug-overlay {
        position: fixed;
        top: 0;
        left: 0;
        pointer-events: none;
        z-index: 999;
    }
</style>
