<script>
    import { Trial, MouseCoordinate } from '$lib/dataTypes';
    import { untrack, tick } from 'svelte';
    import { getContext } from 'svelte';

    let {
        zoneWidth   = 40,   
        distance    = 250, 
        nextTrial,
        currentTask,
        enableSampling,
        disableSampling,
        onTrialReady
    } = $props();


    const { pxPerMm } = getContext('task');

    const TRACK_WIDTH_BASE = 150*pxPerMm;
    const HANDLE_RADIUS    = 5*pxPerMm;



    let trackWidth  = $state(0);
    // Current position x position of the handler. Y is constant
    let handleX     = $state(0);
    // This adjusts target's position
    let zoneLeft    = $state(0);
    let zoneW       = $state(0);
    let zoneCenterX = $state(0);
    let isDragging = $state(false)

    let currentTrial = null;

    let trackEl = $state(null);

    let inZoneNow = $derived(
        isDragging && handleX >= zoneLeft && handleX <= zoneLeft + zoneW
    );



    function setup() {

        const sZoneWidth = zoneWidth;
        const sDistance  = distance;
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

        const trackRect = trackEl.getBoundingClientRect();
    
        const handlerXGlobal = trackRect.left + handleX;
        const handlerYGlobal = trackRect.top + trackRect.height / 2;

        const zoneCenterXGlobal = trackRect.left + zoneCenterX;
        const zoneCenterYGlobal = trackRect.top + trackRect.height / 2;

        currentTrial = new Trial(handlerXGlobal, handlerYGlobal, zoneCenterXGlobal, zoneCenterYGlobal, zoneWidth);
        onTrialReady(currentTrial)
        currentTask.addTrial(currentTrial);
    }

    $effect(() => {
        zoneWidth; distance; trackEl;
        untrack(() => { if (trackEl) setup(); });
    });

    function moveHandle(clientX) {
        if (!trackEl) return;
        const rect = trackEl.getBoundingClientRect();
        handleX = Math.max(HANDLE_RADIUS, Math.min(trackWidth - HANDLE_RADIUS, clientX - rect.left));
    }

    function onMouseDown(e) {
        
        isDragging = true;
        enableSampling()
        moveHandle(e.clientX);
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
    }

    function onMouseMove(e) {
        if (!isDragging) return;
        moveHandle(e.clientX);
    }

    function onMouseUp(e) {
        if (!isDragging) return;
        disableSampling()
        isDragging = false;
        currentTrial.complete(e.clientX, e.clientY);
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        nextTrial();
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
        
        style="left: {zoneLeft}px; width: {zoneW}px"
    >
        <div class="zone-target-line" class:zone-active={inZoneNow}>
            <div class="zone-target-accuracy-line" style="width:{HANDLE_RADIUS}px"></div>
        </div>

       
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
        height: 5px;
        transform: translateY(-50%);
        background: #a3a3a3;
        border-radius: 99px;
    }

    .zone {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        height: 1rem;
        /* background: rgba(212, 85, 57, 0.6); */
        border-left: 3px solid blue;
        border-right: 3px solid blue;
        /* border-radius: 6px; */
        pointer-events: none;
        transition: background 0.15s, border-color 0.15s;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .zone-target-line {
        width: 100%;
        height: 5px;
        background: blue;
        opacity: 0.7;
        display: flex;
        justify-content: center;
        transition: box-shadow 0.15s, border-color 0.15s;
    }

    .zone-target-line.zone-active{
        box-shadow: 0 2px 16px rgb(39, 26, 152);
    }
    .zone-target-accuracy-line {
        height: 5px;
        background: red;
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
        opacity: 80%;
    }
</style>