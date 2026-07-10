# Backend API

API Python com FastAPI, SQLAlchemy e Alembic.

## Setup local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Migrações (Alembic)

```bash
# Aplicar migrações
alembic upgrade head

# Criar nova migração (autogenerate)
alembic revision --autogenerate -m "descricao"

# Reverter última migração
alembic downgrade -1
```

## Executar

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Estrutura

```
app/
├── api/v1/       # Rotas da API
├── core/         # Config e database
├── models/       # Modelos SQLAlchemy
├── schemas/      # Schemas Pydantic
└── main.py       # Entry point FastAPI
alembic/          # Migrações de banco
tests/            # Testes
```
