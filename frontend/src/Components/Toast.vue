<script setup>
import { ref, watch } from "vue"

// Recebe as flash messages do Django via Inertia shared props.
// Cada mensagem é exibida por alguns segundos e removida automaticamente.
const props = defineProps(["messages"])

const visible = ref([])

watch(() => props.messages, (msgs) => {
    if (!msgs || !msgs.length) return

    msgs.forEach((msg, i) => {
        const item = { ...msg, id: Date.now() + i }
        visible.value.push(item)

        setTimeout(() => {
            visible.value = visible.value.filter(v => v.id !== item.id)
        }, 4000)
    })
}, { immediate: true })
</script>

<template>
    <div class="toast-container">
        <div
            v-for="toast in visible"
            :key="toast.id"
            class="toast"
            :class="toast.tags"
        >
            {{ toast.message }}
        </div>
    </div>
</template>

<style scoped>
.toast-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.toast {
    padding: 0.75rem 1.25rem;
    border-radius: 0.375rem;
    color: #fff;
    font-weight: 500;
    animation: toast-in 0.3s ease, toast-out 0.3s ease 3.7s;
    min-width: 250px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toast.success {
    background-color: #10b981;
}

.toast.error {
    background-color: #ef4444;
}

.toast.warning {
    background-color: #f59e0b;
}

.toast.info {
    background-color: #3b82f6;
}

@keyframes toast-in {
    from { opacity: 0; transform: translateX(100%); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes toast-out {
    from { opacity: 1; transform: translateX(0); }
    to { opacity: 0; transform: translateX(100%); }
}
</style>
