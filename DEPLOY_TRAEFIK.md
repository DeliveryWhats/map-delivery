# Deploy da Store Coverage API com Traefik

Este guia explica como fazer o deploy da API no seu ambiente Docker Swarm com Traefik.

## 🚀 Deploy no seu ambiente

### 1. Build da imagem localmente

```bash
# Fazer build da imagem
./build-local.sh
```

### 2. Deploy no Docker Swarm

```bash
# Deploy usando docker-compose.yml
docker stack deploy -c docker-compose.yml store-coverage-stack

# Ou usando o arquivo específico para Traefik
docker stack deploy -c docker-compose.traefik.yml store-coverage-stack
```

### 3. Verificar o deploy

```bash
# Verificar serviços
docker service ls

# Verificar logs
docker service logs store-coverage-stack_store-coverage-api -f
```

## 🌐 Acesso

A API estará disponível em:
- **URL**: `https://map.zibb.com.br`
- **Docs**: `https://map.zibb.com.br/docs`
- **Health Check**: `https://map.zibb.com.br/`

## 🔧 Configuração Traefik

O arquivo `docker-compose.yml` já está configurado com:

- **Host**: `map.zibb.com.br`
- **HTTPS**: Certificado SSL automático via Let's Encrypt
- **Redirecionamento**: www.map.zibb.com.br → map.zibb.com.br
- **Network**: `network_public` (mesmo do seu site)
- **Porta**: 8000 (interna do container)

## 📋 Labels Traefik configuradas

```yaml
labels:
  - traefik.enable=true
  - traefik.http.routers.store-coverage-api.rule=Host(`map.zibb.com.br`)
  - traefik.http.routers.store-coverage-api.entrypoints=websecure
  - traefik.http.routers.store-coverage-api.tls.certresolver=letsencryptresolver
  - traefik.http.routers.store-coverage-api.priority=1
  - traefik.http.routers.store-coverage-api.service=store-coverage-api
  - traefik.http.services.store-coverage-api.loadbalancer.server.port=8000
```

## 🧪 Teste da API

```bash
curl --location 'https://map.zibb.com.br/check-coverage' \
--header 'Content-Type: application/json' \
--data '{
    "latitude": -19.980325789089846, 
    "longitude": -43.94391134478284,
    "company_id": "3d507d03-28eb-4736-a365-ba6b1af174b0"
}'
```

## 🔄 Atualização

Para atualizar a API:

```bash
# 1. Fazer build da nova versão
./build-local.sh

# 2. Atualizar o stack
docker service update --image victorsorroche/store-coverage-api:latest store-coverage-stack_store-coverage-api
```

## 🛠️ Troubleshooting

### Verificar se o serviço está rodando
```bash
docker service ps store-coverage-stack_store-coverage-api
```

### Verificar logs
```bash
docker service logs store-coverage-stack_store-coverage-api -f
```

### Verificar network
```bash
docker network ls | grep network_public
```

### Remover stack (se necessário)
```bash
docker stack rm store-coverage-stack
```

## 📁 Arquivos importantes

- `docker-compose.yml` - Configuração principal com Traefik
- `docker-compose.traefik.yml` - Versão com credenciais hardcoded
- `build-local.sh` - Script para build local
- `Dockerfile` - Definição da imagem Docker
