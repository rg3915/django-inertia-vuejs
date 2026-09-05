<script setup>
import { computed, ref } from "vue"

const props = defineProps(["movies"])
defineEmits(["edit", "delete"])

// --- Busca reativa ---
// Este é o slide "Um exemplo do dia a dia": o usuário digita e a lista filtra
// na hora, sem recarregar a página e sem nenhuma ida ao servidor.
//
// Os filmes já chegaram como props do Django na primeira renderização, então
// filtrar é só uma computed sobre um array em memória. Repare no que NÃO existe
// aqui: nenhum fetch, nenhum endpoint /api/filmes/?q=..., nenhum debounce,
// nenhum estado de loading. É reatividade pura do Vue sobre dados do Django.
const search = ref("")

const filteredMovies = computed(() => {
    const term = search.value.trim().toLowerCase()

    if (!term) return props.movies

    return props.movies.filter((movie) =>
        [movie.title, movie.director, movie.genre]
            .filter(Boolean)
            .some((field) => field.toLowerCase().includes(term))
    )
})
</script>

<template>
    <!-- role="search" em vez da tag <search>: o compilador do Vue não reconhece
         <search> como elemento HTML nativo e tenta resolvê-la como componente.
         O PicoCSS estiliza [role=search] do mesmo jeito. -->
    <div class="toolbar">
        <!-- Ações da página (ex.: "Novo filme") entram aqui, ao lado da busca. -->
        <slot name="actions" />

        <div role="search">
            <input
                v-model="search"
                type="search"
                placeholder="Buscar por título, diretor ou gênero…"
                aria-label="Buscar filmes"
            >
        </div>
    </div>

    <!-- O contador também é reativo: acompanha a digitação em tempo real. -->
    <small v-if="search" class="search-count">
        {{ filteredMovies.length }} de {{ movies.length }} filme(s)
    </small>

    <figure>
        <table>
            <thead>
                <tr>
                    <th>Título</th>
                    <th>Diretor</th>
                    <th>Ano</th>
                    <th>Nota</th>
                    <th>Status</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="movie in filteredMovies" :key="movie.id">
                    <td>{{ movie.title }}</td>
                    <td>{{ movie.director }}</td>
                    <td>{{ movie.year }}</td>
                    <!-- stars e status_label vêm prontos do model Django -->
                    <td class="stars">{{ movie.stars }}</td>
                    <td>{{ movie.status_label }}</td>
                    <td>
                        <a href="#" role="button" class="outline" @click.prevent="$emit('edit', movie)">Editar</a>
                        &nbsp;
                        <a href="#" role="button" class="outline secondary" @click.prevent="$emit('delete', movie)">Excluir</a>
                    </td>
                </tr>
                <tr v-if="!filteredMovies.length">
                    <td colspan="6">
                        <em v-if="search">Nenhum filme encontrado para "{{ search }}".</em>
                        <em v-else>Nenhum filme cadastrado ainda.</em>
                    </td>
                </tr>
            </tbody>
        </table>
    </figure>
</template>

<style scoped>
.toolbar {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

/* A busca ocupa o espaço que sobra; o botão fica do tamanho do texto. */
.toolbar [role="search"] {
    flex: 1;
    margin-bottom: 0;
}

/* O conteúdo do slot vem do componente pai, daí o :slotted(). */
.toolbar :slotted(button) {
    margin-bottom: 0;
    white-space: nowrap;
}

.search-count {
    display: block;
    margin-top: -0.75rem;
    margin-bottom: 1rem;
}

.stars {
    white-space: nowrap;
    letter-spacing: 0.1em;
}
</style>
