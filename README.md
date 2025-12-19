# Fazendas API

API RESTful para consulta de fazendas com dados geoespaciais, desenvolvida com FastAPI, SQLAlchemy e PostGIS.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias](#tecnologias)
- [Funcionalidades](#funcionalidades)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Uso da API](#uso-da-api)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Testes](#testes)
- [Otimizações](#otimizações)

## 🎯 Sobre o Projeto

A Fazendas API é uma aplicação que permite consultar informações sobre fazendas utilizando dados geoespaciais. A API oferece endpoints para buscar fazendas por ID, por ponto geográfico (latitude/longitude) e por raio de distância, com suporte a paginação.

### Características Principais

- ✅ Consultas espaciais otimizadas com PostGIS
- ✅ Paginação em endpoints de busca
- ✅ Retorno de coordenadas (latitude/longitude) do centróide
- ✅ Validação de entrada com Pydantic
- ✅ Logging estruturado
- ✅ Health check endpoint
- ✅ Documentação interativa (Swagger UI)
- ✅ Seed data automático (56 fazendas)

## 🚀 Tecnologias

- **Python 3.11**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **GeoAlchemy2** - Extensão espacial para SQLAlchemy
- **Shapely** - Manipulação de geometrias
- **PostgreSQL + PostGIS** - Banco de dados com extensão espacial
- **Docker & Docker Compose** - Containerização
- **Pydantic** - Validação de dados
- **Pytest** - Framework de testes

## 📦 Funcionalidades

### Endpoints Disponíveis

#### 1. **GET /fazendas/{gid}**

Busca uma fazenda específica por ID.

**Resposta:**

```json
{
  "gid": 1,
  "cod_imovel": "SP-3500105-279714F410E746B0B440EFAD4B0933D4",
  "municipio": "Adamantina",
  "cod_estado": "SP",
  "latitude": -21.709303464740216,
  "longitude": -51.072970851419676,
  ...
}
```

#### 2. **POST /fazendas/busca-ponto**

Busca fazendas que contêm um ponto geográfico específico.

**Request:**

```json
{
  "latitude": -21.6813,
  "longitude": -50.7479
}
```

**Resposta:** Lista de fazendas que contêm o ponto.

#### 3. **POST /fazendas/busca-raio**

Busca fazendas dentro de um raio (em km) a partir de um ponto, com paginação.

**Request:**

```json
{
  "latitude": -21.6813,
  "longitude": -50.7479,
  "raio_km": 50,
  "page": 1,
  "page_size": 10
}
```

**Resposta:**

```json
{
  "count": 56,
  "page": 1,
  "page_size": 10,
  "total_pages": 6,
  "raio_km": 50,
  "results": [...]
}
```

#### 4. **GET /health**

Verifica o status da API e conectividade com o banco de dados.

**Resposta:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

## 📋 Pré-requisitos

- Docker
- Docker Compose

## 🔧 Instalação e Execução

### 1. Clone o repositório

```bash
git clone https://github.com/ZeRoColdma/mtteste
cd mtteste
```

### 2. Inicie a aplicação com Docker Compose

```bash
docker-compose up --build
```

A aplicação estará disponível em:

- **API**: <http://localhost:8000>
- **Documentação Interativa (Swagger)**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

### 3. Parar a aplicação

```bash
docker-compose down
```

### 4. Parar e remover volumes (limpar banco de dados)

```bash
docker-compose down -v
```

## 📖 Uso da API

### Via Swagger UI (Recomendado)

1. Acesse <http://localhost:8000/docs>
2. Explore os endpoints disponíveis
3. Clique em "Try it out" para testar
4. Preencha os parâmetros e clique em "Execute"

### Via cURL

**Buscar fazenda por ID:**

```bash
curl http://localhost:8000/fazendas/1
```

**Buscar por ponto:**

```bash
curl -X POST "http://localhost:8000/fazendas/busca-ponto" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -21.6813,
    "longitude": -50.7479
  }'
```

**Buscar por raio (com paginação):**

```bash
curl -X POST "http://localhost:8000/fazendas/busca-raio" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -21.6813,
    "longitude": -50.7479,
    "raio_km": 50,
    "page": 1,
    "page_size": 10
  }'
```

### Via Python

```python
import httpx

# Buscar por raio
response = httpx.post(
    "http://localhost:8000/fazendas/busca-raio",
    json={
        "latitude": -21.6813,
        "longitude": -50.7479,
        "raio_km": 50,
        "page": 1,
        "page_size": 10
    }
)

data = response.json()
print(f"Total de fazendas: {data['count']}")
print(f"Página {data['page']} de {data['total_pages']}")
```

## 📁 Estrutura do Projeto

```
mtteste/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configurações centralizadas
│   │   ├── database.py        # Conexão com banco de dados
│   │   └── exceptions.py      # Exceções customizadas
│   └── fazendas/
│       ├── __init__.py
│       ├── models_sqla.py     # Modelos SQLAlchemy
│       ├── schemas.py         # Schemas Pydantic
│       ├── routes/            # Camada de rotas (API handlers)
│       │   ├── __init__.py
│       │   └── fazendas.py
│       ├── services/          # Camada de serviços (lógica de negócio)
│       │   ├── __init__.py
│       │   └── fazenda_service.py
│       └── repositories/      # Camada de repositórios (acesso a dados)
│           ├── __init__.py
│           └── fazenda_repository.py
├── scripts/                   # Scripts utilitários
│   ├── __init__.py
│   ├── create_tables.py       # Script de criação de tabelas
│   ├── load_seeds.py          # Script de carga de dados
│   └── waitfordb.py           # Script de espera do banco
├── tests/
│   ├── __init__.py
│   └── test_fazendas.py       # Testes da API
├── main.py                    # Ponto de entrada da aplicação
├── seeds.json                 # Dados iniciais (56 fazendas)
├── requirements.txt           # Dependências Python
├── pytest.ini                 # Configuração de testes
├── Dockerfile                 # Configuração Docker
├── docker-compose.yml         # Orquestração de containers
└── README.md                  # Este arquivo
```

## 🧪 Testes

### Executar testes

```bash
docker-compose run --rm app pytest tests/test_fazendas.py -v
```

### Cobertura de testes

Os testes cobrem:

- ✅ GET /fazendas/{gid}
- ✅ POST /fazendas/busca-ponto
- ✅ POST /fazendas/busca-raio

## ⚡ Otimizações

### Performance

- **Connection Pooling**: Pool de 5 conexões + 10 overflow
- **Índices Espaciais**: Índice GIST na coluna `geom`
- **Índices Compostos**: `municipio` + `cod_estado`
- **Paginação**: Evita carregar todos os resultados em memória

### Código

- **Configuração Centralizada**: Variáveis de ambiente com `pydantic-settings`
- **Error Handling**: Exceções customizadas e handlers globais
- **Validação**: Validators Pydantic para coordenadas e parâmetros
- **Logging Estruturado**: Logs com timestamp, nível e contexto

### API

- **CORS**: Configurável via environment variables
- **Compressão GZip**: Respostas > 1KB são comprimidas
- **Request Tracking**: UUID único por requisição (header `X-Request-ID`)
- **Process Time**: Header `X-Process-Time` em todas as respostas

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` (opcional) para customizar:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fazendasdb
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Database Pool
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# API
API_TITLE=Fazendas API
API_VERSION=1.0.0
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["*"]
```

## 📊 Dados Iniciais

A aplicação vem com 56 fazendas pré-cadastradas de Adamantina/SP, carregadas automaticamente na primeira inicialização a partir do arquivo `seeds.json`.
