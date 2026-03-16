<script setup>
import { useForm } from "@inertiajs/vue3"

// 'errors' vem do Django: form.errors passado como prop pelo Inertia.
// No GET inicial, errors é um objeto vazio {}.
// No POST com validação falha, o Django redireciona de volta
// e o errors vem preenchido, ex: { "title": ["Este campo é obrigatório."] }
const props = defineProps(["errors"])

const form = useForm({
    title: "",
    director: "",
    year: "",
    genre: "",
    rating: "",
    status: "want",
    notes: "",
})

function submit() {
    form.post("/create/")
}
</script>

<template>
    <main class="container">
        <h1>Novo Filme</h1>

        <form @submit.prevent="submit">
            <label>
                Titulo
                <input v-model="form.title" :aria-invalid="!!errors.title" />
                <small v-if="errors.title" style="color: red">{{ errors.title[0] }}</small>
            </label>

            <label>
                Diretor
                <input v-model="form.director" :aria-invalid="!!errors.director" />
                <small v-if="errors.director" style="color: red">{{ errors.director[0] }}</small>
            </label>

            <div class="grid">
                <label>
                    Ano
                    <input v-model="form.year" type="number" min="0" :aria-invalid="!!errors.year" />
                    <small v-if="errors.year" style="color: red">{{ errors.year[0] }}</small>
                </label>

                <label>
                    Genero
                    <input v-model="form.genre" :aria-invalid="!!errors.genre" />
                    <small v-if="errors.genre" style="color: red">{{ errors.genre[0] }}</small>
                </label>
            </div>

            <div class="grid">
                <label>
                    Nota (0-10)
                    <input v-model="form.rating" type="number" min="0" max="10" :aria-invalid="!!errors.rating" />
                    <small v-if="errors.rating" style="color: red">{{ errors.rating[0] }}</small>
                </label>

                <label>
                    Status
                    <select v-model="form.status" :aria-invalid="!!errors.status">
                        <option value="want">Quero Ver</option>
                        <option value="watching">Assistindo</option>
                        <option value="watched">Assistido</option>
                    </select>
                    <small v-if="errors.status" style="color: red">{{ errors.status[0] }}</small>
                </label>
            </div>

            <label>
                Notas
                <textarea v-model="form.notes" :aria-invalid="!!errors.notes"></textarea>
                <small v-if="errors.notes" style="color: red">{{ errors.notes[0] }}</small>
            </label>

            <div class="grid">
                <button type="submit" :disabled="form.processing" :aria-busy="form.processing">Salvar</button>
                <a href="/" role="button" class="outline secondary">Voltar</a>
            </div>
        </form>
    </main>
</template>
