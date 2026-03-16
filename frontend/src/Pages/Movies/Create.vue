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
    <div>
        <h1>Novo Filme</h1>
        <form @submit.prevent="submit">
            <div>
                <label>Titulo</label>
                <input v-model="form.title" />
                <span v-if="errors.title" style="color: red">{{ errors.title[0] }}</span>
            </div>
            <div>
                <label>Diretor</label>
                <input v-model="form.director" />
                <span v-if="errors.director" style="color: red">{{ errors.director[0] }}</span>
            </div>
            <div>
                <label>Ano</label>
                <input v-model="form.year" type="number" min="0" />
                <span v-if="errors.year" style="color: red">{{ errors.year[0] }}</span>
            </div>
            <div>
                <label>Genero</label>
                <input v-model="form.genre" />
                <span v-if="errors.genre" style="color: red">{{ errors.genre[0] }}</span>
            </div>
            <div>
                <label>Nota (0-10)</label>
                <input v-model="form.rating" type="number" min="0" max="10" />
                <span v-if="errors.rating" style="color: red">{{ errors.rating[0] }}</span>
            </div>
            <div>
                <label>Status</label>
                <select v-model="form.status">
                    <option value="want">Quero Ver</option>
                    <option value="watching">Assistindo</option>
                    <option value="watched">Assistido</option>
                </select>
                <span v-if="errors.status" style="color: red">{{ errors.status[0] }}</span>
            </div>
            <div>
                <label>Notas</label>
                <textarea v-model="form.notes"></textarea>
                <span v-if="errors.notes" style="color: red">{{ errors.notes[0] }}</span>
            </div>
            <button type="submit" :disabled="form.processing">Salvar</button>
        </form>
        <a href="/">Voltar</a>
    </div>
</template>
