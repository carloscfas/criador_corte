# Criador de Cortes - Geração Automática de Shorts

Plataforma SaaS baseada em Inteligência Artificial que recebe vídeos longos (principalmente podcasts) e gera automaticamente Shorts para YouTube, TikTok e Instagram.

## 🚀 Funcionalidades

- **Upload de Vídeos**: Upload de vídeos longos com barra de progresso
- **Extração de Áudio**: Extração automática com FFmpeg
- **Transcrição**: Transcrição com Whisper (timestamps por palavra)
- **Análise IA**: Análise com OpenAI GPT-4o para encontrar melhores momentos
- **Score de Viralização**: Sistema de pontuação (0-100) baseado em emoção, curiosidade, retenção
- **Geração de Cortes**: Cortes inteligentes com buffer de 8 segundos
- **Legendas Automáticas**: SRT, ASS (karaokê), highlight
- **Reconhecimento Facial**: Rastreamento de falante e zoom inteligente
- **Dashboard**: Estatísticas completas e métricas
- **Exportação**: Exportação em formato 9:16 (1080x1920, 60fps)
- **SEO**: Geração automática de títulos, descrições e hashtags
- **Publicação**: Integração placeholder para YouTube, TikTok, Instagram

## 🛠 Stack Tecnológica

### Backend
- **Python 3.13+**
- **FastAPI**: Framework web assíncrono
- **SQLAlchemy**: ORM para PostgreSQL
- **Alembic**: Migrations do banco de dados
- **PostgreSQL**: Banco de dados relacional
- **Redis**: Broker para Celery
- **Celery**: Processamento assíncrono
- **FFmpeg**: Processamento de vídeo
- **Whisper**: Transcrição de áudio
- **OpenAI GPT-4o**: Análise de conteúdo e SEO
- **OpenCV**: Reconhecimento facial
- **Docker**: Containerização

### Frontend
- **React 18**
- **TypeScript**
- **Vite**: Build tool
- **TailwindCSS**: Estilização
- **Shadcn UI**: Componentes UI
- **TanStack Query**: Gerenciamento de dados
- **React Router**: Navegação
- **Axios**: Cliente HTTP
- **Lucide React**: Ícones

## 📁 Estrutura do Projeto

```
Criador-Cortes/
├── backend/
│   ├── app/
│   │   ├── api/              # Rotas FastAPI
│   │   ├── core/             # Configurações, segurança
│   │   ├── models/           # Models SQLAlchemy
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── repositories/     # Repository Pattern
│   │   ├── services/         # Lógica de negócio
│   │   ├── workers/          # Celery tasks
│   │   ├── ai/               # Serviços de IA
│   │   ├── video/            # Processamento de vídeo
│   │   ├── database/         # Configurações do DB
│   │   └── utils/            # Helpers
│   ├── alembic/              # Migrations
│   ├── tests/                # Testes
│   ├── requirements.txt      # Dependências Python
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── pages/            # Páginas
│   │   ├── services/         # API calls
│   │   ├── hooks/            # Custom hooks
│   │   ├── contexts/         # React contexts
│   │   ├── types/            # TypeScript types
│   │   └── lib/              # Utilitários
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml        # Orquestração
└── README.md
```

## 🏗 Arquitetura

O projeto segue **Clean Architecture** com separação clara de responsabilidades:

- **api/**: Controllers (rotas FastAPI)
- **services/**: Lógica de negócio
- **repositories/**: Acesso ao banco de dados (Repository Pattern)
- **models/**: Entidades do banco de dados
- **schemas/**: DTOs (Pydantic)
- **workers/**: Tasks assíncronas (Celery)

## 🚀 Como Rodar

### Pré-requisitos

- Docker e Docker Compose
- Python 3.13+
- Node.js 20+
- OPENAI_API_KEY (para análise e SEO)

### 1. Configurar Variáveis de Ambiente

```bash
cd backend
cp .env.example .env
```

Edite o `.env` com suas credenciais:
```
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/criador_cortes
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=your-openai-api-key
```

### 2. Iniciar Serviços com Docker Compose

```bash
cd /home/carlos/Documentos/Criador-Cortes
docker-compose up -d
```

Isso iniciará:
- PostgreSQL (porta 5432)
- Redis (porta 6379)
- Backend FastAPI (porta 8000)
- Celery Worker
- Frontend (porta 5173)

### 3. Rodar Migrations do Banco de Dados

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Instalar Dependências do Frontend (Desenvolvimento Local)

```bash
cd frontend
npm install
npm run dev
```

### 5. Acessar a Aplicação

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

## 📡 API Endpoints

### Autenticação
- `POST /auth/register` - Criar conta
- `POST /auth/login` - Fazer login
- `GET /auth/me` - Obter usuário atual

### Projetos
- `POST /projects/` - Criar projeto
- `GET /projects/` - Listar projetos do usuário
- `GET /projects/{id}` - Obter projeto
- `PUT /projects/{id}` - Atualizar projeto
- `DELETE /projects/{id}` - Deletar projeto

### Vídeos
- `POST /videos/upload/{project_id}` - Upload de vídeo
- `GET /videos/{id}` - Obter vídeo
- `GET /status/video/{id}` - Status do processamento

### Clips
- `GET /clips/video/{video_id}` - Listar clips de um vídeo
- `GET /clips/{id}` - Obter clip
- `PUT /clips/{id}` - Atualizar clip
- `POST /clips/{id}/approve` - Aprovar clip

### Dashboard
- `GET /dashboard/` - Estatísticas do usuário

### Exportação
- `POST /export/` - Criar job de exportação
- `GET /export/job/{id}` - Status do job
- `GET /export/clip/{clip_id}` - Jobs de um clip

### Redes Sociais
- `POST /social/publish` - Publicar em redes sociais
- `GET /social/requirements` - Requisitos de publicação

## 🔧 Configuração

### Backend

As configurações ficam em `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    OPENAI_API_KEY: Optional[str]
    # ...
```

### Frontend

As configurações ficam em `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

## 🧪 Testes

```bash
cd backend
pytest
pytest --cov=app
```

## 📊 Fluxo do Sistema

1. **Upload**: Usuário envia vídeo
2. **Processamento**: Celery extrai áudio
3. **Transcrição**: Whisper transcreve o áudio
4. **Análise**: OpenAI analisa a transcrição
5. **Geração**: Clips são gerados com scores
6. **Exportação**: Usuário aprova e exporta
7. **Publicação**: Opcionalmente publica em redes sociais

## 🔐 Segurança

- Senhas hashadas com BCrypt
- Tokens JWT com expiração
- CORS configurado
- Validação de entrada com Pydantic
- Rate limiting (recomendado para produção)

## 🚀 Deploy

### Produção

Para deploy em produção, siga o guia completo em [DEPLOYMENT.md](./DEPLOYMENT.md).

#### Resumo Rápido:

1. **Configurar variáveis de ambiente**
   ```bash
   cp backend/.env.example .env
   # Edite .env com suas credenciais reais
   ```

2. **Configurar SSL/HTTPS**
   ```bash
   # Usar Let's Encrypt ou certificados próprios
   mkdir ssl
   # Copiar certificados para ssl/cert.pem e ssl/key.pem
   ```

3. **Atualizar configurações**
   - Adicionar seu domínio em `backend/app/core/config.py` (CORS_ORIGINS)
   - Atualizar `nginx.conf` com seu domínio

4. **Deploy**
   ```bash
   docker compose -f docker-compose.prod.yml build
   docker compose -f docker-compose.prod.yml up -d
   docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

#### Requisitos de Produção:
- **CPU**: 4+ cores (8+ recomendado)
- **RAM**: 8GB+ (16GB+ recomendado)
- **Storage**: 50GB+ SSD
- **GEMINI_API_KEY**: Obrigatório
- **Domínio com SSL**: Recomendado

#### Serviços em Produção:
- PostgreSQL com persistência
- Redis com persistência
- Backend FastAPI (4 workers)
- Celery Worker (4 workers)
- Celery Beat (para tarefas agendadas)
- Frontend (Nginx servindo build otimizado)
- Nginx (proxy reverso com rate limiting)

## 📝 Próximos Passos

- [ ] Implementar testes unitários e de integração
- [ ] Configurar CI/CD (GitHub Actions)
- [ ] Adicionar rate limiting
- [ ] Implementar cache com Redis
- [ ] Adicionar monitoramento (Sentry, Prometheus)
- [ ] Implementar integração real com APIs de redes sociais
- [ ] Adicionar suporte a múltiplos idiomas
- [ ] Implementar WebSocket para progresso em tempo real
- [ ] Adicionar sistema de notificações
- [ ] Implementar plano de assinatura e pagamentos

## 📄 Licença

Este projeto é privado e confidencial.

## 👥 Suporte

Para suporte, entre em contato com a equipe de desenvolvimento.
