# Django + Inertia.js + Vue 3

CRUD de filmes usando Django no backend com Inertia.js e Vue 3 no frontend. Um monólito moderno com experiência SPA sem precisar de API REST, Vue Router, Pinia ou CORS.

## Stack

- [Django 6.1](https://docs.djangoproject.com/en/6.1/)
- [inertia-django 2.0](https://github.com/inertiajs/inertia-django) (protocolo Inertia v3)
- [Vue 3.5](https://vuejs.org/)
- [@inertiajs/vue3 3.7](https://inertiajs.com/) (client v3, sem axios)
- [Vite 8](https://vite.dev/)
- [django-vite 3.1](https://github.com/MrBin99/django-vite)
- [psycopg 3.3](https://www.psycopg.org/psycopg3/)
- [python-decouple 3.8](https://github.com/HBNetwork/python-decouple)
- [PostgreSQL 18.6](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
- [Ruff](https://docs.astral.sh/ruff/) (dev)

## Requisitos

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- Docker e Docker Compose

## Instalação

```bash
# Clone o repositório
git clone https://github.com/rg3915/django-inertia-vuejs.git
cd django-inertia-vuejs

# Copie o arquivo de variáveis de ambiente e gere uma SECRET_KEY
cp .env.example .env
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Cole o valor gerado na variável SECRET_KEY do .env

# Suba o banco de dados e o pgAdmin
docker compose up -d

# Instale as dependências Python
uv sync

# Rode as migrations
uv run python manage.py migrate

# Popule o banco com os filmes da demonstração
uv run python manage.py seed_movies

# Instale as dependências do frontend
cd frontend
npm install
cd ..
```

## Rodando o projeto

Você precisa de dois terminais:

```bash
# Terminal 1 - Django
uv run python manage.py runserver
```

```bash
# Terminal 2 - Vite (frontend)
cd frontend
npm run dev
```

Acesse http://localhost:8000

## Dados de exemplo

```bash
# Popula o banco (idempotente — não duplica)
uv run python manage.py seed_movies

# Apaga tudo antes de popular
uv run python manage.py seed_movies --clear
```

Os três primeiros filmes são do Quentin Tarantino de propósito: na demonstração,
digitar `tarantino` na busca filtra a lista em tempo real, do lado do cliente,
sem nenhuma requisição ao servidor.

## Notas sobre o Inertia v3

O projeto usa o protocolo Inertia v3, que mudou dois pontos em relação ao v2:

- **CSRF** — o client v3 trocou o axios por um XHR próprio, que por padrão usa os
  nomes do Laravel (`XSRF-TOKEN` / `X-XSRF-TOKEN`). Em vez de adaptar o Django, o
  client é configurado com os nomes nativos em `frontend/src/main.js`, e o
  `settings.py` fica com os padrões (`csrftoken` / `X-CSRFToken`).
- **Flash messages** — as mensagens do `django.contrib.messages` agora são nativas
  e chegam em `page.flash.messages` (não como prop). O middleware customizado que
  fazia isso à mão foi removido.

## Documentação

Veja o arquivo [django_inertia.md](django_inertia.md) para o guia completo do projeto.

Veja [detalhes.md](detalhes.md) para um guia de leitura do código: onde o Inertia
entra na configuração, como a view conversa com o componente Vue e o que o projeto
deixa de precisar por não ter uma API REST no meio.

## Palestra

Os slides da palestra **Inertia.js — O Monolito Moderno: construindo SPAs com Django
e Vue sem precisar de uma API REST**, que usa este projeto como demonstração:

- [palestra-inertia-v4.pdf](palestra-inertia-v4.pdf) — versão para leitura offline
- [slides.com/regissantos/inertiajs](https://slides.com/regissantos/inertiajs) — versão online
