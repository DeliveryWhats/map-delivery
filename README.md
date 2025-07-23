# Store Coverage API

Uma API Python simples para determinar se uma geolocalização é atendida por alguma loja de uma empresa, baseada em arquivos de mapas KML/KMZ.

## Funcionalidades

- **Verificação de Cobertura**: Determina se uma coordenada (latitude/longitude) está dentro da área de cobertura de uma loja
- **Suporte a KML/KMZ**: Processa arquivos de mapas nos formatos KML e KMZ
- **Busca Flexível**: 
  - Sem `store_id`: retorna a primeira loja que cobre a região
  - Com `store_id`: verifica se essa loja específica cobre a região
- **API REST**: Endpoints GET e POST para facilitar testes e integração
- **PostgreSQL**: Utiliza PostgreSQL como banco de dados

## Configuração

### 1. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure suas credenciais do PostgreSQL:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Database Configuration
DB_HOST=seu_host_postgres
DB_PORT=5432
DB_NAME=store_coverage
DB_USER=seu_usuario
DB_PASSWORD=sua_senha

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 2. Instalação

1. Instale as dependências:
```bash
pip3 install -r requirements.txt
```

2. Execute a API:
```bash
uvicorn main:app --reload
```

A API estará disponível em `http://127.0.0.1:8000/`

**Nota**: O banco de dados PostgreSQL deve estar configurado e a tabela `company_delivery_map` deve existir com os dados de mapas KML/KMZ.

## Uso da API

### Endpoint POST: `/check-coverage`

```bash
curl -X POST "http://localhost:8000/check-coverage" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -23.5450,
    "longitude": -46.6350,
    "company_id": 1
  }'
```

O campo store_id pode ser enviado opcionalmente para verificar se naquela loja específica a coordenada está coberta. Se não vamos retornar a primeira loja na company que cobre a coordenada.


### Parâmetros

- `latitude` (obrigatório): Latitude da coordenada
- `longitude` (obrigatório): Longitude da coordenada  
- `company_id` (obrigatório): UUID da empresa
- `store_id` (opcional): UUID da loja específica para verificar

### Respostas

**Sucesso (200)**:
```json
{
  "store_id": "550e8400-e29b-41d4-a716-446655440000",
  "region_name": "Centro São Paulo",
  "company_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Não encontrado (404)**:
```json
{
  "detail": "Location not covered by any store"
}
```

## Estrutura do Banco de Dados

Tabela `company_delivery_map`:
- `id`: ID único da região (SERIAL)
- `company_id`: UUID da empresa
- `store_id`: UUID da loja (pode ser NULL)
- `type`: Tipo do arquivo ('kml' ou 'kmz')
- `region_name`: Nome da região
- `file_path`: Caminho para o arquivo de mapa
- `status`: Status ativo (1) ou inativo (0)
- `created_at`: Timestamp de criação

## Documentação da API

Acesse `http://localhost:8000/docs` para a documentação interativa do Swagger.
