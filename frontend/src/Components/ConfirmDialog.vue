<script setup>
import { ref, watch } from "vue"
import { useModal } from "../composables/useModal"

// Dialog genérico de confirmação.
// Controla visibilidade via v-model (open).
const props = defineProps(["open", "title", "message"])
const emit = defineEmits(["update:open", "confirm"])

const dialogRef = ref(null)
const { isOpen, open, close } = useModal(dialogRef)

// Sincroniza v-model:open do pai com o estado interno do modal
watch(() => props.open, (val) => {
    if (val && !isOpen.value) open()
    if (!val && isOpen.value) close()
})

function handleClose() {
    close()
    emit("update:open", false)
}
</script>

<template>
    <dialog ref="dialogRef" @close="handleClose">
        <article>
            <header>
                <button aria-label="Close" rel="prev" @click="handleClose"></button>
                <h3>{{ title }}</h3>
            </header>
            <p v-html="message"></p>
            <footer>
                <div class="grid">
                    <button class="outline secondary" @click="handleClose">Cancelar</button>
                    <button class="contrast" @click="$emit('confirm')">Confirmar</button>
                </div>
            </footer>
        </article>
    </dialog>
</template>
