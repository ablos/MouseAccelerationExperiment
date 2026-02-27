<script>
    import { onDestroy, onMount, getContext } from 'svelte';
    import ClickTarget from "./ClickTarget.svelte";
    import DebugOverlay from './DebugOverlay.svelte'; // DEBUG
    import { createMouseSampler } from './MouseSampler';
    import { TaskStatus, TaskType } from '$lib/enums';
	import { Task, Trial, MouseCoordinate } from '$lib/dataTypes';
    import RequestFullscreen from '$lib/RequestFullscreen.svelte';

    const enableDebug = false;

    const { pxPerMm, isFullscreen, onComplete} = getContext('task');

    // Values in mm, designed for a reference 1080p screen
    const radii = [3, 5, 10];
    const distances = [30, 60, 120];

    // Create and shuffle trial combinations
    let trials = radii.flatMap(r => distances.map(distance => ({ r, distance })));
    trials = trials.sort(() => Math.random() - 0.5);

    // set state variables
    let currentTrialIndex = $state(0);
    let status = $state(TaskStatus.IDLE);
    let screenWidth = $state(0);
    let screenHeight = $state(0);
    let targetX = $state(0);
    let targetY = $state(0);
    let radius = $state(0);
    let innerPercentage = 0.2;

    let debugDistance = $state(0); // DEBUG
    let debugOriginX = $state(0); // DEBUG
    let debugOriginY = $state(0); // DEBUG

    let currentTask = null;
    let currentTrial = null;

    function onMouseSample(x, y, timestamp) {
        currentTrial.addCoordinate(new MouseCoordinate(x, y, currentTrial.startTime));
    }

    const sampler = createMouseSampler(onMouseSample);

    function isInBounds(x, y, r) {
        return x >= r && x <= screenWidth - r && y >= r && y <= screenHeight - r;
    }

    function getIntersectionAnglesVertical(lineX, distance, r) {
        let result = []

        // Check if circle center is even close enough to intersect
        if (Math.abs(lineX - targetX) >= distance)
            return result;

        // Get the two angles
        let t1 = Math.acos((lineX - targetX) / distance);
        let t2 = (Math.PI * 2) - t1;

        // Calculate the y values for these angles
        let y1 = targetY + distance * Math.sin(t1);
        let y2 = targetY + distance * Math.sin(t2);

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
        if (Math.abs(lineY - targetY) >= distance)
            return result;

        // Get the two angles
        let t1 = Math.asin((lineY - targetY) / distance);
        let t2 = Math.PI - t1;

        // Calculate the x values for these angles
        let x1 = targetX + distance * Math.cos(t1);
        let x2 = targetX + distance * Math.cos(t2);

        // Check if the resulting coordinates are in bounds to be included
        if (isInBounds(x1, lineY, r))
            result.push(t1);

        if (isInBounds(x2, lineY, r))
            result.push(t2);

        return result;
    }

    // Calculates the next position based on the trials list
    function runTrial(cursorX, cursorY) {
        // Retrieve trial data for current trial
        let { r, distance } = trials[currentTrialIndex];

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

            const mx = targetX + distance * Math.cos(mid);
            const my = targetY + distance * Math.sin(mid);

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
         // Set new values
        radius = r;
        debugDistance = distance; // DEBUG
        debugOriginX = targetX;  // DEBUG
        debugOriginY = targetY;  // DEBUG
        targetX = targetX + Math.cos(angle) * distance;
        targetY = targetY + Math.sin(angle) * distance;
        currentTrialIndex += 1;
        currentTrial = new Trial(cursorX, cursorY, targetX, targetY, radius);
        currentTask.addTrial(currentTrial);

    }

    // handles fullscreen change
    function handleFullscreenChange() {

        // center target
        setTimeout(() => {
            screenWidth = window.innerWidth;
            screenHeight = window.innerHeight;
            targetX = screenWidth / 2;
            targetY = screenHeight / 2;
            radius = 13 * pxPerMm;
        }, 100);
    }


    function handleTaskStart(cursorX, cursorY) {
        status = TaskStatus.RUNNING;

        currentTask = new Task(TaskType.CLICKING);

        sampler.start();
        runTrial(cursorX, cursorY);
    }

    function handleTaskDone() {
        currentTask.complete();
        sampler.stop();
        status = TaskStatus.DONE;
        // document.exitFullscreen();

        console.log(currentTask);

        onComplete(currentTask)
    }

    // handles click functionality
    function handleClick(e) {
        // Don't do anything if we are not in fullscreen
        if (!isFullscreen) return;

        // calculate Euclidian distance from cursor to target
        const dist = Math.sqrt((targetX - e.clientX) ** 2 + (targetY - e.clientY) ** 2);
        
        // if status is idle and we hit the target, start the task
        if (status == TaskStatus.IDLE) {
            if (dist <= radius) {
                handleTaskStart(e.clientX, e.clientY);
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

        // Store trial
        currentTrial.complete(e.clientX, e.clientY);

        // Check if completed
        if (currentTrialIndex == trials.length) {
            handleTaskDone();
            return;
        }

        // Move to next position
        runTrial(e.clientX, e.clientY);
    }

    // runs on client after page load
    onMount(() => {
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
    $effect(()=>{
        console.log("RERENDERED")
    })
</script>


    {#if status == TaskStatus.IDLE}
        <h1 class="text-2xl font-bold" style:top="calc(50% - {radius}px - 50px)">Click the target to start the test</h1> 
    {/if}

    <ClickTarget {radius} {innerPercentage} x={targetX} y={targetY} />

    {#if enableDebug}
        <DebugOverlay currentX={debugOriginX} currentY={debugOriginY} {screenWidth} {screenHeight} distance={debugDistance} r={radius} /> <!-- DEBUG -->
    {/if}
    


<style>

    h1 {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
    }

</style>