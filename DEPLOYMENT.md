# Deployment Guide - Criador de Cortes

## Pré-requisitos de Produção

### Requisitos Mínimos de Servidor
- **CPU**: 4+ cores (8+ recomendado para processamento de vídeo)
- **RAM**: 8GB+ (16GB+ recomendado)
- **Storage**: 50GB+ SSD (depende do volume de vídeos)
- **GPU**: Opcional mas altamente recomendado para Whisper/IA

### Software Necessário
- Docker 24.0+
- Docker Compose 2.0+
- OpenSSL (para gerar chaves)
- Domínio configurado com DNS

### Serviços Externos Obrigatórios
- **GEMINI_API_KEY**: Para análise de IA
- **Servidor de emails** (opcional): Para notificações

## Configuração de Produção

### 1. Configurar Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto:

```bash
# Database
POSTGRES_USER=sua_usuario_seguro
POSTGRES_PASSWORD=sua_senha_muito_segura_32_chars
POSTGRES_DB=criador_cortes
POSTGRES_PORT=5432

# Redis
REDIS_PORT=6379

# Security
SECRET_KEY=$(openssl rand -hex 32)

# AI APIs
GEMINI_API_KEY=sua_gemini_api_key

# Environment
ENVIRONMENT=production

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### 2. Configurar SSL/HTTPS

#### Opção A: Let's Encrypt (Recomendada)

```bash
# Instalar certbot
sudo apt-get install certbot

# Gerar certificados
sudo certbot certonly --standalone -d seu-dominio.com

# Copiar certificados para o projeto
mkdir ssl
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem ssl/key.pem
sudo chmod 644 ssl/*.pem
```

#### Opção B: Certificados Auto-assinados (Apenas para teste)

```bash
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem
```

### 3. Atualizar nginx.conf para HTTPS

Descomente e configure a seção HTTPS em `nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name seu-dominio.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... location blocks
}
```

### 4. Configurar CORS

Atualize `backend/app/core/config.py` para incluir seu domínio:

```python
CORS_ORIGINS: list = [
    "https://seu-dominio.com",
    "https://www.seu-dominio.com"
]
```

## Deploy

### 1. Build e Iniciar Serviços

```bash
# Build das imagens
docker compose -f docker-compose.prod.yml build

# Iniciar serviços
docker compose -f docker-compose.prod.yml up -d

# Verificar status
docker compose -f docker-compose.prod.yml ps
```

### 2. Rodar Migrations

```bash
# Entrar no container backend
docker compose -f docker-compose.prod.yml exec backend bash

# Rodar migrations
alembic upgrade head

# Sair do container
exit
```

### 3. Verificar Logs

```bash
# Logs de todos os serviços
docker compose -f docker-compose.prod.yml logs -f

# Logs específicos
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f celery_worker
```

## Monitoramento e Manutenção

### Verificar Saúde dos Serviços

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend health check
curl http://localhost:3000/health
```

### Backup do Banco de Dados

```bash
# Backup manual
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U admin criador_cortes > backup_$(date +%Y%m%d).sql

# Backup automatizado (adicionar ao crontab)
0 2 * * * cd /path/to/project && docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U admin criador_cortes > /backups/db_$(date +\%Y\%m\%d).sql
```

### Limpeza de Arquivos Temporários

```bash
# Limpar arquivos de uploads antigos (mais de 30 dias)
find uploads/ -type f -mtime +30 -delete

# Limpar logs do Docker
docker system prune -a --volumes -f
```

## Escalabilidade

### Aumentar Workers do Celery

Edite `docker-compose.prod.yml`:

```yaml
celery_worker:
  command: celery -A app.workers.celery_app worker --loglevel=info --concurrency=8
```

### Configurar Balanceamento de Carga

Para múltiplas instâncias do backend:

```yaml
backend:
  deploy:
    replicas: 3
```

### Usar Serviços Gerenciados

Para produção em escala, considere substituir:

- **PostgreSQL**: RDS, Neon, Supabase
- **Redis**: ElastiCache, Upstash, Redis Cloud
- **Storage**: S3, GCS, Cloudflare R2
- **CDN**: Cloudflare, CloudFront

## Segurança

### Firewall

```bash
# Permitir apenas portas necessárias
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### Atualizações de Segurança

```bash
# Atualizar imagens Docker
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# Atualizar sistema operacional
sudo apt update && sudo apt upgrade -y
```

### Monitoramento

Considere adicionar:

- **Sentry**: Para error tracking
- **Prometheus + Grafana**: Para métricas
- **Uptime monitoring**: UptimeRobot, Pingdom

## Troubleshooting

### Serviços não iniciam

```bash
# Verificar logs
docker compose -f docker-compose.prod.yml logs

# Reconstruir imagens
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### Problemas com GPU

Se tiver GPU NVIDIA, instale nvidia-docker:

```bash
# Adicionar suporte GPU ao docker-compose
# Adicionar --gpus all ao serviço backend/celery_worker
```

### Alto uso de memória

```bash
# Limitar memória dos containers
# Adicionar ao docker-compose.prod.yml:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G
```

## Rollback

Se algo der errado:

```bash
# Parar serviços
docker compose -f docker-compose.prod.yml down

# Voltar para versão anterior
git checkout <commit-hash>

# Rebuild e restart
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

## CI/CD (Opcional)

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/Criador-Cortes
            git pull origin main
            docker compose -f docker-compose.prod.yml build
            docker compose -f docker-compose.prod.yml up -d
```

## Suporte

Para problemas de deployment, verifique:
1. Logs dos containers
2. Recursos do servidor (CPU, RAM, Disk)
3. Conectividade de rede
4. Configurações de firewall
