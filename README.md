# 🔥 Divulga PRO

> Gerador de mensagens de venda para afiliados — cole o link, copie a mensagem pronta.

![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)
![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=flat-square&logo=vite)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103-009688?style=flat-square&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-BaaS-3ECF8E?style=flat-square&logo=supabase)
![License](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)

---

## 📌 Sobre o projeto

**Divulga PRO** é uma aplicação SaaS voltada para afiliados e divulgadores de promoções. O usuário cola o link de um produto de grandes marketplaces brasileiros e recebe automaticamente o título, o preço e uma mensagem formatada pronta para compartilhar no WhatsApp, Telegram ou redes sociais.

O sistema conta com autenticação, planos de assinatura (FREE e PRO) e controle de acesso por Row Level Security no banco de dados.

---

## ✨ Funcionalidades

- 🔗 **Scraping automático** de produtos por URL
- 🛒 **Lojas suportadas:** Mercado Livre, Americanas, Shopee, Kabum, Casas Bahia, OLX e Magazine Luiza
- 📋 **Mensagem pronta** formatada para cópia com um clique
- 🔐 **Autenticação** com Supabase Auth (JWT)
- 👤 **Planos FREE e PRO** com limites e features diferenciadas
- 🛡️ **Rotas protegidas** com guard de autenticação e plano
- 📱 **Design responsivo** com tema dark minimalista

---

## 🗂️ Arquitetura

```
├── backend/               # API Python (FastAPI)
│   ├── main.py            # Endpoints REST
│   ├── scraper.py         # Scrapers por marketplace
│   └── requirements.txt
│
└── src/                   # Frontend React (Vite)
    ├── contexts/          # AuthContext (estado global)
    ├── pages/             # Login, Register, Home, Dashboard, ChoosePlan
    ├── routes/            # ProtectedRoute (guard)
    ├── services/          # Supabase client, API URL
    └── components/        # ResultCard
```

### Stack

| Camada | Tecnologia |
|---|---|
| Frontend | React 19 + Vite 7 |
| Roteamento | React Router v7 |
| Estilo | CSS Modules (tema dark) |
| Backend | Python + FastAPI |
| Scraping | Requests + BeautifulSoup4 |
| BaaS | Supabase (Auth + PostgreSQL + RLS) |

---

## 🚀 Como rodar localmente

### Pré-requisitos

- Node.js >= 20
- Python >= 3.10
- Conta no [Supabase](https://supabase.com)

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/divulga-pro.git
cd divulga-pro
```

### 2. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
VITE_SUPABASE_URL=sua_url_do_supabase
VITE_SUPABASE_ANON_KEY=sua_anon_key
```

### 3. Inicie o backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. Inicie o frontend

```bash
# na raiz do projeto
npm install
npm run dev
```

Acesse `http://localhost:5173`

---

## 🗄️ Banco de dados (Supabase)

O projeto utiliza uma trigger SQL que cria automaticamente o perfil do usuário ao se cadastrar:

```sql
create function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.profiles (id, email, plan)
  values (new.id, new.email, 'free');
  return new;
end;
$$;

create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();
```

A tabela `profiles` armazena o plano do usuário (`free` ou `pro`) com Row Level Security habilitado.

---

## 📐 Fluxo da aplicação

```
/login ou /register
        ↓
  Autenticação via Supabase
        ↓
  /choose-plan  (se sem plano)
        ↓
  /dashboard    (painel do usuário)
        ↓
  /home         (gerador de links)
```

Todas as rotas após login são protegidas pelo componente `ProtectedRoute`, que valida sessão e plano antes de renderizar.

---

## 🏪 Lojas e estratégia de scraping

Cada marketplace tem um scraper dedicado com múltiplas estratégias de fallback:

1. **JSON-LD** (`application/ld+json`) — padrão rico em dados estruturados
2. **`__NEXT_DATA__`** — dados server-side de apps Next.js
3. **Meta tags** (`og:title`, `product:price:amount`, `itemprop`)
4. **API pública** — usado na Shopee para extrair dados via `shopid/itemid`
5. **Regex no HTML** — fallback de último recurso

---

## 📦 Deploy

- **Frontend:** [Netlify](https://netlify.com) — build: `npm run build`, publish: `dist/`
- **Backend:** [Render](https://render.com) — `uvicorn main:app --host 0.0.0.0 --port 8000`

> Lembre de trocar `API_URL` em `src/services/api.js` para a URL de produção antes do build.

---

## 📄 Licença

MIT © 2025 Divulga PRO
