<script setup>
import { ref, watch } from "vue"

// O tema já foi aplicado no <html> pelo script inline do base.html, antes da
// primeira pintura. Aqui só lemos o estado atual e passamos a controlá-lo.
const isDark = ref(document.documentElement.dataset.theme === "dark")

watch(isDark, (dark) => {
    const theme = dark ? "dark" : "light"
    // O Pico troca a paleta inteira a partir deste atributo no <html>.
    document.documentElement.dataset.theme = theme
    try {
        localStorage.setItem("theme", theme)
    } catch {
        // Navegação privada ou storage bloqueado: o tema vale só nesta sessão.
    }
})
</script>

<template>
    <label class="theme-switch">
        <input type="checkbox" role="switch" v-model="isDark" />
        {{ isDark ? "Escuro" : "Claro" }}
    </label>
</template>

<style scoped>
.theme-switch {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    white-space: nowrap;
}
</style>
