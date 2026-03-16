<script setup>
import { router } from "@inertiajs/vue3"

// defineProps é uma macro do Vue 3 que declara quais dados o componente espera receber.
// Quem passa esses dados é o Django — quando a view faz:
//   render(request, "Movies/Index", props={"movies": data, "stats": {...}})
// o Inertia serializa esse dict como JSON e injeta como props no componente Vue.
// É como se o Django fizesse <Index :movies="data" :stats="stats" />,
// mas quem faz essa passagem é o protocolo Inertia, não um componente pai Vue.
// Sem o defineProps, o componente não teria acesso aos dados.
const props = defineProps(["movies", "stats"])

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
function deleteMovie(id) {
    if (confirm("Tem certeza?")) {
        router.post(`/${id}/delete/`)
    }
}
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

        <a href="/create/" role="button">Novo filme</a>

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
                            <a :href="`/${movie.id}/update/`">Editar</a>
                            <a href="#" role="button" class="outline secondary" @click.prevent="deleteMovie(movie.id)">Excluir</a>
                        </td>
                    </tr>
                </tbody>
            </table>
        </figure>
    </main>
</template>
