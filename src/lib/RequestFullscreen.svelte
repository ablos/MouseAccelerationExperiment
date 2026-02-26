<script>
    function onClick() {
        document.documentElement.requestFullscreen();
    }
</script>

<div class="flex flex-col items-center justify-center w-screen h-screen">
    <h1 class="text-2xl font-bold mb-3">Please go into fullcreen by clicking the button below</h1>
    <button onclick={onClick} class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
        Enable Fullscreen
    </button>
</div>