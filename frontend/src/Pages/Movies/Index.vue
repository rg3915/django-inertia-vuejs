<script setup>
import { ref, onMounted } from "vue"
import { router, useForm } from "@inertiajs/vue3"
import StatsBar from "../../Components/StatsBar.vue"
import MovieTable from "../../Components/MovieTable.vue"
import MovieFormDialog from "../../Components/MovieFormDialog.vue"
import ConfirmDialog from "../../Components/ConfirmDialog.vue"

// defineProps é uma macro do Vue 3 que declara quais dados o componente espera receber.
// Quem passa esses dados é o Django — quando a view faz:
//   render(request, "Movies/Index", props={"movies": data, "stats": {...}})
// o Inertia serializa esse dict como JSON e injeta como props no componente Vue.
//
// Quando uma validação falha no backend, o Django re-renderiza Movies/Index
// com props extras: errors, showDialog, editMovie e formData.
// Isso permite reabrir o dialog com os dados preenchidos e os erros exibidos.
const props = defineProps([
    "movies", "stats",
    "errors", "showDialog", "editMovie", "formData",
])

// --- Estado dos dialogs ---
// Controlados por refs locais (reativo). O Vue atualiza o DOM automaticamente
// quando qualquer ref muda — sem manipulação manual de DOM.
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)
const movieToDelete = ref(null)
const editingMovieId = ref(null)

// --- Form de criação ---
// useForm é um helper do Inertia que cria um objeto reativo com os campos
// do formulário, estado de processamento e métodos para enviar (post, put, etc).
const createForm = useForm({
    title: "",
    director: "",
    year: "",
    genre: "",
    rating: "",
    status: "want",
    notes: "",
})

function openCreate() {
    createForm.reset()
    showCreateDialog.value = true
}

// createForm.post() faz um POST diretamente para uma rota do Django.
// A URL `/create/` é uma rota definida no urls.py — não existe Vue Router.
// O Inertia intercepta a resposta: se for um redirect 302 (sucesso),
// busca os novos dados via JSON e atualiza a página sem recarregar.
// Se for uma re-renderização (erro de validação), atualiza os props
// e o dialog reabre com os erros exibidos.
function submitCreate() {
    createForm.post("/create/", {
        onSuccess: () => { showCreateDialog.value = false },
    })
}

// --- Form de edição ---
const editForm = useForm({
    title: "",
    director: "",
    year: "",
    genre: "",
    rating: "",
    status: "want",
    notes: "",
})

function openEdit(movie) {
    editingMovieId.value = movie.id
    editForm.title = movie.title
    editForm.director = movie.director
    editForm.year = movie.year || ""
    editForm.genre = movie.genre
    editForm.rating = movie.rating || ""
    editForm.status = movie.status
    editForm.notes = movie.notes
    showEditDialog.value = true
}

function submitEdit() {
    editForm.post(`/${editingMovieId.value}/update/`, {
        onSuccess: () => { showEditDialog.value = false },
    })
}

// --- Delete ---
// router.post() faz um POST diretamente para uma rota do Django.
// O Inertia intercepta a resposta (um redirect 302), busca os novos dados
// via JSON e troca o componente sem recarregar a página.
function confirmDelete(movie) {
    movieToDelete.value = movie
    showDeleteDialog.value = true
}

function executeDelete() {
    router.post(`/${movieToDelete.value.id}/delete/`, {}, {
        onSuccess: () => {
            showDeleteDialog.value = false
            movieToDelete.value = null
        },
    })
}

// --- Reabrir dialog se o servidor retornou com erros de validação ---
// Quando o Django detecta erro de validação, ele re-renderiza Movies/Index
// com showDialog='create' ou 'edit', junto com formData (dados submetidos)
// e errors. O onMounted lê esses props e reabre o dialog automaticamente,
// mantendo os dados que o usuário digitou e exibindo os erros.
onMounted(() => {
    if (props.showDialog === "create" && props.formData) {
        createForm.title = props.formData.title || ""
        createForm.director = props.formData.director || ""
        createForm.year = props.formData.year || ""
        createForm.genre = props.formData.genre || ""
        createForm.rating = props.formData.rating || ""
        createForm.status = props.formData.status || "want"
        createForm.notes = props.formData.notes || ""
        showCreateDialog.value = true
    }

    if (props.showDialog === "edit" && props.editMovie) {
        editingMovieId.value = props.editMovie.id
        editForm.title = props.formData?.title || props.editMovie.title
        editForm.director = props.formData?.director || props.editMovie.director
        editForm.year = props.formData?.year || props.editMovie.year || ""
        editForm.genre = props.formData?.genre || props.editMovie.genre
        editForm.rating = props.formData?.rating || props.editMovie.rating || ""
        editForm.status = props.formData?.status || props.editMovie.status
        editForm.notes = props.formData?.notes || props.editMovie.notes
        showEditDialog.value = true
    }
})
</script>

<template>
    <main class="container">
        <!-- Em django_inertia.md tem comentários explicando cada atributo a seguir. -->
        <StatsBar :stats="stats" />

        <button @click="openCreate">Novo filme</button>

        <MovieTable :movies="movies" @edit="openEdit" @delete="confirmDelete" />

        <MovieFormDialog
            v-model:open="showCreateDialog"
            :form="createForm"
            :errors="showCreateDialog ? errors : {}"
            title="Novo Filme"
            @submit="submitCreate"
        />

        <MovieFormDialog
            v-model:open="showEditDialog"
            :form="editForm"
            :errors="showEditDialog ? errors : {}"
            title="Editar Filme"
            @submit="submitEdit"
        />

        <ConfirmDialog
            v-model:open="showDeleteDialog"
            title="Confirmar exclusão"
            :message="`Tem certeza que deseja excluir <strong>${movieToDelete?.title}</strong>?`"
            @confirm="executeDelete"
        />
    </main>
</template>
