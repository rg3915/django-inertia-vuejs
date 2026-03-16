<script setup>
import { useForm } from "@inertiajs/vue3"

// 'movie' vem do Django: movie.serializable_values() passado como prop pelo Inertia.
// O useForm inicializa os campos do formulário com os valores atuais do filme.
const props = defineProps(["movie"])

const form = useForm({
    title: props.movie.title,
    director: props.movie.director,
    year: props.movie.year || "",
    genre: props.movie.genre,
    status: props.movie.status,
    notes: props.movie.notes,
})

function submit() {
    form.post(`/${props.movie.id}/update/`)
}
</script>

<template>
    <div>
        <h1>Editar: {{ movie.title }}</h1>
        <form @submit.prevent="submit">
            <div>
                <label>Titulo</label>
                <input v-model="form.title" required />
            </div>
            <div>
                <label>Diretor</label>
                <input v-model="form.director" />
            </div>
            <div>
                <label>Ano</label>
                <input v-model="form.year" type="number" />
            </div>
            <div>
                <label>Genero</label>
                <input v-model="form.genre" />
            </div>
            <div>
                <label>Status</label>
                <select v-model="form.status">
                    <option value="want">Quero Ver</option>
                    <option value="watching">Assistindo</option>
                    <option value="watched">Assistido</option>
                </select>
            </div>
            <div>
                <label>Notas</label>
                <textarea v-model="form.notes"></textarea>
            </div>
            <button type="submit" :disabled="form.processing">Salvar</button>
        </form>
        <a href="/">Voltar</a>
    </div>
</template>
