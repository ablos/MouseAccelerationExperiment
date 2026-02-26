<script>
    import { onDestroy, onMount } from 'svelte';
    import ClickTarget from "./ClickTarget.svelte";
    import RequestFullscreen from '$lib/RequestFullscreen.svelte';
    import DebugOverlay from './DebugOverlay.svelte'; // DEBUG
    import { TaskStatus } from '$lib/enums';
    import { createMouseSampler } from './MouseSampler';

    const enableDebug = true;

    let { pxPerMm, onComplete } = $props();

    // Values in mm, designed for a reference 1080p screen
    const radii = [3, 5, 10];
    const distances = [30, 60, 120];

    // Create and shuffle trial combinations
    let trials = radii.flatMap(r => distances.map(distance => ({ r, distance })));
    trials = trials.sort(() => Math.random() - 0.5);

    // set state variables
    let currentTrial = $state(0);
    let status = $state(TaskStatus.IDLE);
    let isFullscreen = $state(false);
    let currentX = $state(0);
    let currentY = $state(0);
    let screenWidth = $state(0);
    let screenHeight = $state(0);
    let radius = $state(0);
    let innerPercentage = 0.2;

    let debugDistance = $state(0); // DEBUG
    let debugOriginX = $state(0); // DEBUG
    let debugOriginY = $state(0); // DEBUG
    let trialStartTimeStamp = 0;
    let taskStart = new Date();
    let trialStarts = [];
    let distancesFromTarget = [];

    function onMouseSample(x, y, timestamp) {
        
    }

    const sampler = createMouseSampler(onMouseSample);

    function isInBounds(x, y, r) {
        return x >= r && x <= screenWidth - r && y >= r && y <= screenHeight - r;
    }

    function getIntersectionAnglesVertical(lineX, distance, r) {
        let result = []

        // Check if circle center is even close enough to intersect
        if (Math.abs(lineX - currentX) >= distance)
            return result;

        // Get the two angles
        let t1 = Math.acos((lineX - currentX) / distance);
        let t2 = (Math.PI * 2) - t1;

        // Calculate the y values for these angles
        let y1 = currentY + distance * Math.sin(t1);
        let y2 = currentY + distance * Math.sin(t2);

        // Check if the resulting coordinates are in bounds to be included
        if (isInBounds(lineX, y1, r))
            result.push(t1);

        if (isInBounds(lineX, y2, r))
            result.push(t2);

        return result;
    }

    function getIntersectionAnglesHorizontal(lineY, distance, r) {
        let result = [];

        // Check if circle is even close enough to intersect
        if (Math.abs(lineY - currentY) >= distance)
            return result;

        // Get the two angles
        let t1 = Math.asin((lineY - currentY) / distance);
        let t2 = Math.PI - t1;

        // Calculate the x values for these angles
        let x1 = currentX + distance * Math.cos(t1);
        let x2 = currentX + distance * Math.cos(t2);

        // Check if the resulting coordinates are in bounds to be included
        if (isInBounds(x1, lineY, r))
            result.push(t1);

        if (isInBounds(x2, lineY, r))
            result.push(t2);

        return result;
    }

    // Calculates the next position based on the trials list
    function nextPosition() {
        // Retrieve trial data for current trial
        let { r, distance } = trials[currentTrial];

        // convert mm to pixels
        r *= pxPerMm;
        distance *= pxPerMm;

        // Get all intersection angles
        let angles = [];
        angles.push(...getIntersectionAnglesHorizontal(r, distance, r));
        angles.push(...getIntersectionAnglesHorizontal(screenHeight - r, distance, r));
        angles.push(...getIntersectionAnglesVertical(r, distance, r));
        angles.push(...getIntersectionAnglesVertical(screenWidth - r, distance, r));

        angles.sort((a, b) => a - b);

        // Build a list of valid arcs by testing each segment's midpoint
        let validArcs = [];

        for (let i = 0; i < angles.length; i++) {
            const start = angles[i];
            const end = i + 1 < angles.length ? angles[i + 1] : angles[0] + Math.PI * 2;
            const mid = (start + end) / 2;

            const mx = currentX + distance * Math.cos(mid);
            const my = currentY + distance * Math.sin(mid);

            if (isInBounds(mx, my, r))
                validArcs.push({ start, end });
        }

        // Pick a random angle
        const totalLength = validArcs.reduce((sum, arc) => sum + (arc.end - arc.start), 0);
        let pick = Math.random() * totalLength;

        let angle = 0;
        for (const arc of validArcs) {
            const len = arc.end - arc.start;

            if (pick <= len) {
                angle = arc.start + pick;
                break;
            }

            pick -= len;
        }

        // Set new values
        radius = r;
        debugDistance = distance; // DEBUG
        debugOriginX = currentX;  // DEBUG
        debugOriginY = currentY;  // DEBUG
        currentX = currentX + Math.cos(angle) * distance;
        currentY = currentY + Math.sin(angle) * distance;
        currentTrial += 1;
        trialStarts.push(Date.now());
        trialStartTimeStamp = performance.now();
    }

    // handles fullscreen change
    function handleFullscreenChange() {
        isFullscreen = !!document.fullscreenElement;

        // center target
        setTimeout(() => {
            screenWidth = window.innerWidth;
            screenHeight = window.innerHeight;
            currentX = screenWidth / 2;
            currentY = screenHeight / 2;
            radius = 13 * pxPerMm;
        }, 100);
    }

    function handleTaskStart() {
        console.log("Starting task...");
        document.documentElement.requestFullscreen();
        status = TaskStatus.RUNNING;
        taskStart = Date.now();
        sampler.start();
        nextPosition();
    }

    function handleTaskDone() {
        const trialEnd = Date.now();
        sampler.stop();

        status = TaskStatus.DONE;
        console.log("test done");
        document.exitFullscreen();

        onComplete();
    }

    // handles click functionality
    function handleClick(e) {
        // Don't do anything if we are not in fullscreen
        if (!isFullscreen) return;

        // calculate Euclidian distance from cursor to target
        const dist = Math.sqrt((currentX - e.clientX) ** 2 + (currentY - e.clientY) ** 2);
        
        // if status is idle and we hit the target, start the task
        if (status == TaskStatus.IDLE) {
            if (dist <= radius) {
                handleTaskStart();
            }
            return;
        }

        // Check if we hit the target
        if (dist <= radius * innerPercentage)
            console.log("BULLSEYE!");
        else if (dist <= radius)
            console.log("Hit!");
        else
            console.log("Miss.");

        // Store distance
        distancesFromTarget.push(dist);

        // Check if completed
        if (currentTrial == trials.length - 1) {
            handleTaskDone();
            return;
        }

        // Move to next position
        nextPosition();
    }

    // runs on client after page load
    onMount(() => {
        // Detect fullscreen state
        isFullscreen = !!document.fullscreenElement;
        handleFullscreenChange();

        // Add event listeners
        window.addEventListener('click', handleClick);
        document.addEventListener('fullscreenchange', handleFullscreenChange);

        // Clean up function for event listeners
        return () => {
            window.removeEventListener('click', handleClick);
            document.removeEventListener('fullscreenchange', handleFullscreenChange)
        }
    });
</script>

{#if isFullscreen}
    {#if status == TaskStatus.IDLE}
        <h1 class="text-2xl font-bold" style:top="calc(50% - {radius}px - 50px)">Click the target to start the test</h1> 
    {/if}

    <ClickTarget {radius} {innerPercentage} x={currentX} y={currentY} />

    {#if enableDebug}
        <DebugOverlay currentX={debugOriginX} currentY={debugOriginY} {screenWidth} {screenHeight} distance={debugDistance} r={radius} /> <!-- DEBUG -->
    {/if}
{:else}
    <RequestFullscreen />
{/if}

<style>

    h1 {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
    }

</style>