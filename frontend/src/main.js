import "@picocss/pico"
import { createApp, h } from "vue"
import { createInertiaApp } from "@inertiajs/vue3"

createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob("./Pages/**/*.vue", { eager: true })
        return pages[`./Pages/${name}.vue`]
    },

    // A partir do Inertia v3 o axios foi trocado por um cliente XHR próprio,
    // que por padrão usa os nomes de CSRF do Laravel (XSRF-TOKEN / X-XSRF-TOKEN).
    // Aqui ensinamos o cliente a falar a língua do Django — assim o settings.py
    // fica com os padrões do framework, sem gambiarra dos dois lados.
    http: {
        xsrfCookieName: "csrftoken",
        xsrfHeaderName: "X-CSRFToken",
    },

    setup({ el, App, props, plugin }) {
        createApp({ render: () => h(App, props) })
            .use(plugin)
            .mount(el)
    },
})
