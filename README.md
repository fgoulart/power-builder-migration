# Power Builder Migration

Monorepo com **Angular** (frontend) e **Python/FastAPI** (backend) com **Alembic** para migrações de banco de dados.

## Estrutura

```
.
├── apps/
│   ├── frontend/          # Angular 19
│   └── backend/           # FastAPI + SQLAlchemy + Alembic
├── docker-compose.yml     # PostgreSQL + backend
└── package.json           # Scripts do monorepo
```

## Pré-requisitos

- Node.js >= 20
- Python >= 3.11
- Docker (opcional, para PostgreSQL)

## Início rápido

### 1. Instalar dependências

```bash
# Raiz do monorepo
npm install

# Backend Python
npm run backend:install
```

### 2. Banco de dados

```bash
# Subir PostgreSQL via Docker
docker compose up -d db

# Copiar variáveis de ambiente
cp apps/backend/.env.example apps/backend/.env

# Rodar migrações
npm run db:migrate
```

### 3. Desenvolvimento

```bash
# Frontend e backend em paralelo
npm run dev

# Ou separadamente:
npm run frontend    # http://localhost:4200
npm run backend     # http://localhost:8000
```

## URLs

| Serviço        | URL                          |
|----------------|------------------------------|
| Frontend       | http://localhost:4200        |
| Backend API    | http://localhost:8000        |
| API Docs       | http://localhost:8000/docs   |
| PostgreSQL     | localhost:5432               |

## Comandos úteis

```bash
# Nova migração Alembic
npm run db:revision -- "descricao da migracao"

# Build do frontend
npm run frontend:build

# Testes do frontend
npm run frontend:test
```
