<script>
    let { radius = 50, innerPercentage = 0.2, x = 0, y = 0 } = $props();
    let outerDiameter = $derived(radius * 2);
    let innerDiameter = $derived(outerDiameter * innerPercentage);
</script>

<div class="outer" style:width="{outerDiameter}px" style:height="{outerDiameter}px" style:left="{x - radius}px" style:top="{y - radius}px">
    <div class="inner" style:width="{innerDiameter}px" style:height="{innerDiameter}px"></div>
</div>

<style>
    .outer, .inner{
        border-radius: 50%;
    }

    .outer {
        background-color: blue;
        display: flex;
        align-items: center;
        justify-content: center;
        position: absolute;
    }

    .inner {
        background-color: red;
    }
</style>
