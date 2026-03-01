<script>
    import { onMount, getContext } from "svelte";
    import { File, Folder } from 'lucide-svelte';
    import { createMouseSampler } from "./MouseSampler";
    import { TaskStatus, TaskType } from '$lib/enums';
    import { Task, Trial } from "$lib/dataTypes";
    import { MouseCoordinate } from "$lib/dataTypes";
    
    const { pxPerMm, onComplete } = getContext('task');

    // in mm like ClickTask
    const targetSizes = [9, 15, 30];
    const distances = [30, 60, 120];

    let trials = targetSizes.flatMap(target => distances.map(distance => ({target, distance})))
    trials = trials.sort(() => Math.random() - 0.5)
    // states initialization
    let status = $state(TaskStatus.IDLE);
    let currentTrialIndex = $state(0)
    let isDragging = $state(false);
    let screenWidth = $state(window.innerWidth);
    let screenHeight = $state(window.innerHeight);
    // Target (drop zone) position
    let targetX = $state(0);
    let targetY = $state(0);
    let fileX = $state(0);
    let fileY = $state(0);
    let folderSize = $state(0);
    
    // derived states
    let folderStyle = $derived(
        `position:absolute; left:${fileX}px; top:${fileY}px; cursor:${isDragging ? 'grabbing' : 'grab'}; opacity:${isDragging ? 0.7 : 1}; transform: translate(-50%, -50%);`
    );
    let targetStyle = $derived(
        `position:absolute; left:${targetX}px; top:${targetY}px; transform: translate(-50%, -50%);`
    );
    let isOverTarget = $derived(
        isDragging && Math.sqrt((targetX - fileX) ** 2 + (targetY - fileY) ** 2) <= folderSize 
    );

    let offsetX = 0;
    let offsetY = 0;

    let currentTask = null;
    let currentTrial = null;


    // Sampler
    function onMouseSample(x, y, timestamp) {
        if (currentTrial && isDragging){
            currentTrial.addCoordinate(new MouseCoordinate(x, y, timestamp));
        } 
    }
    const sampler = createMouseSampler(onMouseSample);

    handleTaskStart();


    function isInBounds(x, y, r) {
        return x >= r && x <= screenWidth - r && y >= r && y <= screenHeight - r;
    }

    function onMouseDown(e){
        if (status === TaskStatus.IDLE) {
            
            return;
        }
        
        isDragging = true;
        offsetX = e.clientX - fileX;
        offsetY = e.clientY - fileY;
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);

    }

    function onMouseMove(e){
        if(!isDragging) return;
        fileX = e.clientX - offsetX;
        fileY = e.clientY - offsetY;

    }


    function onMouseUp(e){
        isDragging = false;
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        isOverTarget = false;

        currentTrial.complete(e.clientX, e.clientY);
        if (currentTrialIndex >= trials.length) {
            handleTaskDone();
            return;
        }

        runTrial(e.clientX, e.clientY);
    }


    function runTrial() {
        let { target, distance } = trials[currentTrialIndex];

        // convert mm to px
        const size = target * pxPerMm;
        const dist = distance * pxPerMm;

        // Place folder at center or current target position
        fileX = size + Math.random() * (screenWidth - size * 2);
        fileY = size + Math.random() * (screenHeight - size * 2);
        folderSize = size;

        

        // Pick a random angle for the target drop zone
        let angle = Math.random() * Math.PI * 2;
        let newTargetX = fileX + Math.cos(angle) * dist;
        let newTargetY = fileY + Math.sin(angle) * dist;

        // Keep trying until in bounds
        let attempts = 0;
        while (!isInBounds(newTargetX, newTargetY, size) && attempts < 30) {
            angle = Math.random() * Math.PI * 2;
            newTargetX = fileX + Math.cos(angle) * dist;
            newTargetY = fileY + Math.sin(angle) * dist;
            attempts++;
        }

        targetX = newTargetX;
        targetY = newTargetY;

        currentTrialIndex++;
        currentTrial = new Trial(fileX, fileY, targetX, targetY, size);
        currentTask.addTrial(currentTrial);
    }

    function handleTaskStart() {
        status = TaskStatus.RUNNING;
        currentTask = new Task(TaskType.DRAGGING);
        sampler.start();
        runTrial();
    }

    function handleTaskDone() {
        currentTask.complete();
        sampler.stop();
        status = TaskStatus.DONE;
        onComplete(currentTask);
    }

    onMount(()=>{

        return () => sampler.stop();
    })


</script>

<div class="container">
    <div style={targetStyle}>
        <Folder 
            size={folderSize} 
            color="blue"
            style="transition: color 0.15s, filter 0.15s; filter: {isOverTarget ? 'drop-shadow(0 0 12px #22c55e)' : 'none'};"
         />
    </div>

    <!-- Draggable file -->
    <div
        style={folderStyle}
        onmousedown={onMouseDown}
        role="button"
        tabindex="0"
        onkeydown={onMouseDown}
    >
        <File size={folderSize} color="gray" />
    </div>
</div>


<style>
    .container {

        height: 100vh;
        position: relative;
    }


</style>