<script>
    let { data } = $props();
</script>

<p>Participant page for participant {data.participant.code}. Named '{data.contact?.name ?? 'unknown'}'. They did {data.sessions?.length ?? 0} sessions.</p>