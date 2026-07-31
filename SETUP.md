# Guia de Setup - Criador de Cortes

## Pré-requisitos

- Docker e Docker Compose instalados
- OPENAI_API_KEY (obter em https://platform.openai.com/api-keys)
- Git

## Configuração Inicial

### 1. Clonar o Repositório

```bash
cd /home/carlos/Documentos/Criador-Cortes
```

### 2. Configurar Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto:

```bash
cp backend/.env.example backend/.env
```

Edite o `backend/.env` com suas credenciais:

```env
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/criador_cortes
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**IMPORTANTE**: Substitua `your-secret-key-change-in-production` por uma chave secreta forte e adicione sua `OPENAI_API_KEY`.

### 3. Criar Diretório de Uploads

```bash
mkdir -p uploads
mkdir -p uploads/audio
mkdir -p uploads/exports
mkdir -p uploads/processed
mkdir -p uploads/subtitles
```

### 4. Iniciar Serviços com Docker Compose

```bash
docker-compose up -d --build
```

Isso iniciará:
- PostgreSQL (porta 5432)
- Redis (porta 6380)
- Backend FastAPI (porta 8001)
- Celery Worker
- Frontend (porta 5174)

### 5. Verificar Status dos Serviços

```bash
docker-compose ps
```

Todos os serviços devem estar com status "Up".

### 6. Verificar Logs (se necessário)

```bash
# Ver todos os logs
docker-compose logs -f

# Ver logs específicos
docker-compose logs backend
docker-compose logs celery_worker
docker-compose logs frontend
```

## Acesso à Aplicação

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8001
- **Swagger Docs**: http://localhost:8001/docs

## Primeiro Uso

### 1. Criar Conta

1. Acesse http://localhost:5174
2. Clique em "Não tem uma conta? Cadastre-se"
3. Preencha email, senha e nome completo
4. Clique em "Criar Conta"

### 2. Fazer Login

1. Após criar a conta, faça login
2. Você será redirecionado para o Dashboard

### 3. Criar Projeto

1. Vá para a página "Projetos"
2. Clique em "Novo Projeto"
3. Dê um nome ao projeto
4. Clique em criar

### 4. Upload de Vídeo

1. Acesse o projeto criado
2. Clique em "Upload Vídeo"
3. Selecione um arquivo de vídeo (mp4, mov, avi, mkv, webm)
4. Aguarde o processamento

### 5. Processamento

O sistema irá automaticamente:
1. Extrair o áudio do vídeo
2. Transcrever com Whisper
3. Analisar com OpenAI GPT-4o
4. Gerar clips com scores de viralização

### 6. Aprovar e Exportar Clips

1. Vá para a página "Clips"
2. Revise os clips gerados
3. Aprove os clips que deseja exportar
4. Exporte em formato 9:16 para redes sociais

## Troubleshooting

### Serviços não iniciam

```bash
# Parar tudo
docker-compose down

# Remover volumes (cuidado: apaga dados)
docker-compose down -v

# Rebuild e iniciar
docker-compose up -d --build
```

### Erro de conexão com banco de dados

```bash
# Verificar se PostgreSQL está saudável
docker-compose ps postgres

# Ver logs do PostgreSQL
docker-compose logs postgres
```

### Erro de OPENAI_API_KEY

Verifique se a variável está configurada no `backend/.env` e no `docker-compose.yml`.

### Whisper não funciona

O Whisper precisa de PyTorch. Se houver erro de dependência:

```bash
# Rebuild do backend
docker-compose build backend
docker-compose up -d backend
```

### Frontend não acessível

Verifique se o proxy está configurado corretamente em `frontend/vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8001',
    changeOrigin: true,
  },
}
```

## Estrutura de Portas

| Serviço | Porta Externa | Porta Interna |
|---------|---------------|---------------|
| PostgreSQL | 5432 | 5432 |
| Redis | 6380 | 6379 |
| Backend | 8001 | 8000 |
| Frontend | 5174 | 5173 |

## Parar Serviços

```bash
docker-compose down
```

## Desenvolvimento

### Backend (Local)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend (Local)

```bash
cd frontend
npm install
npm run dev
```

## Próximos Passos

- Configurar HTTPS para produção
- Implementar integração real com APIs de redes sociais
- Adicionar sistema de pagamentos
- Configurar monitoramento (Sentry, Prometheus)
- Implementar WebSocket para progresso em tempo real

## Suporte

Para problemas técnicos, verifique os logs dos containers:
```bash
docker-compose logs -f [nome_do_serviço]
```
