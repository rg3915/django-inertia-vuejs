# Django + Inertia.js + Vue 3

CRUD de filmes usando Django no backend com Inertia.js e Vue 3 no frontend. Um monólito moderno com experiência SPA sem precisar de API REST, Vue Router, Pinia ou CORS.

## Stack

- [Django 6.0.3](https://docs.djangoproject.com/en/6.0/)
- [inertia-django 1.2.0](https://github.com/inertiajs/inertia-django)
- [Vue 3](https://vuejs.org/)
- [Vite](https://vite.dev/)
- [django-vite 3.1.0](https://github.com/MrBin99/django-vite)
- [python-decouple 3.8](https://github.com/HBNetwork/python-decouple)
- [PostgreSQL 18.3](https://www.postgresql.org/)
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

## Produção

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## Documentação

Veja o arquivo [django_inertia.md](django_inertia.md) para o guia completo do projeto.
