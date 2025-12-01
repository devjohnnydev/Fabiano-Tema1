# Media Scope - YouTube Analytics Dashboard

Dashboard de analytics do YouTube com análise de sentimentos de comentários e gestão de assinaturas.

## Funcionalidades

- Dashboard com métricas do YouTube (visualizações, likes, inscritos)
- Análise de sentimentos de comentários
- Login com Google OAuth2
- Gestão de assinaturas e planos
- Interface responsiva e moderna

## Tecnologias Utilizadas

- **Backend:** Django 5.2.8
- **Banco de Dados:** PostgreSQL
- **Autenticação:** Google OAuth2 (social-auth-app-django)
- **APIs:** YouTube Data API v3, YouTube Analytics API
- **Análise de Sentimentos:** TextBlob
- **Servidor de Produção:** Gunicorn
- **Arquivos Estáticos:** Whitenoise

---

# Passo a Passo para Hospedar no Railway

## Pré-requisitos

1. Conta no [Railway](https://railway.app)
2. Conta no [Google Cloud Console](https://console.cloud.google.com) com credenciais OAuth2
3. Repositório no GitHub com o código do projeto

---

## Passo 1: Preparar o Repositório

Certifique-se de que seu repositório contém os seguintes arquivos:

```
├── Procfile              # Comando de inicialização
├── railway.json          # Configurações do Railway
├── requirements.txt      # Dependências Python
├── runtime.txt           # Versão do Python
└── nixpacks.toml         # Configurações do Nixpacks
```

---

## Passo 2: Criar Projeto no Railway

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Autorize o Railway a acessar seu GitHub (se ainda não fez)
5. Selecione o repositório do projeto

---

## Passo 3: Adicionar Banco de Dados PostgreSQL

1. No painel do projeto Railway, clique em **"+ New"**
2. Selecione **"Database"** → **"Add PostgreSQL"**
3. Aguarde a criação do banco de dados
4. O Railway automaticamente criará a variável `DATABASE_URL`

---

## Passo 4: Configurar Variáveis de Ambiente

1. Clique no serviço do seu app (não no banco de dados)
2. Vá na aba **"Variables"**
3. Adicione as seguintes variáveis:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta do Django (gere uma nova) | `sua-chave-secreta-muito-longa-aqui` |
| `DEBUG` | Modo debug (False em produção) | `False` |
| `ALLOWED_HOSTS` | Domínios permitidos | `seu-app.up.railway.app` |
| `CSRF_TRUSTED_ORIGINS` | Origens confiáveis para CSRF | `https://seu-app.up.railway.app` |
| `GOOGLE_OAUTH2_KEY` | Client ID do Google OAuth | `xxxxx.apps.googleusercontent.com` |
| `GOOGLE_OAUTH2_SECRET` | Client Secret do Google OAuth | `GOCSPX-xxxxxxx` |
| `EMAIL_HOST_USER` | Email para envio (opcional) | `seu-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Senha de app do Gmail (opcional) | `xxxx xxxx xxxx xxxx` |

### Como gerar uma SECRET_KEY segura:

```python
# Execute no terminal Python:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Ou use um gerador online: https://djecrety.ir/

---

## Passo 5: Configurar Google OAuth2

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto ou selecione um existente
3. Vá em **"APIs & Services"** → **"Credentials"**
4. Clique em **"Create Credentials"** → **"OAuth client ID"**
5. Selecione **"Web application"**

### URIs de Redirecionamento (Adicionar em "Authorized redirect URIs"):

```
https://seu-app.up.railway.app/auth/complete/google-oauth2/
```

### Origens JavaScript Autorizadas (Adicionar em "Authorized JavaScript origins"):

```
https://seu-app.up.railway.app
```

7. Copie o **Client ID** e **Client Secret** para as variáveis de ambiente

### APIs necessárias para habilitar no Google Cloud:

- YouTube Data API v3
- YouTube Analytics API

---

## Passo 6: Deploy

1. O Railway fará o deploy automaticamente ao detectar as mudanças
2. Acompanhe o progresso na aba **"Deployments"**
3. Após o deploy, o Railway executará automaticamente:
   - Instalação das dependências
   - Migrações do banco de dados
   - Coleta de arquivos estáticos
   - Inicialização do servidor Gunicorn

---

## Passo 7: Obter o Domínio

1. Vá na aba **"Settings"** do serviço
2. Em **"Domains"**, clique em **"Generate Domain"**
3. Copie o domínio gerado (ex: `seu-app.up.railway.app`)
4. **IMPORTANTE:** Atualize as seguintes variáveis com o domínio correto:
   - `ALLOWED_HOSTS` 
   - `CSRF_TRUSTED_ORIGINS`
5. Atualize as URIs de redirecionamento no Google Cloud Console

---

## Passo 8: Verificar o Deploy

1. Acesse o domínio do seu app
2. Teste o login com Google
3. Verifique se o dashboard carrega corretamente

---

# Desenvolvimento Local

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/mediascope.git
cd mediascope
```

2. Crie e ative um virtualenv:
```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

3. Crie o arquivo `.env`:
```bash
SECRET_KEY=sua-secret-key-aqui
DEBUG=True
GOOGLE_OAUTH2_KEY=sua-chave-api-aqui
GOOGLE_OAUTH2_SECRET=sua-chave-secreta-aqui
DB_NAME=MediaScope
DB_USER=postgres
DB_PASSWORD=sua-senha-aqui
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=your-email-here
EMAIL_HOST_PASSWORD=your-password-here
```

4. Instale dependências:
```bash
pip install -r requirements.txt
```

5. Configure o banco de dados:
```bash
python manage.py migrate
python manage.py createcachetable
```

6. Rode o servidor:
```bash
python manage.py runserver 0.0.0.0:5000
```

---

## Comandos Úteis

```bash
# Rodar migrações
python manage.py migrate

# Criar tabela de cache
python manage.py createcachetable

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Rodar servidor de desenvolvimento
python manage.py runserver 0.0.0.0:5000

# Criar superusuário
python manage.py createsuperuser
```

---

## Estrutura do Projeto

```
├── accounts/          # App de autenticação e usuários
├── analytics/         # App principal de analytics
├── core/              # App de páginas públicas (landing, planos)
├── subscriptions/     # App de assinaturas
├── config/            # Configurações do Django
├── static/            # Arquivos estáticos (CSS, JS, imagens)
├── staticfiles/       # Arquivos estáticos coletados (produção)
├── manage.py          # Utilitário do Django
├── requirements.txt   # Dependências Python
├── Procfile           # Comando de produção
├── railway.json       # Configurações Railway
├── nixpacks.toml      # Configurações Nixpacks
└── runtime.txt        # Versão do Python
```

---

## Troubleshooting (Solução de Problemas)

### Erro: "CSRF verification failed"
- Verifique se `CSRF_TRUSTED_ORIGINS` contém a URL correta do seu app
- O formato deve ser: `https://seu-app.up.railway.app`

### Erro: "Invalid redirect_uri"
- Atualize as URIs de redirecionamento no Google Cloud Console
- A URI deve ser: `https://seu-app.up.railway.app/auth/complete/google-oauth2/`

### Arquivos estáticos não carregam
- Verifique se `whitenoise` está instalado e configurado no `MIDDLEWARE`
- Execute `python manage.py collectstatic --noinput`

### Erro de banco de dados
- Verifique se o PostgreSQL está conectado ao serviço
- Verifique se `DATABASE_URL` está configurado nas variáveis

### Erro: "DisallowedHost"
- Adicione o domínio correto em `ALLOWED_HOSTS`

---

## Boas Práticas

- Nunca versionar o `.env` com chaves reais
- Use variáveis de ambiente para credenciais
- Mantenha o `DEBUG=False` em produção
- Implemente logs para monitorar erros

---

## Licença

Este projeto é privado e de uso exclusivo do proprietário.
