<script setup>
import { ref, watch } from "vue"
import { usePage } from "@inertiajs/vue3"

// A partir do Inertia v3 as mensagens do django.contrib.messages são nativas:
// o inertia-django as coloca em page.flash.messages, no topo do page object
// (não é mais uma prop, e não precisa mais de middleware customizado).
// Cada item vem no formato { level, message }, onde level é 'success',
// 'error', 'warning' ou 'info' — exatamente as tags do Django.
const page = usePage()

const visible = ref([])

watch(() => page.flash?.messages, (msgs) => {
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
            :class="toast.level"
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
