# YouTube Analytics Dashboard

## Visão Geral
Aplicação Django para análise de dados do YouTube, incluindo dashboard de analytics, análise de sentimentos de comentários, e gestão de assinaturas.

## Estrutura do Projeto
```
├── accounts/          # App de autenticação e usuários
│   ├── models.py      # CustomUser model
│   ├── views.py       # Login, registro, settings
│   └── templates/     # Templates de autenticação
├── analytics/         # App principal de analytics
│   ├── models.py      # Profile model
│   ├── views.py       # Dashboard e análise de sentimentos
│   ├── youtube_service.py  # Integração com YouTube API
│   └── templates/     # Templates do dashboard
├── core/              # App de páginas públicas
│   └── templates/     # Landing page, planos
├── subscriptions/     # App de assinaturas
│   └── models.py      # Plan, Subscription, Payment
├── config/            # Configurações do Django
│   └── settings.py    # Configurações do projeto
├── static/            # Arquivos estáticos
├── requirements.txt   # Dependências Python
├── Procfile          # Comando de deploy (Railway/Heroku)
└── railway.json      # Configurações Railway
```

## Tecnologias Utilizadas
- Django 5.2.8
- PostgreSQL
- Google OAuth2 (social-auth-app-django)
- YouTube Data API v3
- YouTube Analytics API
- TextBlob (análise de sentimentos)
- Whitenoise (arquivos estáticos)
- Gunicorn (servidor WSGI)

## Variáveis de Ambiente Necessárias
Veja `.env.example` para lista completa:
- `SECRET_KEY` - Chave secreta do Django
- `DATABASE_URL` - URL do banco PostgreSQL
- `GOOGLE_OAUTH2_KEY` - Client ID do Google OAuth
- `GOOGLE_OAUTH2_SECRET` - Client Secret do Google OAuth
- `EMAIL_HOST_USER` - Email para envio
- `EMAIL_HOST_PASSWORD` - Senha do email

## Deploy no Railway
1. Conecte o repositório ao Railway
2. Adicione um banco PostgreSQL
3. Configure as variáveis de ambiente
4. O deploy será automático via Procfile

## Comandos Úteis
```bash
# Rodar migrações
python manage.py migrate

# Criar cache table
python manage.py createcachetable

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Rodar servidor de desenvolvimento
python manage.py runserver 0.0.0.0:5000

# Rodar servidor de produção
gunicorn config.wsgi --bind 0.0.0.0:$PORT
```

## Alterações Recentes
- 01/12/2025: Projeto preparado para deploy no Railway
  - Configurações de segurança movidas para variáveis de ambiente
  - Adicionado whitenoise para servir arquivos estáticos
  - Adicionado gunicorn para servidor de produção
  - Criado Procfile e railway.json
  - Corrigidos bugs nos modelos
