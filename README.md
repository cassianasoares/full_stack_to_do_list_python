# Todo List — Aplicação Fullstack

Aplicação de lista de tarefas com autenticação de usuários, construída com **Django REST Framework** no backend e **React + TypeScript** no frontend, servidos juntos por um **Nginx** via **Docker Compose**.

---

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────────────────┐
│                   Docker Compose                     │
│                                                      │
│  ┌─────────────────────────────────────────────┐     │
│  │          container: frontend                │     │
│  │                                             │     │
│  │   Nginx :80  ──► /          React (dist)    │     │
│  │               ──► /api/     proxy → web     │     │
│  │               ──► /admin/   proxy → web     │     │
│  │               ──► /static/  Django statics  │     │
│  └───────────────────────┬─────────────────────┘     │
│                          │ rede interna docker       │
│  ┌───────────────────────▼─────────────────────┐     │
│  │            container: web                   │     │
│  │                                             │     │
│  │        Django + Gunicorn :8000              │     │
│  └─────────────────────────────────────────────┘     │
│                                                      │
│  Volumes: sqlite_data · django_static                │
└──────────────────────────────────────────────────────┘
         ▲
  host: localhost:8000
```

**Decisões de design:**

- **Nginx como ponto de entrada único** — todo o tráfego entra pela porta `8000` do host. O Nginx roteia as requisições para o React ou para o Django sem expor o backend diretamente.
- **Volume compartilhado `django_static`** — o backend executa `collectstatic` e deposita os arquivos neste volume. O Nginx lê o mesmo volume para servir os estáticos do Django (ex: painel de administração) sem passar pelo Gunicorn.
- **Backend isolado na rede interna** — o container `web` não expõe nenhuma porta ao host, só é acessível internamente pelo Nginx. Isso reduz a superfície de ataque.

---

## 🚀 Tecnologias

### Backend (`/backend`)
| Tecnologia | Versão | Papel |
|---|---|---|
| Python | 3.12 | Runtime |
| Django | ^6.0 | Framework web |
| Django REST Framework | ^3.17 | Construção da API REST |
| djangorestframework-simplejwt | ^5.3 | Autenticação via JWT |
| Gunicorn | ^21.0 | Servidor WSGI de produção |
| SQLite | — | Banco de dados (persistido em volume) |
| python-dotenv | ^1.0 | Carregamento de variáveis de ambiente |
| pytest + pytest-django | — | Testes automatizados |

### Frontend (`/frontend`)
| Tecnologia | Versão | Papel |
|---|---|---|
| React | 19 | UI |
| TypeScript | — | Tipagem estática |
| Vite | 8 | Bundler e dev server |
| react-router-dom | — | Roteamento SPA |
| axios | — | Cliente HTTP com interceptors |

### Infraestrutura
| Tecnologia | Papel |
|---|---|
| Nginx | Proxy reverso + servidor de estáticos |
| Docker Compose | Orquestração dos containers |

---

## 📂 Estrutura do Projeto

```
todo_list/
├── backend/                    # Aplicação Django
│   ├── config/                 # Configuração central do Django
│   │   ├── settings.py         # Settings com suporte a .env
│   │   ├── settings_ci.py      # Settings para CI (SQLite em memória)
│   │   ├── urls.py             # Roteamento raiz → /api/auth/
│   │   └── wsgi.py
│   ├── accounts/               # App de autenticação e usuários
│   │   ├── models.py           # Modelo User customizado (login por e-mail)
│   │   ├── serializers.py      # Validação e serialização de dados
│   │   ├── views.py            # Endpoints: register, login, logout, me
│   │   ├── urls.py             # Rotas do app accounts
│   │   └── tests/              # Testes unitários e de integração
│   ├── requirements.txt        # Dependências de produção
│   ├── requirements-dev.txt    # Dependências extras de desenvolvimento
│   ├── Dockerfile              # Imagem do backend (Python + Gunicorn)
│   ├── pyproject.toml          # Configuração de ferramentas (ruff, etc.)
│   ├── pytest.ini              # Configuração do pytest
│   └── bandit.yaml             # Configuração do scan de segurança Bandit
│
├── frontend/                   # Aplicação React
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts       # Instância axios + interceptor de 401
│   │   │   └── auth.ts         # Funções de chamada à API de autenticação
│   │   ├── context/
│   │   │   └── AuthContext.tsx # Estado global de autenticação (React Context)
│   │   ├── routes/
│   │   │   └── ProtectedRoute.tsx  # HOC para rotas que exigem login
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   └── HomePage.tsx
│   │   ├── types/              # Tipos TypeScript compartilhados
│   │   └── App.tsx             # Configuração das rotas com react-router-dom
│   ├── Dockerfile              # Multi-stage: Node build → Nginx serve
│   └── vite.config.ts          # Proxy /api → localhost:8000 (dev local)
│
├── nginx/
│   └── nginx.conf              # Regras de roteamento do Nginx
│
├── e2e/                        # Testes E2E com Selenium
│   ├── conftest.py             # Fixtures compartilhadas (driver, usuário de teste)
│   ├── pytest.ini              # Configuração do pytest para E2E
│   ├── requirements.txt        # Dependências: selenium, pytest, webdriver-manager
│   ├── pages/                  # Page Object Models (POM)
│   │   ├── login_page.py       # Seletores e ações da página de login
│   │   ├── register_page.py    # Seletores e ações da página de registro
│   │   └── home_page.py        # Seletores e ações da página home
│   └── tests/
│       ├── test_login.py       # Testes de login (estrutura, erros, sucesso)
│       ├── test_register.py    # Testes de registro (validação client-side, sucesso)
│       └── test_session.py     # Testes de sessão e proteção de rotas
│
└── docker-compose.yml          # Orquestração: frontend + web
```

---

## 🔒 Segurança

- **JWT via HttpOnly Cookies** — os tokens de acesso e refresh são armazenados em cookies `HttpOnly`, impedindo acesso via JavaScript e mitigando ataques XSS.
- **Rotação de refresh tokens** — a cada refresh, o token antigo é invalidado e adicionado à blacklist (`simplejwt` + `token_blacklist`).
- **Autenticação por e-mail** — o modelo `User` é customizado (`AUTH_USER_MODEL`) e usa e-mail como `USERNAME_FIELD`, com backend de autenticação dedicado (`EmailBackend`).
- **Usuário não-root no container** — o container Django cria e usa o usuário `django`, sem privilégios de root.
- **Backend sem porta exposta** — o container `web` não publica nenhuma porta ao host; só é acessível pelo Nginx via rede interna do Docker.
- **Variáveis de ambiente** — nenhuma configuração sensível está no código. Tudo é carregado via `.env` com `python-dotenv`.
- **Bandit** — análise estática de segurança no código Python, configurada via `bandit.yaml` e integrada ao CI.

---

## ⚙️ Como rodar

### Pré-requisitos
- Docker e Docker Compose instalados.

### Passos

1. Copie o arquivo de ambiente do backend:

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Ajuste as variáveis no arquivo `backend/.env`:

   ```env
   DJANGO_SECRET_KEY=sua_chave_secreta_aqui
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1,web
   ```

3. Suba os containers:

   ```bash
   docker-compose up --build -d
   ```

4. Acesse a aplicação em:

   ```
   http://localhost:8000
   ```

### Desenvolvimento local (sem Docker)

Para rodar o backend localmente:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

Para rodar o frontend localmente (com proxy configurado para `localhost:8000`):

```bash
cd frontend
npm install
npm run dev
```

### Testes de Unidade/Integração (Backend)

```bash
cd backend
pytest
```

### Testes E2E com Selenium

Os testes E2E rodam contra a aplicação em execução (`docker-compose up -d`) e
exigem o Google Chrome instalado na máquina local.

**1. Instale as dependências:**

```bash
cd e2e
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Certifique-se que a aplicação está rodando:**

```bash
# Na raiz do projeto
docker-compose up -d
```

**3. Execute todos os testes E2E:**

```bash
cd e2e
pytest
```

**4. Opções úteis:**

```bash
# Rodar apenas testes de autenticação
pytest -m auth

# Rodar apenas testes que precisam do backend (marcados como slow)
pytest -m slow

# Rodar testes de proteção de rotas
pytest -m session

# Ver log detalhado de cada passo
pytest -v --tb=long
```

#### Arquitetura dos testes E2E

Os testes seguem o padrão **Page Object Model (POM)**:

- Cada página da aplicação tem uma classe correspondente em `e2e/pages/` que encapsula todos os seletores e ações.
- Os testes em `e2e/tests/` interagem apenas com os Page Objects, nunca com o WebDriver diretamente.
- Os elementos são selecionados via atributo `data-testid`, que é estável a mudanças de estilo ou estrutura HTML.
- O Chrome roda em modo **headless** (sem janela), tornando os testes compatíveis com CI.

---

## 🌐 Endpoints da API

Prefixo base: `/api/auth/`

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/auth/register/` | Cadastro de novo usuário |
| `POST` | `/api/auth/login/` | Login (retorna cookies JWT) |
| `POST` | `/api/auth/logout/` | Logout (invalida tokens) |
| `GET` | `/api/auth/me/` | Dados do usuário autenticado |

---

## 📂 Volumes Docker

| Volume | Descrição |
|---|---|
| `sqlite_data` | Persistência do banco de dados `db.sqlite3` |
| `django_static` | Arquivos estáticos do Django coletados via `collectstatic`, compartilhados com o Nginx |
