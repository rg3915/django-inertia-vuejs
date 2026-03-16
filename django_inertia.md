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
│       ├── urls.py
│       └── middleware.py
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── composables/
        │   └── useModal.js
        ├── Components/
        │   ├── ConfirmDialog.vue
        │   ├── MovieFormDialog.vue
        │   ├── MovieTable.vue
        │   ├── StatsBar.vue
        │   └── Toast.vue
        └── Pages/
            └── Movies/
                └── Index.vue
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
    "apps.core.middleware.InertiaFlashMiddleware",
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

Todo o CRUD acontece em uma única página (`Movies/Index`). As views de criação e edição, em caso de erro de validação, re-renderizam `Movies/Index` com props extras (`errors`, `showDialog`, `formData`) para que o dialog reabra com os erros exibidos.

Crie `apps/core/middleware.py` — middleware que compartilha flash messages do Django como prop do Inertia:

```python
# apps/core/middleware.py
from django.contrib import messages
from inertia import share


class InertiaFlashMiddleware:
    """Compartilha flash messages do Django como prop 'flash' do Inertia.

    O django.contrib.messages armazena mensagens na sessão.
    Este middleware lê as mensagens ANTES da view executar
    (elas foram setadas na request anterior, ex: messages.success no POST)
    e as compartilha via share() para que estejam disponíveis como prop.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lê as mensagens da sessão ANTES da view executar.
        # As mensagens foram criadas na request anterior (ex: POST que fez redirect).
        flash = [
            {"message": str(m), "tags": m.tags}
            for m in messages.get_messages(request)
        ]

        if flash:
            share(request, flash=flash)

        return self.get_response(request)
```

```python
# apps/core/views.py
import json

from django.contrib import messages
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


def _index_props():
    """Props comuns para a página Index."""
    movies = Movie.objects.all()
    data = [movie.serializable_values(exclude=["added_at"]) for movie in movies]
    return {
        "movies": data,
        "stats": {
            "total": movies.count(),
            "want": movies.filter(status="want").count(),
            "watching": movies.filter(status="watching").count(),
            "watched": movies.filter(status="watched").count(),
        },
    }


def movie_list(request):
    return render(request, "Movies/Index", props=_index_props())


def movie_create(request):
    data = _get_post_data(request)
    form = MovieForm(data)

    if form.is_valid():
        form.save()
        messages.success(request, "Filme criado com sucesso!")
        return redirect("movie_list")

    props = _index_props()
    props["errors"] = form.errors
    props["showDialog"] = "create"
    props["formData"] = dict(data)
    return render(request, "Movies/Index", props=props)


def movie_update(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    data = _get_post_data(request)
    form = MovieForm(data, instance=movie)

    if form.is_valid():
        form.save()
        messages.success(request, "Filme atualizado com sucesso!")
        return redirect("movie_list")

    props = _index_props()
    props["errors"] = form.errors
    props["showDialog"] = "edit"
    props["editMovie"] = movie.serializable_values(exclude=["added_at"])
    props["formData"] = dict(data)
    return render(request, "Movies/Index", props=props)


def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    messages.success(request, "Filme excluído com sucesso!")
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
npm install vue @inertiajs/vue3 @vitejs/plugin-vue @picocss/pico
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
import "@picocss/pico"
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

Antes de criar a página principal, crie os componentes reutilizáveis.

Crie `frontend/src/Components/StatsBar.vue` — barra de estatísticas:

```vue
<script setup>
defineProps(["stats"])
</script>

<template>
    <hgroup>
        <h1>Filmes</h1>
        <p>
            Total: {{ stats.total }} |
            Quero ver: {{ stats.want }} |
            Assistindo: {{ stats.watching }} |
            Assistidos: {{ stats.watched }}
        </p>
    </hgroup>
</template>
```

Crie `frontend/src/Components/MovieTable.vue` — tabela de filmes que emite eventos para editar e excluir:

```vue
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
```

Crie `frontend/src/Components/MovieFormDialog.vue` — dialog reutilizável para criar e editar filmes:

```vue
<script setup>
import { ref, watch } from "vue"
import { useModal } from "../composables/useModal"

// Recebe o form (useForm do Inertia), os errors do Django,
// o título do dialog e controla visibilidade via v-model (open).
const props = defineProps(["form", "errors", "title", "open"])
const emit = defineEmits(["update:open", "submit"])

const dialogRef = ref(null)
const { isOpen, open, close } = useModal(dialogRef)

// Sincroniza v-model:open do pai com o estado interno do modal
watch(() => props.open, (val) => {
    if (val && !isOpen.value) open()
    if (!val && isOpen.value) close()
})

function handleClose() {
    close()
    emit("update:open", false)
}
</script>

<template>
    <dialog ref="dialogRef" @close="handleClose">
        <article>
            <header>
                <button aria-label="Close" rel="prev" @click="handleClose"></button>
                <h3>{{ title }}</h3>
            </header>
            <form @submit.prevent="$emit('submit')">
                <label>
                    Titulo
                    <input v-model="form.title" :aria-invalid="!!errors?.title" />
                    <small v-if="errors?.title" style="color: red">{{ errors.title[0] }}</small>
                </label>

                <label>
                    Diretor
                    <input v-model="form.director" :aria-invalid="!!errors?.director" />
                    <small v-if="errors?.director" style="color: red">{{ errors.director[0] }}</small>
                </label>

                <div class="grid">
                    <label>
                        Ano
                        <input v-model="form.year" type="number" min="0" :aria-invalid="!!errors?.year" />
                        <small v-if="errors?.year" style="color: red">{{ errors.year[0] }}</small>
                    </label>
                    <label>
                        Genero
                        <input v-model="form.genre" :aria-invalid="!!errors?.genre" />
                        <small v-if="errors?.genre" style="color: red">{{ errors.genre[0] }}</small>
                    </label>
                </div>

                <div class="grid">
                    <label>
                        Nota (0-10)
                        <input v-model="form.rating" type="number" min="0" max="10" :aria-invalid="!!errors?.rating" />
                        <small v-if="errors?.rating" style="color: red">{{ errors.rating[0] }}</small>
                    </label>
                    <label>
                        Status
                        <select v-model="form.status" :aria-invalid="!!errors?.status">
                            <option value="want">Quero Ver</option>
                            <option value="watching">Assistindo</option>
                            <option value="watched">Assistido</option>
                        </select>
                        <small v-if="errors?.status" style="color: red">{{ errors.status[0] }}</small>
                    </label>
                </div>

                <label>
                    Notas
                    <textarea v-model="form.notes" :aria-invalid="!!errors?.notes"></textarea>
                    <small v-if="errors?.notes" style="color: red">{{ errors.notes[0] }}</small>
                </label>

                <footer>
                    <div class="grid">
                        <button type="button" class="outline secondary" @click="handleClose">Cancelar</button>
                        <button type="submit" :disabled="form.processing" :aria-busy="form.processing">Salvar</button>
                    </div>
                </footer>
            </form>
        </article>
    </dialog>
</template>
```

Crie `frontend/src/Components/ConfirmDialog.vue` — dialog genérico de confirmação:

```vue
<script setup>
import { ref, watch } from "vue"
import { useModal } from "../composables/useModal"

// Controla visibilidade via v-model (open).
const props = defineProps(["open", "title", "message"])
const emit = defineEmits(["update:open", "confirm"])

const dialogRef = ref(null)
const { isOpen, open, close } = useModal(dialogRef)

watch(() => props.open, (val) => {
    if (val && !isOpen.value) open()
    if (!val && isOpen.value) close()
})

function handleClose() {
    close()
    emit("update:open", false)
}
</script>

<template>
    <dialog ref="dialogRef" @close="handleClose">
        <article>
            <header>
                <button aria-label="Close" rel="prev" @click="handleClose"></button>
                <h3>{{ title }}</h3>
            </header>
            <p v-html="message"></p>
            <footer>
                <div class="grid">
                    <button class="outline secondary" @click="handleClose">Cancelar</button>
                    <button class="contrast" @click="$emit('confirm')">Confirmar</button>
                </div>
            </footer>
        </article>
    </dialog>
</template>
```

Crie `frontend/src/composables/useModal.js` — composable que controla a animação dos modais PicoCSS:

```js
import { ref, watch, nextTick } from "vue"

/**
 * Composable para controlar modais com animação do PicoCSS.
 *
 * O PicoCSS espera que o modal use o HTMLDialogElement (showModal/close)
 * e que as classes modal-is-open, modal-is-opening e modal-is-closing
 * sejam aplicadas no <html> para controlar animações e scroll.
 */
export function useModal(dialogRef) {
    const isOpen = ref(false)
    const ANIMATION_DURATION = 400

    function open() {
        isOpen.value = true
        nextTick(() => {
            if (dialogRef.value) {
                dialogRef.value.showModal()
                document.documentElement.classList.add("modal-is-open", "modal-is-opening")
                setTimeout(() => {
                    document.documentElement.classList.remove("modal-is-opening")
                }, ANIMATION_DURATION)
            }
        })
    }

    function close() {
        document.documentElement.classList.add("modal-is-closing")
        setTimeout(() => {
            document.documentElement.classList.remove("modal-is-open", "modal-is-closing")
            if (dialogRef.value) {
                dialogRef.value.close()
            }
            isOpen.value = false
        }, ANIMATION_DURATION)
    }

    return { isOpen, open, close }
}
```

Crie `frontend/src/Components/Toast.vue` — componente que exibe flash messages do Django:

```vue
<script setup>
import { ref, watch } from "vue"

// Recebe as flash messages do Django via Inertia shared props.
// Cada mensagem é exibida por alguns segundos e removida automaticamente.
const props = defineProps(["messages"])

const visible = ref([])

watch(() => props.messages, (msgs) => {
    if (!msgs || !msgs.length) return

    msgs.forEach((msg, i) => {
        const item = { ...msg, id: Date.now() + i }
        visible.value.push(item)

        setTimeout(() => {
            visible.value = visible.value.filter(v => v.id !== item.id)
        }, 4000)
    })
}, { immediate: true })
</script>

<template>
    <div class="toast-container">
        <div
            v-for="toast in visible"
            :key="toast.id"
            class="toast"
            :class="toast.tags"
        >
            {{ toast.message }}
        </div>
    </div>
</template>
```

> O CSS do Toast (posicionamento fixo no canto superior direito, cores por tipo de mensagem e animações de entrada/saída) está no componente via `<style scoped>`. Veja o código-fonte completo no projeto.

Agora crie `frontend/src/Pages/Movies/Index.vue`. Todo o CRUD acontece nesta única página, usando os componentes acima.

```vue
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
        <!-- :stats é uma prop — passa o objeto stats do Django para o componente filho.
             No Vue, o prefixo ":" (abreviação de v-bind) indica que o valor é uma
             expressão JavaScript, não uma string literal. Sem ":", seria a string "stats". -->
        <StatsBar :stats="stats" />

        <!-- @click é um evento nativo do DOM. Quando o botão é clicado,
             executa a função openCreate() que reseta o form e abre o dialog. -->
        <button @click="openCreate">Novo filme</button>

        <!-- :movies é uma prop — passa a lista de filmes para o componente.
             @edit e @delete são eventos customizados emitidos pelo componente filho
             (via $emit). Quando o usuário clica "Editar" ou "Excluir" dentro da tabela,
             o MovieTable emite o evento com o objeto movie como argumento,
             e o Index.vue chama a função correspondente (openEdit ou confirmDelete). -->
        <MovieTable :movies="movies" @edit="openEdit" @delete="confirmDelete" />

        <!-- v-model:open é um binding bidirecional — o componente pai (Index) controla
             se o dialog está aberto, e o componente filho (MovieFormDialog) pode fechá-lo
             emitindo update:open. É equivalente a :open + @update:open juntos.
             :form passa o objeto useForm do Inertia (reativo — mudanças no filho
             refletem no pai automaticamente porque é o mesmo objeto por referência).
             :errors passa os erros do Django, mas só quando o dialog está aberto
             (evita mostrar erros de um dialog no outro).
             title sem ":" é uma string literal — não precisa de binding.
             @submit é um evento customizado — quando o form é submetido dentro do
             MovieFormDialog, ele emite "submit" e o Index.vue chama submitCreate(). -->
        <MovieFormDialog
            v-model:open="showCreateDialog"
            :form="createForm"
            :errors="showCreateDialog ? errors : {}"
            title="Novo Filme"
            @submit="submitCreate"
        />

        <!-- Mesmo componente MovieFormDialog reutilizado para edição.
             A única diferença são as props: editForm em vez de createForm,
             showEditDialog em vez de showCreateDialog, e submitEdit em vez de submitCreate.
             Isso é o poder dos componentes Vue — mesma UI, dados diferentes. -->
        <MovieFormDialog
            v-model:open="showEditDialog"
            :form="editForm"
            :errors="showEditDialog ? errors : {}"
            title="Editar Filme"
            @submit="submitEdit"
        />

        <!-- ConfirmDialog é um componente genérico — não sabe nada sobre filmes.
             Recebe title, message e emite "confirm" quando o usuário confirma.
             :message usa ":" porque o valor é uma template literal JavaScript
             (com ${} para interpolar o título do filme).
             @confirm chama executeDelete() que faz o POST para o Django. -->
        <ConfirmDialog
            v-model:open="showDeleteDialog"
            title="Confirmar exclusão"
            :message="`Tem certeza que deseja excluir <strong>${movieToDelete?.title}</strong>?`"
            @confirm="executeDelete"
        />
    </main>
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
    data = _get_post_data(request)
    form = MovieForm(data)

    if form.is_valid():
        form.save()
        messages.success(request, "Filme criado com sucesso!")
        return redirect("movie_list")

    # form.errors é {"title": ["Este campo é obrigatório."]} no POST inválido
    # Re-renderiza Movies/Index com os erros e showDialog='create'
    # para que o dialog reabra automaticamente com os erros exibidos.
    props = _index_props()
    props["errors"] = form.errors
    props["showDialog"] = "create"
    props["formData"] = dict(data)
    return render(request, "Movies/Index", props=props)
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