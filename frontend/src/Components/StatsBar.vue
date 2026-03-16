<script setup>
defineProps(["stats"])
</script>

<template>
    <hgroup>
        <h1>Filmes</h1>
        <p>
            Total: {{ stats.total }} |
            Quero ver: {{ stats.want }} |
            Assistindo: {{ stats.watching }} |
            Assistidos: {{ stats.watched }}
        </p>
    </hgroup>
</template>
