<script>
    import Button from "$lib/components/ui/button/button.svelte";
</script>

<form method="POST" action="?/logout">
    <Button type="submit" class="absolute top-2 right-2">
        Log out
    </Button>
</form>

<div class="flex flex-col justify-center items-center max-w-200 gap-3">
    <h1 class="text-3xl">Welcome to the experiment!</h1>
    <p>
        Some explanation about the experiment.  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vitae rhoncus tortor, ut lobortis dui. Donec eu molestie odio. Maecenas faucibus condimentum sapien, at semper enim tincidunt at. Aenean risus mi, vestibulum et nisl in, molestie sodales elit. Cras placerat dictum augue, varius rutrum magna facilisis at. Vivamus venenatis massa risus, sit amet elementum turpis gravida et. Vestibulum luctus tempor eros, at rutrum magna pellentesque ut. Etiam eget consequat sem. Ut viverra sit amet neque vel tincidunt.     Etiam placerat tincidunt ante, at scelerisque ex maximus et. Nullam quis laoreet massa, quis suscipit metus. Donec neque nibh, vestibulum ut est nec, venenatis imperdiet dolor. Praesent quis hendrerit dui. In sed mattis augue. Donec pulvinar viverra lectus. Vestibulum eget massa luctus, efficitur purus sit amet, maximus ex. Pellentesque ut sollicitudin libero. Nam quis diam luctus, pulvinar nunc nec, iaculis eros. Ut ut mi viverra, cursus nibh a, sodales neque. Vivamus egestas arcu sit amet libero varius rutrum. Mauris mollis leo ut urna malesuada, vitae bibendum turpis pharetra. Aliquam varius tellus quis posuere dapibus.    Sed vel nunc eget ipsum maximus auctor. Morbi nec consequat quam. Nulla eleifend gravida nibh, nec volutpat est cursus nec. Proin laoreet id est vel finibus. Fusce tempus efficitur auctor. Aliquam euismod id magna efficitur elementum. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Cras sed erat id nunc blandit gravida id ut libero. Vivamus eleifend metus vel orci ultrices, vitae fermentum odio tempor. Nunc rhoncus nec mi eget interdum. Integer vel orci lorem. Etiam fermentum viverra eros ut dapibus. Morbi urna quam, tempor vitae commodo id, tincidunt at est. Aenean eget felis non libero molestie vulputate. Aliquam auctor laoreet molestie. Vivamus interdum ex non tristique congue.
    </p>
    
    <Button href="/session" data-sveltekit-reload>Continue to experiment</Button>
</div>
