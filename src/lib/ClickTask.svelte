<script>
    import { onMount } from 'svelte';
    import ClickTarget from "./ClickTarget.svelte";
    import RequestFullscreen from './RequestFullscreen.svelte';
    import { TaskStatus } from './enums';

    const radii = [10, 20, 40];
    const distances = [100, 200, 400];

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
    let radius = $state(50);
    let innerPercentage = 0.2;

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

        console.log(r);
        console.log(distance);

        // Get all intersection angles
        let angles = [];
        angles.push(...getIntersectionAnglesHorizontal(r, distance, r));
        angles.push(...getIntersectionAnglesHorizontal(screenHeight - r, distance, r));
        angles.push(...getIntersectionAnglesVertical(r, distance, r));
        angles.push(...getIntersectionAnglesVertical(screenWidth - r, distance, r));

        console.log(angles);

        // Set new values
        radius = r;
        // currentX = currentX + Math.cos(angle) * distance;
        // currentY = currentY + Math.sin(angle) * distance;
        currentTrial += 1;
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
        }, 100);
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
                console.log("Starting task...");
                document.documentElement.requestFullscreen();
                status = TaskStatus.RUNNING;
                nextPosition();
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