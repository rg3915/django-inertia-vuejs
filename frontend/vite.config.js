import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({
    plugins: [vue()],
    root: ".",
    base: "/static/",
    build: {
        outDir: "dist",
        manifest: true,
        rollupOptions: {
            input: "src/main.js",
        },
    },
    server: {
        origin: "http://localhost:5173",
    },
})
