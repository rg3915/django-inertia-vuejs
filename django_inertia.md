# Django + Inertia.js + Vue 3 — Guia Completo

> Stack: Django · inertia-django · Vue 3 · Vite · PostgreSQL · Docker · uv

---

## O que é o Inertia.js

O Inertia.js é descrito como **"The Modern Monolith"** — uma camada de protocolo que permite construir SPAs com a experiência de componentes Vue (ou React/Svelte) sem abrir mão da arquitetura server-side do Django.

Ele não é um framework completo. É uma **cola** entre o backend e o frontend: intercepta as navegações do browser, substitui apenas o componente renderizado, e injeta os dados (props) diretamente do Django — sem construir uma API REST separada.

---

## Por que o Inertia existe

O Inertia foi criado para resolver um problema específico: o **monólito que quer virar SPA**.

Frameworks como Django, Laravel e Rails nascem com:
- Sistema de templates (renderização server-side)
- Roteamento server-side
- Sessões, middleware e autenticação prontos

O Inertia **substitui o template engine**: em vez de renderizar HTML, o Django renderiza um componente Vue com props injetados. Toda a infraestrutura — rotas, sessão, permissões, middleware — continua sendo do Django.

```mermaid
graph TD
    A["Você quer Vue no frontend"] --> B{"O backend renderiza HTML?"}

    B -->|SIM - Django, Laravel, Rails| C{"Quer SPA sem construir API?"}
    C -->|SIM| D["✅ Inertia.js"]
    C -->|NÃO| E["Templates + HTMX / Alpine.js"]

    B -->|NÃO - FastAPI, Node, Go| F["Vue standalone\n+ Vue Router + Pinia"]

    D --> G["Sem API, sem Vue Router,\nsem Pinia, sem CORS"]
    F --> H["API obrigatória,\nVue Router, Pinia, CORS"]

    style D fill:#10b981,color:#fff
    style F fill:#3b82f6,color:#fff
    style E fill:#f59e0b,color:#fff
```

### Se fosse FastAPI — o Inertia não se aplica

O FastAPI nasce como API pura. Não tem template engine, não tem roteamento server-side de páginas, não tem sessão nativa. O Inertia pressupõe todas essas coisas.

Com FastAPI, a arquitetura é obrigatoriamente:
- Backend: JSON puro, sempre
- Frontend: Vue standalone, totalmente independente
- Vue Router, Pinia e uma camada `api/` são sua responsabilidade
- CORS é obrigatório configurar

> O Inertia elimina a necessidade de construir uma API quando você **não precisa** de uma API. Se você escolheu o FastAPI, você escolheu ter uma API — e o Inertia não tem papel nenhum nisso.

---

## O problema que o Inertia resolve

Sem o Inertia, usar Vue com Django implica uma de duas abordagens ruins:

### Sem Inertia — Django Ninja + Vue SPA separado

Dois projetos independentes. O Vue faz fetch/axios para uma API REST, precisa de Vue Router, Pinia, CORS, e autenticação duplicada.

```mermaid
graph TD
    USER["Navegador"]

    subgraph FRONTEND ["Frontend — projeto separado"]
        direction TB
        VUE["Vue 3 + Vue Router + Pinia"]
        AXIOS["axios / fetch"]
    end

    subgraph BACKEND ["Backend — projeto separado"]
        direction TB
        NINJA["Django Ninja\nAPI REST + Schemas"]
        DJ["Django"]
    end

    USER --> VUE
    VUE --> AXIOS
    AXIOS -- "HTTP JSON + CORS + JWT" --> NINJA
    NINJA --> DJ

    style FRONTEND fill:#3b82f6,color:#fff
    style BACKEND fill:#10b981,color:#fff
```

**Problemas:**
- Autenticação duplicada (sessão no Django + JWT no Vue)
- CORS entre dois projetos
- Schemas no Django Ninja *e* tipos no TypeScript para manter sincronizados
- Roteamento dividido: `urls.py` no Django e Vue Router no frontend
- Dois deploys, dois servidores
- O sistema de permissões do Django não funciona nativamente no frontend

### Com Inertia — um projeto só

O Django renderiza componentes Vue diretamente, passando dados como props. Sem API, sem axios, sem Vue Router, sem CORS.

```mermaid
graph LR
    subgraph MONOLITO ["Projeto único"]
        DJ["Django\nurls.py + views"]
        INERTIA["Inertia\nprotocolo"]
        VUE["Vue 3\ncomponentes\n+ defineProps"]
        DJ -- "props" --> INERTIA
        INERTIA -- "componente + dados" --> VUE
    end

    USER["Navegador"] --> DJ

    style MONOLITO fill:#10b981,color:#fff
```

Sem Vue Router. Sem Pinia. Sem axios/fetch. Sem CORS. Sem JWT. Um projeto, um deploy.

### Abordagem 2 — Templates Django + Vue como "ilhas"

Vue é injetado pontualmente em templates HTML. Cada navegação faz um full page reload. A experiência SPA se perde.

---

## Como o Inertia resolve

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant I as Inertia Client
    participant D as Django view
    participant DB as Banco

    rect rgb(209, 250, 229)
        note over B,DB: Primeira visita — full page load
        B->>D: GET /movies/ (sem header X-Inertia)
        D->>DB: Movie.objects.all()
        DB-->>D: queryset
        D-->>B: HTML completo + dados embutidos no div#app
        B->>I: Inertia inicializa, lê dados do div#app
        I-->>B: Renderiza Movies/Index.vue com os props
    end

    rect rgb(238, 237, 254)
        note over B,DB: Navegação SPA — sem reload
        B->>I: Usuário clica em link
        I->>D: GET /create/ (header: X-Inertia: true)
        D-->>I: JSON com componente e props
        I-->>B: Troca só o componente Vue
    end

    rect rgb(254, 243, 199)
        note over B,DB: Submit de formulário
        B->>I: Usuário submete form
        I->>D: POST /store/ (JSON + XSRF-TOKEN)
        D->>DB: Movie.objects.create(...)
        DB-->>D: ok
        D-->>I: redirect 302
        I->>D: GET / (X-Inertia: true)
        D-->>I: JSON com Movies/Index + props frescos
        I-->>B: Atualiza a lista sem recarregar
    end
```

O diagrama mostra três momentos distintos:

**1. Primeira visita (full page load)** — O navegador faz um GET normal para `/movies/`, sem nenhum header especial. O Django consulta o banco (`Movie.objects.all()`), monta um HTML completo com os dados já embutidos dentro de um `div#app`, e devolve tudo para o navegador. O Inertia Client (JavaScript) inicializa, lê esses dados do `div#app` e renderiza o componente `Movies/Index.vue` com os props. Essa primeira resposta é HTML de verdade — bom para SEO e performance inicial.

**2. Navegação SPA (sem reload)** — Quando o usuário clica em um link (ex: "Novo filme"), o Inertia intercepta o clique e faz um GET para `/create/` com o header `X-Inertia: true`. O Django reconhece esse header e, em vez de devolver HTML completo, responde apenas com um JSON contendo o nome do componente (`Movies/Create`) e os props. O Inertia Client recebe esse JSON e troca apenas o componente Vue na tela — sem recarregar a página, sem piscar, sem perder estado.

**3. Submit de formulário** — O usuário preenche e submete o form. O Inertia envia um POST para `/create/` com os dados + XSRF-TOKEN. O Django valida, salva no banco e responde com um redirect 302. O Inertia intercepta esse redirect, faz automaticamente um novo GET (com `X-Inertia: true`), recebe o JSON com os dados atualizados, e atualiza a lista na tela — tudo sem reload.

Em resumo: na primeira visita, HTML completo; depois, só JSON. O navegador nunca recarrega. O Django trabalha como sempre (views, redirect, sessão); o Inertia cuida da experiência SPA no meio.

---

## Estrutura do projeto

```
movies/
├── docker-compose.yml          # Dev: PostgreSQL + pgAdmin
├── docker-compose.prod.yml     # Prod: Nginx + Django + PostgreSQL
├── Dockerfile                  # Multi-stage: Node (build) + Python (run)
├── nginx.conf
├── .env
├── manage.py
├── pyproject.toml
├── templates/
│   └── base.html
├── apps/
│   ├── settings.py
│   ├── urls.py
│   └── core/
│       ├── models.py
│       ├── forms.py
│       ├── views.py
│       └── urls.py
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        └── Pages/
            └── Movies/
                ├── Index.vue
                ├── Create.vue
                └── Edit.vue
```

---

## Infraestrutura — o que roda onde

O Docker cuida **apenas** do banco e do pgAdmin. Django e Vue/Vite rodam **localmente** — são o mesmo monólito e precisam se enxergar diretamente durante o desenvolvimento.

```mermaid
graph TB
    subgraph DOCKER ["Docker — docker-compose.yml"]
        PGA["pgAdmin\nporta 5050"]
        DB["PostgreSQL\nporta 5431"]
        PGA -->|conecta| DB
    end

    USER["Usuário :8000"] --> DJ
    DJ["Django\nuv run python manage.py runserver\nporta 8000"] -.->|lê assets via| VITE["Vite + Vue 3\nnpm run dev + HMR\nporta 5173"]
    DJ -->|DATABASE_URL| DB
```

### docker-compose.yml

```yaml
services:
  db:
    image: postgres:18.3-alpine
    restart: unless-stopped
    env_file: .env
    ports:
      - "5431:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - movies-network

  pgadmin:
    image: dpage/pgadmin4
    restart: unless-stopped
    env_file: .env
    ports:
      - "5050:80"
    depends_on:
      - db
    networks:
      - movies-network

volumes:
  pgdata:

networks:
  movies-network:
```

### Como rodar em desenvolvimento

```bash
# 1. Sobe o banco e o pgAdmin
docker compose up -d

# 2. Em um terminal — Django
uv sync
uv run python manage.py migrate
uv run python manage.py runserver

# 3. Em outro terminal — Vite (frontend)
cd frontend
npm install
npm run dev
```

O Vite roda localmente porque o Django precisa ler os assets dele em tempo real (HMR). Colocar o Vite dentro do Docker adicionaria complexidade sem benefício — ambos são parte do mesmo monólito e rodam na mesma máquina durante o desenvolvimento.

> Para a configuração de infraestrutura de produção (Dockerfile, Nginx, docker-compose.prod.yml), veja a seção [Produção](#produção) no final do documento.

---

## Tutorial — do zero ao CRUD funcionando

### Passo 1 — Docker (banco + pgAdmin)

Crie a pasta do projeto e os arquivos de infraestrutura:

```bash
mkdir django-inertia-vuejs  # caso a pasta ainda não exista
cd django-inertia-vuejs  # caso já não esteja dentro da pasta
```

Crie o `.env` e gere uma `SECRET_KEY`:

```bash
cat <<'EOF' > .env
SECRET_KEY=mude-me

POSTGRES_DB=movies_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5431

PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin

DATABASE_URL=postgres://postgres:postgres@localhost:5431/movies_db
EOF
```

Para gerar a `SECRET_KEY`, rode:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Cole o valor gerado na variável `SECRET_KEY` do `.env`.

Crie o `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:18.3-alpine
    restart: unless-stopped
    env_file: .env
    ports:
      - "5431:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - movies-network

  pgadmin:
    image: dpage/pgadmin4
    restart: unless-stopped
    env_file: .env
    ports:
      - "5050:80"
    depends_on:
      - db
    networks:
      - movies-network

volumes:
  pgdata:

networks:
  movies-network:
```

```bash
docker compose up -d
```

### Passo 2 — Django

```bash
uv init --bare
uv add django inertia-django django-vite django-extensions psycopg2-binary python-decouple
uv add --dev ruff

uv run django-admin startproject apps .
mkdir apps/core
uv run python manage.py startapp core apps/core
```

Edite `apps/core/apps.py` para que o Django reconheça a app como subpasta:

```python
from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = "apps.core"
```

Edite `apps/settings.py`:

```python
from decouple import config

SECRET_KEY = config("SECRET_KEY")

INSTALLED_APPS = [
    # ... apps padrão ...
    "django_extensions",
    "django_vite",
    "inertia",
    "apps.core",
]

MIDDLEWARE = [
    # ... middleware padrão ...
    "inertia.middleware.InertiaMiddleware",  # adicionar após SessionMiddleware
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": "localhost",
        "PORT": config("POSTGRES_PORT", default="5431"),
    }
}

TEMPLATES = [
    {
        # ...
        "DIRS": [BASE_DIR.joinpath("templates")],
        # ...
    },
]

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

# CSRF — o Inertia.js (axios) lê o cookie XSRF-TOKEN automaticamente
CSRF_COOKIE_NAME = "XSRF-TOKEN"
CSRF_HEADER_NAME = "HTTP_X_XSRF_TOKEN"

# Inertia
INERTIA_LAYOUT = "base.html"

# Django Vite
DJANGO_VITE = {
    "default": {
        "dev_mode": True,
        "dev_server_host": "localhost",
        "dev_server_port": 5173,
        "manifest_path": BASE_DIR.joinpath("frontend", "dist", ".vite", "manifest.json"),
    }
}

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR.joinpath("frontend", "dist"),
]
```

Crie `templates/base.html`:

```html
{% load django_vite %}
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movies</title>
    {% vite_hmr_client %}
    {% vite_asset 'src/main.js' %}
</head>
<body>
    {% block inertia %}{% endblock %}
</body>
</html>
```

### Passo 3 — Model

```python
# apps/core/models.py
from django.db import models

class Movie(models.Model):
    class Status(models.TextChoices):
        WANT = "want", "Quero Ver"
        WATCHING = "watching", "Assistindo"
        WATCHED = "watched", "Assistido"
    title    = models.CharField(max_length=200)
    director = models.CharField(max_length=200, blank=True)
    year     = models.PositiveIntegerField(null=True, blank=True)
    genre    = models.CharField(max_length=100, blank=True)
    rating   = models.PositiveSmallIntegerField(null=True, blank=True)
    status   = models.CharField(max_length=10, choices=Status.choices, default=Status.WANT)
    notes    = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Filme"
        verbose_name_plural = "Filmes"

    def __str__(self):
        return self.title

    def serializable_values(self, exclude=[]):
        tree = {}
        for field in self._meta.fields:
            if field.name in exclude:
                continue
            tree[field.name] = self.serializable_value(field.name)
        return tree
```

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Passo 4 — Form

```python
# apps/core/forms.py
from django import forms

from .models import Movie


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ("title", "director", "year", "genre", "rating", "status", "notes")
```

### Passo 5 — Views

O `inertia-django` oferece 3 formas de retornar respostas Inertia:

**1. Função `render()`** — a mais explícita, semelhante ao `render` do Django:

```python
from inertia import render

def movie_list(request):
    return render(request, "Movies/Index", props={"movies": data})
```

**2. Decorator `@inertia()`** — a view retorna apenas o dict de props:

```python
from inertia import inertia

@inertia("Movies/Index")
def movie_list(request):
    return {"movies": data}
```

**3. Classe `InertiaResponse`** — para controle máximo:

```python
from inertia import InertiaResponse

def movie_list(request):
    return InertiaResponse(request, "Movies/Index", props={"movies": data})
```

As três fazem a mesma coisa: na primeira visita, retornam HTML completo com os dados embutidos no `div#app`; nas navegações seguintes (com header `X-Inertia: true`), retornam apenas JSON com o nome do componente e os props.

Neste tutorial usamos a **função `render()`** por ser a mais familiar para quem vem do Django.

> **Atenção: Inertia v2 envia JSON, não form-urlencoded**
>
> O `useForm.post()` do Inertia v2 envia os dados com `Content-Type: application/json`. O `request.POST` do Django só lê `application/x-www-form-urlencoded` ou `multipart/form-data` — com JSON, ele fica vazio.
>
> Por isso criamos o helper `_get_post_data()` que detecta o content type e faz o parse do `request.body` quando necessário.

```python
# apps/core/views.py
import json

from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect
from inertia import render

from .forms import MovieForm
from .models import Movie


def _get_post_data(request):
    """O Inertia v2 envia JSON, mas o Django ModelForm espera QueryDict."""
    if request.content_type == "application/json":
        return QueryDict(mutable=True) | json.loads(request.body)
    return request.POST


def movie_list(request):
    movies = Movie.objects.all()
    data = [movie.serializable_values(exclude=["added_at"]) for movie in movies]
    return render(
        request,
        "Movies/Index",
        props={
            "movies": data,
            "stats": {
                "total": movies.count(),
                "want": movies.filter(status="want").count(),
                "watching": movies.filter(status="watching").count(),
                "watched": movies.filter(status="watched").count(),
            },
        },
    )


def movie_create(request):
    data = _get_post_data(request) if request.method == "POST" else None
    form = MovieForm(data)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("movie_list")

    return render(request, "Movies/Create", props={"errors": form.errors})


def movie_update(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    data = _get_post_data(request) if request.method == "POST" else None
    form = MovieForm(data, instance=movie)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("movie_list")

    data = movie.serializable_values(exclude=["added_at"])
    return render(
        request,
        "Movies/Edit",
        props={
            "movie": data,
            "errors": form.errors,
        },
    )


def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    return redirect("movie_list")
```

### Passo 6 — URLs

```python
# apps/core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("",                 views.movie_list,   name="movie_list"),
    path("create/",          views.movie_create,  name="movie_create"),
    path("<int:pk>/update/",   views.movie_update,  name="movie_update"),
    path("<int:pk>/delete/", views.movie_delete,  name="movie_delete"),
]
```

```python
# apps/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
]
```

### Passo 7 — Frontend (Vue + Vite + Inertia)

```bash
mkdir frontend && cd frontend
npm init -y
npm install vue @inertiajs/vue3 @vitejs/plugin-vue
npm install -D vite
```

Crie `frontend/vite.config.js`:

```js
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
```

Crie `frontend/src/main.js`:

```js
import { createApp, h } from "vue"
import { createInertiaApp } from "@inertiajs/vue3"

createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob("./Pages/**/*.vue", { eager: true })
        return pages[`./Pages/${name}.vue`]
    },
    setup({ el, App, props, plugin }) {
        createApp({ render: () => h(App, props) })
            .use(plugin)
            .mount(el)
    },
})
```

Crie `frontend/src/Pages/Movies/Index.vue`.

```vue
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
    <div>
        <h1>Filmes ({{ stats.total }})</h1>

        <p>
            Quero ver: {{ stats.want }} |
            Assistindo: {{ stats.watching }} |
            Assistidos: {{ stats.watched }}
        </p>

        <a href="/create/">Novo filme</a>

        <table>
            <thead>
                <tr>
                    <th>Titulo</th>
                    <th>Diretor</th>
                    <th>Ano</th>
                    <th>Status</th>
                    <th>Acoes</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="movie in movies" :key="movie.id">
                    <td>{{ movie.title }}</td>
                    <td>{{ movie.director }}</td>
                    <td>{{ movie.year }}</td>
                    <td>{{ movie.status }}</td>
                    <td>
                        <a :href="`/${movie.id}/update/`">Editar</a>
                        <button @click="deleteMovie(movie.id)">Excluir</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
```

Crie `frontend/src/Pages/Movies/Create.vue`:

```vue
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
```

Crie `frontend/src/Pages/Movies/Edit.vue`:

```vue
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
```

### Passo 8 — Rodar

```bash
# Terminal 1 — banco (se ainda não subiu)
docker compose up -d

# Terminal 2 — Django
uv run python manage.py runserver

# Terminal 3 — Vite
cd frontend
npm run dev
```

Acesse `http://localhost:8000` — o CRUD de filmes estará funcionando com navegação SPA.

Para visualizar todas as rotas registradas no projeto, use o `show_urls` do django-extensions:

```bash
uv run python manage.py show_urls
```

```
/                 apps.core.views.movie_list    movie_list
/create/          apps.core.views.movie_create  movie_create
/<pk>/update/     apps.core.views.movie_update  movie_update
/<pk>/delete/     apps.core.views.movie_delete  movie_delete
/admin/           django.contrib.admin.sites.AdminSite.index  admin:index
...
```

Útil para confirmar que as URLs estão corretas sem precisar abrir o navegador.

---

## Validação

No Inertia, a validação segue o fluxo natural do Django — sem API, sem status 422, sem tratamento especial no frontend.

### Como funciona

1. O usuário submete o formulário via `form.post("/create/")`
2. O Inertia envia um POST para a rota do Django
3. O Django valida com `ModelForm` — se falhar, **não redireciona**, renderiza a mesma página com `form.errors` nos props
4. O Inertia recebe os props atualizados e o Vue re-renderiza o componente com os erros

### No Django (view)

Os erros do `ModelForm` são passados como prop `errors`. No GET inicial é um dict vazio `{}`; no POST com erro, vem preenchido:

```python
def movie_create(request):
    data = _get_post_data(request) if request.method == "POST" else None
    form = MovieForm(data)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("movie_list")

    # form.errors é {} no GET, ou {"title": ["Este campo é obrigatório."]} no POST inválido
    return render(request, "Movies/Create", props={"errors": form.errors})
```

### No Vue (componente)

```vue
<script setup>
// errors vem do Django como prop — sem fetch, sem try/catch, sem axios
const props = defineProps(["errors"])
</script>

<template>
    <div>
        <label>Titulo</label>
        <input v-model="form.title" />
        <span v-if="errors.title" style="color: red">{{ errors.title[0] }}</span>
    </div>
</template>
```

O `errors.title` é um array porque o Django pode retornar múltiplos erros por campo. Usamos `[0]` para exibir apenas o primeiro.

### O que você não precisa fazer

- Nenhum `try/catch` no frontend
- Nenhum `axios.post().catch(err => ...)` para capturar status 422
- Nenhum estado local para armazenar erros (`ref`, `reactive`)
- Nenhum endpoint de API separado para validação

Os erros vêm como props do Django, no mesmo fluxo de renderização do Inertia. O Vue só precisa declarar `defineProps(["errors"])` e exibir.

---

## HTMX e Alpine.js — outro assunto

O Inertia, HTMX e Alpine.js não são concorrentes diretos. Cada um ocupa um nível diferente de complexidade:

```
Templates Django puros
        │
        ├── Alpine.js
        │     Reatividade local no HTML
        │     Menus, modais, toggles
        │     Sem requisições, sem roteamento
        │
        ├── HTMX
        │     Requisições AJAX sem escrever JS
        │     O servidor responde com HTML, não JSON
        │     Ideal para apps conteúdo-heavy
        │
        └── Inertia + Vue
              SPA completo com componentes ricos
              O servidor responde com JSON + nome do componente
              Ideal para UIs complexas e interativas
```

HTMX e Alpine.js são frequentemente usados **juntos** como alternativa ao Inertia — o chamado "Django + HTMX + Alpine" ou "The Boring Stack". Você tem experiência próxima de SPA sem sair dos templates Django e sem escrever quase nenhum JavaScript.

| | HTMX | Alpine.js | Inertia + Vue |
|---|---|---|---|
| Templates Django | Continua usando | Continua usando | Substitui por componentes |
| JavaScript de estado | Quase nenhum | Mínimo, local | Completo, global |
| Componentes reutilizáveis | Parciais HTML | Limitado | Componentes Vue ricos |
| Curva de aprendizado | Baixa | Baixa | Média |
| Ideal para | Apps conteúdo-heavy | Interações pontuais | Apps interativos complexos |

---

## Tabelas comparativas

### Com Inertia vs sem Inertia (Django Ninja + Vue separado)

| | Com Inertia | Sem Inertia (Django Ninja + Vue) |
|---|---|---|
| API REST | Não necessária | Obrigatória |
| Schemas | Não necessários | Obrigatórios |
| CORS | Não necessário | Obrigatório configurar |
| Autenticação | 100% no Django (sessão) | Duplicada (sessão + JWT) |
| Vue Router | Não existe | Obrigatório |
| Pinia / Vuex | Não necessário | Necessário para estado global |
| Roteamento | Só no `urls.py` | `urls.py` + Vue Router |
| Fetch / Axios manual | Não existe | Necessário em todo endpoint |
| Dados no componente | Props injetados pelo Django | Buscados via fetch no `onMounted` |
| Projetos em paralelo | 1 projeto | 2 projetos |
| Deploy | 1 servidor | 2 servidores ou proxy |
| Docs de API (Swagger) | Não gera | Automático (`/api/docs`) |

### Quando cada abordagem faz mais sentido

| Cenário | Melhor escolha |
|---|---|
| App web só para o próprio frontend | Inertia |
| App que será consumido por mobile também | Django Ninja + Vue separado |
| Equipe domina Django, pouco Vue/React | HTMX + Alpine |
| UI muito complexa, muito estado global | Inertia ou Django Ninja + Vue |
| API pública para terceiros | Django Ninja + Vue (ou FastAPI + Vue) |
| Startup querendo velocidade de desenvolvimento | Inertia |
| Microsserviços, múltiplos frontends | API pura (FastAPI ou Django Ninja) |

### Django + Inertia vs FastAPI + Vue

| | Django + Inertia | FastAPI + Vue |
|---|---|---|
| Usa Inertia | Sim | **Não — incompatível** |
| Resposta do backend | HTML (1ª visita) ou JSON | Sempre JSON |
| Vue Router | Não necessário | Obrigatório |
| Pinia | Não necessário | Obrigatório |
| CORS | Não necessário | Obrigatório |
| Docs de API automáticas | Não | Sim (`/docs` com Swagger) |
| Performance I/O | Boa | Excelente (async nativo) |
| Admin panel | Django Admin pronto | Não existe nativamente |
| Migrations | Django ORM + Alembic opcional | Alembic obrigatório |
| Ideal para | Monólito web com UI rica | API pública, microsserviços |

---

## Vantagens do Django + Inertia

### 1. Sem duplicação de lógica
Você escreve a lógica uma vez no Django e passa os dados diretamente como props para o Vue. Nada de serializers extras, nada de endpoints REST para navegação de páginas.

### 2. Autenticação 100% no Django
Login, sessões, permissões, middleware — tudo continua funcionando no backend como sempre. O Inertia Django lida automaticamente com o CSRF token em cada resposta. Nada de JWT, nada de refresh token no frontend.

### 3. Roteamento unificado
As URLs vivem no `urls.py` do Django. O Vue Router simplesmente não existe nessa arquitetura.

### 4. Experiência SPA real
O usuário tem navegação instantânea, sem piscar de página, com barra de progresso, tudo que se espera de uma SPA moderna — mas o servidor é um monólito Django convencional.

### 5. Partial reloads
Quando só uma parte da página muda, o Inertia busca apenas os props necessários, não a página inteira.

### 6. Shared data global
Dados como usuário logado e notificações são compartilhados entre todas as páginas sem repetir lógica — via `share()` no Django.

### 7. Um projeto, um deploy
Sem CORS, sem dois repositórios, sem sincronizar versões de API entre frontend e backend.

---

## Conclusão

O Inertia.js é a resposta certa para uma pergunta específica: **"Como ter uma SPA moderna sem abrir mão do meu monólito Django?"**

Ele não é a ferramenta certa para todo projeto. Se você precisa de uma API pública, se o seu time é de uma API que múltiplos clientes consomem, ou se você escolheu o FastAPI, o Inertia não se aplica — e nem deveria.

Mas para o caso mais comum — uma equipe Django construindo uma aplicação web com UI interativa para usuários próprios — o Inertia elimina uma camada inteira de complexidade que geralmente não agrega valor ao negócio: a API "pra meu próprio frontend".

A pergunta que o Inertia te força a fazer antes de construir qualquer endpoint é: **"Quem vai consumir isso além do meu próprio frontend?"** Se a resposta for ninguém, você provavelmente não precisa de uma API.

---

## Produção

Em produção o Vite **não existe**. O frontend vira um conjunto de arquivos estáticos (JS, CSS) que o Django serve diretamente. Tudo roda dentro do Docker.

```mermaid
graph TD
    USER["Usuário\n:80"]

    subgraph DOCKER ["Produção — docker-compose.prod.yml"]
        NGINX["Nginx\nreverse proxy\nporta 80"]
        DJ["Django\ngunicorn\nporta 8000\n+ whitenoise"]
        DB["PostgreSQL\nsem porta exposta"]

        NGINX -->|proxy_pass :8000| DJ
        DJ -->|DATABASE_URL| DB
    end

    USER --> NGINX
```

O `npm run build` acontece no **build da imagem** (multi-stage Dockerfile), e os arquivos estáticos ficam embutidos no container do Django. A imagem final não contém Node.

### Dockerfile

```dockerfile
# --- Estágio 1: build do frontend ---
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Estágio 2: Django ---
FROM python:3.12-slim
WORKDIR /app

# Instala uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Instala dependências Python
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copia o projeto
COPY . .

# Copia os assets buildados do estágio 1
COPY --from=frontend /app/frontend/dist /app/frontend/dist

# Coleta arquivos estáticos
RUN uv run python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["uv", "run", "gunicorn", "apps.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### nginx.conf

```nginx
server {
    listen 80;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### docker-compose.prod.yml

```yaml
services:
  web:
    build: .
    env_file: .env
    depends_on:
      - db
    expose:
      - "8000"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web

  db:
    image: postgres:18.3-alpine
    env_file: .env
    volumes:
      - pgdata_prod:/var/lib/postgresql/data

volumes:
  pgdata_prod:
```

### Como subir

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Dev vs Produção

| | Desenvolvimento | Produção |
|---|---|---|
| Django | `runserver` | `gunicorn` com N workers |
| Frontend | Vite rodando com HMR (porta 5173) | Não existe — arquivos estáticos |
| Node.js | Necessário | Não necessário |
| Como o JS chega | Vite serve em tempo real | Django serve via `whitenoise` |
| Banco | Docker local, porta 5431 exposta | Docker sem porta exposta |
| pgAdmin | Docker local, porta 5050 | Não necessário |
| Build do frontend | Não necessário | `npm run build` no Dockerfile |