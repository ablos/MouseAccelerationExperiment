<script>
  import { untrack } from 'svelte';
  let {
    zoneWidth   = 40,   // px at 1080p baseline
    distance    = 250,  // px at 1080p baseline
    onCommit    = (result) => {}  // callback: { hit, reactionTime, errorPx, accuracy }
  } = $props();

  const TRACK_WIDTH_BASE = 800;
  const HANDLE_RADIUS    = 16;
  const scaleX = 1;
  // Layout (scaled px)
  let trackWidth  = $state(0);
  let handleX     = $state(0);
  let zoneLeft    = $state(0);
  let zoneW       = $state(0);
  let zoneCenterX = $state(0);

  // Drag
  let isDragging  = $state(false);
  let dragStarted = $state(false);
  let startTime   = $state(null);

  // Committed result (for visual state after release)
  let committed   = $state(false);
  let hitResult   = $state(false);

  let trackEl = $state(null);

  let inZoneNow = $derived(
    isDragging && handleX >= zoneLeft && handleX <= zoneLeft + zoneW
  );

  function setup() {
    const sZoneWidth = zoneWidth;
    const sDistance  = distance ;
    trackWidth = TRACK_WIDTH_BASE;

    const halfZone = sZoneWidth / 2;
    const padding  = sZoneWidth;
    const zoneMin  = padding + halfZone;
    const zoneMax  = trackWidth - padding - halfZone;

    zoneCenterX = zoneMin + Math.random() * (zoneMax - zoneMin);
    zoneLeft    = zoneCenterX - halfZone;
    zoneW       = sZoneWidth;

    const dir = Math.random() < 0.5 ? -1 : 1;
    let hx = zoneCenterX + dir * sDistance;
    hx = Math.max(HANDLE_RADIUS, Math.min(trackWidth - HANDLE_RADIUS, hx));
    handleX = hx;

    committed   = false;
    hitResult   = false;
    dragStarted = false;
    startTime   = null;
  }

  $effect(() => {
    // Track props as triggers only; write state via untrack to avoid cycles
    zoneWidth; distance; trackEl;
    untrack(() => { if (trackEl) setup(); });
  });

  function moveHandle(clientX) {
    if (!trackEl) return;
    const rect = trackEl.getBoundingClientRect();
    handleX = Math.max(HANDLE_RADIUS, Math.min(trackWidth - HANDLE_RADIUS, clientX - rect.left));
  }

  function commit() {
    if (committed) return;
    committed = true;

    const elapsed  = startTime ? (performance.now() - startTime) : 0;
    const inZone   = handleX >= zoneLeft && handleX <= zoneLeft + zoneW;
    const error    = Math.abs(handleX - zoneCenterX);
    const accuracy = inZone ? Math.max(0, 1 - error / (zoneW / 2)) : 0;

    hitResult = inZone;

    onCommit({
      hit:          inZone,
      reactionTime: Math.round(elapsed),
      errorPx:      Math.round(error / scaleX),
      accuracy:     Math.round(accuracy * 100)
    });
  }

  function onMouseDown(e) {
    if (committed) {
      return;
    }
    isDragging = true;
    moveHandle(e.clientX);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }

  function onMouseMove(e) {
    if (!isDragging) return;
    if (!dragStarted) { dragStarted = true; startTime = performance.now(); }
    moveHandle(e.clientX);
  }

  function onMouseUp() {
    if (!isDragging) return;
    isDragging = false;
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
    commit();
  }

</script>

<div
  class="track"
  bind:this={trackEl}
  style="width: {trackWidth}px"

>
  <div class="track-line"></div>

  <div
    class="zone"
    class:zone-active={inZoneNow || (committed )}
    style="left: {zoneLeft}px; width: {zoneW}px"
  >
    <div class="zone-center"></div>
  </div>

  <div
    role="slider"
    aria-valuenow={Math.round(handleX)}
    tabindex="0"
    onmousedown={onMouseDown}

    class="handle"
    class:dragging={isDragging}
    
    style="left: {handleX}px; width: {HANDLE_RADIUS}px; height: {HANDLE_RADIUS}px"
  ></div>
</div>

<style>
  .track {
    position: relative;
    height: 56px;
    
    user-select: none;
    flex-shrink: 0;
  }

  .track:active { cursor: grabbing; }

  .track-line {
    position: absolute;
    top: 50%;
    left: 0; right: 0;
    height: 4px;
    transform: translateY(-50%);
    background: #2a2a35;
    border-radius: 99px;
  }

  .zone {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    height: 56px;
    background: rgba(212, 85, 57, 0.6);
    border: 1.5px solid rgba(36, 36, 36, 0.35);
    border-radius: 6px;
    pointer-events: none;
    transition: background 0.15s, border-color 0.15s;
  }

  .zone.zone-active {
    background: rgba(207, 53, 14, 0.25);
    border-color: #ec382f;
  }

  .zone-center {
    position: absolute;
    top: 0; bottom: 0;
    left: 50%;
    width: 2px;
    transform: translateX(-50%);
    background: #292929;
    opacity: 0.7;
  }

  .handle {
    position: absolute;
    top: 50%;
    border-radius: 50%;
    background: #f0f0f0;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 0 3px #0d0d10, 0 0 0 5px #f0f0f0;
    transition: box-shadow 0.15s;
    cursor: grab;
  }

  .handle.dragging {
    box-shadow: 0 0 0 3px #0d0d10, 0 0 0 5px #e8ff5a, 0 0 20px rgba(232,255,90,0.35);
  }
</style>