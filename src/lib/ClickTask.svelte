<script>
    import { onMount } from 'svelte';
    import ClickTarget from "./ClickTarget.svelte";
    import RequestFullscreen from './RequestFullscreen.svelte';
    import { TaskStatus } from './enums';

    const sizes = [10, 20, 40];
    const distances = [100, 200, 400];

    // Create and shuffle trial combinations
    let trials = sizes.flatMap(size => distances.map(distance => ({ size, distance })));
    trials = trials.sort(() => Math.random() - 0.5);

    // set state variables
    let currentTrial = $state(0);
    let status = $state(TaskStatus.IDLE);
    let isFullscreen = $state(false);
    let x = $state(0);
    let y = $state(0);
    let radius = $state(50);
    let innerPercentage = 0.2;

    function getBlockedArc(k, offset = 0) {
        if (k <= -1) return null;
        if (k >= 1) return [0, Math.PI * 2];
        const a = Math.acos(k);
        return [(a + offset) % (Math.PI * 2), (Math.PI * 2 - a + offset) % (Math.PI * 2)];
    }

    function subtractArc(intervals, blocked) {
        if (!blocked) return intervals;
        let [bs, be] = blocked;
        
        // Handle wrapped arc by splitting into two subtractions
        if (bs > be + 0.0001) {
            intervals = subtractArc(intervals, [bs, Math.PI * 2]);
            intervals = subtractArc(intervals, [0, be]);
            return intervals;
        }
        
        const result = [];
        for (const [s, e] of intervals) {
            if (bs <= s && be >= e) continue;
            if (bs >= e || be <= s) { result.push([s, e]); continue; }
            if (bs > s) result.push([s, bs]);
            if (be < e) result.push([be, e]);
        }
        return result;
    }

    // Calculates the next position based on the trials list
    function nextPosition() {
        let { size, distance } = trials[currentTrial];
        const W = window.innerWidth;
        const H = window.innerHeight;
        const r = size;

        // Calculate blocked arcs
        const blockedArcs = [
            getBlockedArc((r - x) / distance),
            getBlockedArc((x - (W - r)) / distance),
            getBlockedArc((r - y) / distance, Math.PI / 2),
            getBlockedArc((y - (H - r)) / distance, Math.PI / 2),
        ];

        // Subtract blocked arcs from full circle
        let valid = [[0, Math.PI * 2]];
        for (const arc of blockedArcs) {
            valid = subtractArc(valid, arc);
        }

        // No valid angle (this should never happen)
        if (valid.length === 0) throw new Error('No valid movement arcs available');

        // Pick random angle from valid arcs weighted by length
        const totalLength = valid.reduce((sum, [s, e]) => sum + e - s, 0);
        let rand = Math.random() * totalLength;
        let angle;
        for (const [s, e] of valid) {
            if (rand <= e - s) { angle = s + rand; break; }
            rand -= e - s;
        }

        // Set new values
        radius = r;
        x = x + Math.cos(angle) * distance;
        y = y + Math.sin(angle) * distance;
        currentTrial += 1;
    }

    // handles fullscreen change
    function handleFullscreenChange() {
        isFullscreen = !!document.fullscreenElement;

        // center target
        setTimeout(() => {
            x = window.innerWidth / 2;
            y = window.innerHeight / 2;
        }, 100);
    }

    // handles click functionality
    function handleClick(e) {
        // Don't do anything if we are not in fullscreen
        if (!isFullscreen) return;

        // calculate Euclidian distance from cursor to target
        const dist = Math.sqrt((x - e.clientX) ** 2 + (y - e.clientY) ** 2);
        
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

    <ClickTarget {radius} {innerPercentage} {x} {y} />
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