<script setup>
// Dialog genérico de confirmação.
// Controla visibilidade via v-model (open).
defineProps(["open", "title", "message"])
const emit = defineEmits(["update:open", "confirm"])

function close() {
    emit("update:open", false)
}
</script>

<template>
    <dialog :open="open">
        <article>
            <header>
                <button aria-label="Close" rel="prev" @click="close"></button>
                <h3>{{ title }}</h3>
            </header>
            <p v-html="message"></p>
            <footer>
                <div class="grid">
                    <button class="outline secondary" @click="close">Cancelar</button>
                    <button class="contrast" @click="$emit('confirm')">Confirmar</button>
                </div>
            </footer>
        </article>
    </dialog>
</template>
