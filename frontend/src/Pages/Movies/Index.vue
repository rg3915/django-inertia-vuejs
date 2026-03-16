<script setup>
import { ref, onMounted } from "vue"
import { router, useForm } from "@inertiajs/vue3"

// defineProps é uma macro do Vue 3 que declara quais dados o componente espera receber.
// Quem passa esses dados é o Django — quando a view faz:
//   render(request, "Movies/Index", props={"movies": data, "stats": {...}})
// o Inertia serializa esse dict como JSON e injeta como props no componente Vue.
// É como se o Django fizesse <Index :movies="data" :stats="stats" />,
// mas quem faz essa passagem é o protocolo Inertia, não um componente pai Vue.
// Sem o defineProps, o componente não teria acesso aos dados.
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
// A URL `/${id}/delete/` é uma rota definida no urls.py — não existe Vue Router.
// O Inertia intercepta a resposta (um redirect 302), busca os novos dados
// via JSON e troca o componente sem recarregar a página.
//
// Sem o Inertia, você precisaria:
// 1. Criar uma API REST no Django (Django Ninja + schema + endpoint)
// 2. Chamar essa API com axios ou fetch no Vue
// 3. Manter duas rotas: uma no urls.py e outra no Vue Router
// 4. Configurar CORS entre os dois projetos
//
// Com o Inertia, nada disso existe. O router.post() substitui o axios/fetch,
// a rota é uma só (do Django), e não há API — o Django responde direto
// para o componente Vue via protocolo Inertia.
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
        <hgroup>
            <h1>Filmes</h1>
            <p>
                Total: {{ stats.total }} |
                Quero ver: {{ stats.want }} |
                Assistindo: {{ stats.watching }} |
                Assistidos: {{ stats.watched }}
            </p>
        </hgroup>

        <button @click="openCreate">Novo filme</button>

        <figure>
            <table>
                <thead>
                    <tr>
                        <th>Titulo</th>
                        <th>Diretor</th>
                        <th>Ano</th>
                        <th>Nota</th>
                        <th>Status</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="movie in movies" :key="movie.id">
                        <td>{{ movie.title }}</td>
                        <td>{{ movie.director }}</td>
                        <td>{{ movie.year }}</td>
                        <td>{{ movie.rating }}</td>
                        <td>{{ movie.status }}</td>
                        <td>
                            <a href="#" role="button" class="outline" @click.prevent="openEdit(movie)">Editar</a>
                            &nbsp;
                            <a href="#" role="button" class="outline secondary" @click.prevent="confirmDelete(movie)">Excluir</a>
                        </td>
                    </tr>
                </tbody>
            </table>
        </figure>

        <!-- Dialog: Criar filme -->
        <dialog :open="showCreateDialog">
            <article>
                <header>
                    <button aria-label="Close" rel="prev" @click="showCreateDialog = false"></button>
                    <h3>Novo Filme</h3>
                </header>
                <form @submit.prevent="submitCreate">
                    <label>
                        Titulo
                        <input v-model="createForm.title" :aria-invalid="!!errors?.title" />
                        <small v-if="errors?.title" style="color: red">{{ errors.title[0] }}</small>
                    </label>

                    <label>
                        Diretor
                        <input v-model="createForm.director" :aria-invalid="!!errors?.director" />
                        <small v-if="errors?.director" style="color: red">{{ errors.director[0] }}</small>
                    </label>

                    <div class="grid">
                        <label>
                            Ano
                            <input v-model="createForm.year" type="number" min="0" :aria-invalid="!!errors?.year" />
                            <small v-if="errors?.year" style="color: red">{{ errors.year[0] }}</small>
                        </label>
                        <label>
                            Genero
                            <input v-model="createForm.genre" :aria-invalid="!!errors?.genre" />
                            <small v-if="errors?.genre" style="color: red">{{ errors.genre[0] }}</small>
                        </label>
                    </div>

                    <div class="grid">
                        <label>
                            Nota (0-10)
                            <input v-model="createForm.rating" type="number" min="0" max="10" :aria-invalid="!!errors?.rating" />
                            <small v-if="errors?.rating" style="color: red">{{ errors.rating[0] }}</small>
                        </label>
                        <label>
                            Status
                            <select v-model="createForm.status" :aria-invalid="!!errors?.status">
                                <option value="want">Quero Ver</option>
                                <option value="watching">Assistindo</option>
                                <option value="watched">Assistido</option>
                            </select>
                            <small v-if="errors?.status" style="color: red">{{ errors.status[0] }}</small>
                        </label>
                    </div>

                    <label>
                        Notas
                        <textarea v-model="createForm.notes" :aria-invalid="!!errors?.notes"></textarea>
                        <small v-if="errors?.notes" style="color: red">{{ errors.notes[0] }}</small>
                    </label>

                    <footer>
                        <div class="grid">
                            <button type="button" class="outline secondary" @click="showCreateDialog = false">Cancelar</button>
                            <button type="submit" :disabled="createForm.processing" :aria-busy="createForm.processing">Salvar</button>
                        </div>
                    </footer>
                </form>
            </article>
        </dialog>

        <!-- Dialog: Editar filme -->
        <dialog :open="showEditDialog">
            <article>
                <header>
                    <button aria-label="Close" rel="prev" @click="showEditDialog = false"></button>
                    <h3>Editar Filme</h3>
                </header>
                <form @submit.prevent="submitEdit">
                    <label>
                        Titulo
                        <input v-model="editForm.title" :aria-invalid="!!errors?.title" />
                        <small v-if="errors?.title && showEditDialog" style="color: red">{{ errors.title[0] }}</small>
                    </label>

                    <label>
                        Diretor
                        <input v-model="editForm.director" :aria-invalid="!!errors?.director" />
                        <small v-if="errors?.director && showEditDialog" style="color: red">{{ errors.director[0] }}</small>
                    </label>

                    <div class="grid">
                        <label>
                            Ano
                            <input v-model="editForm.year" type="number" min="0" :aria-invalid="!!errors?.year" />
                            <small v-if="errors?.year && showEditDialog" style="color: red">{{ errors.year[0] }}</small>
                        </label>
                        <label>
                            Genero
                            <input v-model="editForm.genre" :aria-invalid="!!errors?.genre" />
                            <small v-if="errors?.genre && showEditDialog" style="color: red">{{ errors.genre[0] }}</small>
                        </label>
                    </div>

                    <div class="grid">
                        <label>
                            Nota (0-10)
                            <input v-model="editForm.rating" type="number" min="0" max="10" :aria-invalid="!!errors?.rating" />
                            <small v-if="errors?.rating && showEditDialog" style="color: red">{{ errors.rating[0] }}</small>
                        </label>
                        <label>
                            Status
                            <select v-model="editForm.status" :aria-invalid="!!errors?.status">
                                <option value="want">Quero Ver</option>
                                <option value="watching">Assistindo</option>
                                <option value="watched">Assistido</option>
                            </select>
                            <small v-if="errors?.status && showEditDialog" style="color: red">{{ errors.status[0] }}</small>
                        </label>
                    </div>

                    <label>
                        Notas
                        <textarea v-model="editForm.notes" :aria-invalid="!!errors?.notes"></textarea>
                        <small v-if="errors?.notes && showEditDialog" style="color: red">{{ errors.notes[0] }}</small>
                    </label>

                    <footer>
                        <div class="grid">
                            <button type="button" class="outline secondary" @click="showEditDialog = false">Cancelar</button>
                            <button type="submit" :disabled="editForm.processing" :aria-busy="editForm.processing">Salvar</button>
                        </div>
                    </footer>
                </form>
            </article>
        </dialog>

        <!-- Dialog: Confirmar exclusão -->
        <dialog :open="showDeleteDialog">
            <article>
                <header>
                    <button aria-label="Close" rel="prev" @click="showDeleteDialog = false"></button>
                    <h3>Confirmar exclusão</h3>
                </header>
                <p>Tem certeza que deseja excluir <strong>{{ movieToDelete?.title }}</strong>?</p>
                <footer>
                    <div class="grid">
                        <button class="outline secondary" @click="showDeleteDialog = false">Cancelar</button>
                        <button class="contrast" @click="executeDelete">Excluir</button>
                    </div>
                </footer>
            </article>
        </dialog>
    </main>
</template>
