# Onde o Inertia acontece no projeto

Guia de leitura do `django-inertia-vuejs` para a palestra. Cada seção liga um
slide ao código que o sustenta.

Repositório: https://github.com/rg3915/django-inertia-vuejs

---

## Mapa rápido

| Slide | Ideia | Onde está no código |
|---|---|---|
| 15 — Entra o Inertia.js | "Substitui apenas o sistema de templates" | `apps/settings.py:128` |
| 16 — Onde o Inertia entra | Um app só, um deploy | `apps/settings.py:42-55` |
| 17/18 — A ponte | Django fala Python, Vue fala JS | `apps/core/views.py:35` ↔ `frontend/src/Pages/Movies/Index.vue:21` |
| 19 — Como funciona uma requisição | 3 etapas do protocolo | `templates/base.html:12`, `apps/core/views.py:45` |
| 20 — O código: a view | `render(request, "Movies/Index", props=...)` | `apps/core/views.py:34-35` |
| 21 — O código: o componente | `defineProps` recebendo do Django | `frontend/src/Pages/Movies/Index.vue:21-25` |
| 22 — O que você ganha | Auth, rotas e estado no Django | `apps/core/urls.py:5-10` |
| 23 — Com vs. sem Inertia | O que **não** existe no repo | ver "As ausências" |
| 12 — Exemplo do dia a dia | Busca reativa sem servidor | `frontend/src/Components/MovieTable.vue:15-27` |

---

## 1. A configuração — são quatro linhas

Este é o argumento do **slide 15** ("uma camada fina, não um framework
gigante"). O Inertia não pede reestruturação: entra em quatro pontos.

**`apps/settings.py:43`** — o app:

```python
'inertia',
```

**`apps/settings.py:55`** — o middleware, que detecta o cabeçalho `X-Inertia`
e decide entre devolver HTML ou JSON:

```python
'inertia.middleware.InertiaMiddleware',  # adicionar após SessionMiddleware
```

**`apps/settings.py:128`** — a linha mais importante para a tese da palestra:

```python
INERTIA_LAYOUT = 'base.html'
```

É aqui que se vê que o Inertia **substitui o sistema de templates, e nada
mais**. Ele não toma conta das rotas, da sessão nem do ORM.

**`templates/base.html:12`** — o layout inteiro é um HTML comum com um bloco:

```html
{% block inertia %}{% endblock %}
```

O `inertia-django` preenche esse bloco com o `<div id="app">` e um
`<script type="application/json">` contendo os dados da página.

### O lado do cliente

**`frontend/src/main.js:5-25`** — o `createInertiaApp` faz o espelho disso:
`resolve` mapeia o nome que a view passou (`"Movies/Index"`) para o arquivo
`./Pages/Movies/Index.vue`.

```js
resolve: (name) => {
    const pages = import.meta.glob("./Pages/**/*.vue", { eager: true })
    return pages[`./Pages/${name}.vue`]
},
```

**`frontend/src/main.js:15-18`** — a única configuração específica de Django,
por causa do Inertia v3:

```js
http: {
    xsrfCookieName: "csrftoken",
    xsrfHeaderName: "X-CSRFToken",
},
```

O v3 trocou o axios por um cliente XHR próprio, que usa os nomes de CSRF do
Laravel por padrão. Em vez de renomear o cookie do Django, ensinamos o cliente
a falar a língua dele — o `settings.py` fica com os padrões do framework.

---

## 2. O uso — a view (slide 20)

**`apps/core/views.py:34-35`** é o slide 20 quase literalmente:

```python
def movie_list(request):
    return render(request, 'Movies/Index', props=_index_props())
```

Três coisas a destacar ao vivo:

1. O `render` importado na **linha 6** vem de `inertia`, não de
   `django.shortcuts`. É a única troca de import do projeto inteiro.
2. O 2º argumento é o **nome de um componente Vue**, não um arquivo `.html`.
3. O 3º são os dados, que vão **direto para o componente**. Não há serializer,
   nem `JsonResponse`, nem endpoint.

### De onde vêm os props

**`apps/core/views.py:19-31`** monta um dict Python comum:

```python
def _index_props():
    movies = Movie.objects.all()
    data = [movie.serializable_values(exclude=['added_at']) for movie in movies]
    return {
        'movies': data,
        'stats': {...},
    }
```

**`apps/core/models.py:52-53`** mostra bem a ausência de camada de
serialização — campos derivados entram no payload como qualquer outro:

```python
tree['status_label'] = self.status_label   # 'watched' -> 'Assistido'
tree['stars'] = self.stars                 # 4 -> '★★★★☆'
```

Num projeto com DRF, isso seria um `SerializerMethodField` num arquivo à parte.
Aqui é uma `@property` no model (`models.py:32-41`).

---

## 3. O uso — o componente (slide 21)

**`frontend/src/Pages/Movies/Index.vue:21-25`**:

```js
const props = defineProps([
    "movies", "stats",
    "errors", "showDialog", "editMovie", "formData",
])
```

Os dados **já estão aqui** quando o componente monta. Não existe `fetch`,
`onMounted` buscando dados, estado de `loading` nem store.

### Formulários (slide 19, etapa 3)

**`Index.vue:60`** — o POST vai direto para uma rota do Django:

```js
createForm.post("/create/", { onSuccess: () => { ... } })
```

`"/create/"` é literalmente a rota de **`apps/core/urls.py:7`**. Não existe um
`/api/` no meio, e não existe Vue Router traduzindo URL para componente.

**`apps/core/views.py:42-45`** — o backend responde como Django sempre
respondeu, com um redirect:

```python
if form.is_valid():
    form.save()
    messages.success(request, 'Filme criado com sucesso!')
    return redirect('movie_list')
```

O Inertia entende o 302 e busca a próxima página sozinho. É o slide 19 na
prática: **"o Django processa, salva e faz um redirect — como sempre fez"**.

### Erros de validação

**`views.py:47-51`** — quando o form não valida, a view re-renderiza a mesma
página com props extras:

```python
props['errors'] = form.errors
props['showDialog'] = 'create'
props['formData'] = dict(data)
```

`form.errors` do Django chega ao Vue sem tradução. O `onMounted` em
**`Index.vue:120-131`** lê esses props e reabre o dialog preenchido.

### Flash messages

**`frontend/src/Components/Toast.vue:10-14`** — a partir do Inertia v3 as
mensagens do Django são nativas:

```js
const page = usePage()
watch(() => page.flash?.messages, (msgs) => { ... })
```

`messages.success(...)` no Django aparece como toast no Vue. Nenhuma linha de
cola entre os dois — antes deste projeto usar o v3, havia um middleware
customizado só para isso, hoje removido.

---

## 4. A busca reativa (slide 12)

**`frontend/src/Components/MovieTable.vue:15-27`** é onde os dois mundos da
palestra se encontram. Os filmes vieram do Django como props; filtrar é só uma
`computed` sobre um array em memória:

```js
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
```

O que vale apontar é o que **não** está aqui: nenhum `fetch`, nenhum endpoint
`/api/filmes/?q=`, nenhum debounce, nenhum estado de loading.

Na demo, digitar `tarantino` filtra 3 de 8 instantaneamente — os três primeiros
filmes do seed são do Tarantino de propósito
(`apps/core/management/commands/seed_movies.py`).

---

## 5. As ausências (slides 22 e 23)

O slide 23 é uma tabela de "Não precisa". Isso é verificável no repositório —
e é um momento forte para mostrar ao vivo:

```bash
grep -rn "serializers\|rest_framework\|vue-router\|pinia\|corsheaders" apps/ frontend/src/
# nenhum resultado
```

| Slide 23 diz | No repositório |
|---|---|
| API REST — não precisa | Nenhuma rota `/api/`; ver `apps/core/urls.py` |
| Serializers — não precisa | Zero ocorrências |
| CORS — não precisa | `corsheaders` não está instalado |
| Autenticação — sessão do Django | Nenhum JWT; `MIDDLEWARE` padrão |
| Vue Router — não existe | Zero ocorrências; as rotas estão em `urls.py` |
| Pinia — não precisa | Zero ocorrências |
| Projetos/deploys — um | Um `manage.py`, um `package.json` |

Até o **axios sumiu**: no Inertia v3 ele foi substituído por um cliente XHR
interno. As duas únicas ocorrências da palavra no projeto são comentários
explicando isso (`settings.py:122` e `main.js:11`).

Tamanho total: **451 linhas de Python** e **575 de Vue/JS** para um CRUD
completo com busca, dialogs e toasts.

---

## 6. O protocolo, em três etapas (slide 19)

Dá para demonstrar com `curl`, com os dois servidores rodando:

**1 — Primeira visita.** HTML completo, com os dados embutidos:

```bash
curl -s http://localhost:8000/ | grep -o '<script data-page="app"[^>]*>'
# <script data-page="app" type="application/json">
```

**2 — Navegações seguintes.** O mesmo endereço, agora com o cabeçalho:

```bash
curl -s -H "X-Inertia: true" -H "X-Inertia-Version: 1.0" http://localhost:8000/
# {"component": "Movies/Index", "props": {...}, "url": "/", ...}
```

Mesma URL, mesma view. Só muda o formato da resposta — é isso que o middleware
da `settings.py:55` faz.

**3 — Envio de formulário.** Responde `302`, como qualquer view Django.

Repare também no cabeçalho `Vary: X-Inertia` da resposta: é ele que impede um
cache de servir o JSON para quem pediu HTML.

---

## Nota sobre o código

`apps/core/views.py:12-16` tem um helper com uma docstring que envelheceu:

```python
def _get_post_data(request):
    """O Inertia v2 envia JSON, mas o Django ModelForm espera QueryDict."""
```

O comportamento continua correto no v3 (o cliente segue enviando JSON), mas o
texto diz "v2". Se for mostrar esse trecho na tela, vale corrigir antes — ou
usar como gancho para comentar que o projeto foi migrado para o v3.
