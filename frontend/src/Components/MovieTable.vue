<script setup>
defineProps(["movies"])
defineEmits(["edit", "delete"])
</script>

<template>
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
                        <a href="#" role="button" class="outline" @click.prevent="$emit('edit', movie)">Editar</a>
                        &nbsp;
                        <a href="#" role="button" class="outline secondary" @click.prevent="$emit('delete', movie)">Excluir</a>
                    </td>
                </tr>
            </tbody>
        </table>
    </figure>
</template>
