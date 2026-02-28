export function createMouseSampler(onSample, targetFps = 60) 
{
    const interval = 1000 / targetFps;
    
    let mouseX = 0;
    let mouseY = 0;
    let lastSampleTime = 0;
    let rafId = 0;
    let startTime = Date.now();
    
    function onMouseMove(e) 
    {
        mouseX = e.clientX;
        mouseY = e.clientY;
    }
    
    function sample(timestamp) 
    {
        if (timestamp - lastSampleTime >= interval) 
        {
            lastSampleTime = timestamp;
            
            // Only sample if mouse actually moved
            if (mouseX !== 0 || mouseY !== 0)
                onSample(mouseX, mouseY, Date.now() - startTime);
        }
        
        rafId = requestAnimationFrame(sample);
    }
    
    return {
        start() 
        {
            window.addEventListener('mousemove', onMouseMove);
            rafId = requestAnimationFrame(sample);
            startTime = Date.now();
        },
        stop() 
        {
            window.removeEventListener('mousemove', onMouseMove);
            cancelAnimationFrame(rafId);
        }
    };
}