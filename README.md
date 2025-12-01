# MediaScope — Plataforma de Análise de Dados do YouTube

**Resumo**
MediaScope é uma plataforma para coletar, processar e visualizar métricas de canais e vídeos do YouTube, construída em Python utilizando a biblioteca oficial do Google para acesso à YouTube Data API. Esta versão foi entregue como um repositório com scripts de coleta, serviços e uma interface/ou scripts para análise.

---

## Índice
- [Resumo](#resumo)
- [Funcionalidades](#funcionalidades)
- [Stack e Dependências](#stack-e-dependências)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Instalação](#instalação)
- [Configuração (API Keys e .env)](#configuração-api-keys-e-env)
- [Como rodar](#como-rodar)
- [Como a YouTube Data API é utilizada](#como-a-youtube-data-api-é-utilizada)
- [Banco de dados](#banco-de-dados)
- [Melhorias futuras](#melhorias-futuras)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## Funcionalidades
- Coleta de estatísticas de vídeos e canais (views, likes, comentários, inscritos, metadata).
- Agendamento de coleta periódica (cron / scheduler).
- Exportação de dados para CSV/Excel.
- Dashboards / visualizações (pode incluir scripts para gerar gráficos com Plotly/Matplotlib).
- Relatórios automatizados (opcional).

---

## Stack e Dependências
- Python 3.11.8
- google-api-python-client (YouTube Data API)
- requests
- pandas 
- Dependências listadas em `requirements.txt`

> Verifique `requirements.txt` para a lista completa de pacotes e versões.

---

## Estrutura sugerida do repositório 

```
/mnt/data/Project_MediaScope_Senai-dash
```

Arquivos detectados: 64 (amostra incluída no rascunho de documentação entregue).

Pastas e arquivos importantes:
- `config/` — configurações do projeto
- `accounts/`, `analytics/`, `core/`, `subscriptions/` - aplicativos
- `requirements.txt` — dependências Python
- `README.md` original (presente no repositório)
- `.env` ou similar — variáveis de ambiente exemplo


---

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Fabinhonhou/MediaScope.git
cd MediaScope
# caso esteja em outra branch, use o comando git checkout nome-da-branch
# nesse caso, a branch está como dash
git checkout dash
```

2. Crie e ative um virtualenv (recomendado):
```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate    # Windows (PowerShell)
```
3. Crie o arquivo `.env`  (explicação de como obter a api key do youtube e a de Auth logo depois desse passo a passo )
```bash
SECRET_KEY = 'sua-secret-key-aqui'

YOUTUBE_API_KEY='sua-chave-api-aqui'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'sua-chave-api-de-autentição-aqui'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'sua-chave-secreta-de-autenticação-aqui'

DB_NAME='MediaScope'
DB_USER='postgres'
DB_PASSWORD='sua-senha-aqui'
DB_HOST='localhost'
DB_PORT='5432'

EMAIL_HOST_USER=your-email-here
EMAIL_HOST_PASSWORD=your-password-here
``` 

4. Instale dependências:
```bash
pip install -r requirements.txt
```

5. Crie o banco de dados:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable
```

---
## Configurações da API KEY do Youtube e do Google Auth

Como obter a API Key do YouTube:
1. Acesse o console do Google Cloud (https://console.cloud.google.com/).
2. Crie um novo projeto (ou use um existente).
3. Habilite a API "YouTube Data API v3".
4. Vá em "Credenciais" e crie uma API Key.
5. Cole a chave em `YOUTUBE_API_KEY` no seu `.env`.

Como obter a API Key e Secret do Google Auth:
1. Acesse o console do Google Cloud (https://console.cloud.google.com/).
2. Crie um novo projeto (ou use um existente).
3. Habilite a API "Google Identity and Access Management".
4. Vá em "Credenciais" e crie uma.
5. Selecione em "Criar Credenciais" a opção "ID do cliente OAuth 2.0".
6. Selecione "Aplicação Web"
7. Não feche a aba das chaves, copie a Key e cole em `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`
8. Copie o Secret Key e cole em `SOCIAL_AUTH_GOOGLE_OAUTH2_ SECRET`
9. Feche a aba das chaves e reproduza os próximos passos.
10. Adicione em "Origens JavaScript autorizadas" as seguintes URLS (separadas)
1 http://127.0.0.1:8000
2 http://localhost:8000
11. Adicione em "URIs de redirecionamento autorizados" as seguintes URLS (separadas)
1 http://127.0.0.1:8000/oauth/complete/google-oauth2/
2 http://localhost:8000/oauth/complete/google-oauth2/
3 http://127.0.0.1:8000/social/complete/google-oauth2/
4 http://localhost:8000/social/complete/google-oauth2/
5 http://localhost:8000/auth/complete/google-oauth2/
6 http://127.0.0.1:8000/auth/complete/google-oauth2/
7 http://127.0.0.1:8000/auth/complete/google-oauth2/flowName=GeneralOAuthFlow
12. Clique em "Salvar" no final da página.


---

## Como rodar

No terminal, verifique se a venv(ambiente virtual) está ativa e verifique se você está na pasta do projeto.
E então, rode o comando 
```bash
python manage.py runserver
```
esse comando vai iniciar o servidor, que rodara na porta http://127.0.0.1:8000/


---

## Scripts úteis (exemplos)
- `scripts/collect_data.py` — coleta dados da YouTube Data API e grava no banco.
- `scripts/update_metrics.py` — atualiza métricas históricas.
- `scripts/export_csv.py` — exporta dados em CSV/Excel.
- `scripts/run_scheduler.py` — roda um agendador (APScheduler / cron wrapper).

> Consulte os scripts reais no diretório `scripts/` para confirmações de nomes e parâmetros.

---

## Como a YouTube Data API é utilizada
O repositório traz detecções de uso da biblioteca `googleapiclient` / chamadas à YouTube API. Exemplo de uso típico:

```python
from googleapiclient.discovery import build
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

request = youtube.videos().list(part="snippet,statistics,contentDetails", id=VIDEO_ID)
response = request.execute()
```

A documentação do Google (YouTube Data API v3) é a referência para parâmetros e quotas. Lembre-se de tratar quotas e implementar retries/backoff para chamadas em lote.

---

## Banco de dados
PostgreSQL

---

## Boas práticas e observações
- Nunca versionar o `.env` com chaves reais.
- Use variáveis de ambiente para credenciais.
- Trate e registre erros de chamadas à API (logs).
- Implemente paginação e controle de rate-limits.
- Centralize chamadas à API em um módulo/service para facilitar testes e mocking.

---

## Melhorias futuras
- Implementar análise de sentimento dos comentários (NLP).
- Dashboard web completo (React/Vue/Plotly Dash).
- Agendamento robusto (Celery/RabbitMQ ou APScheduler com supervisão).
- Monitor de quota da API e alertas.
- Históricos detalhados e projeções de crescimento.

---

## Contribuição
Sinta-se à vontade para abrir issues e pull requests. Use o padrão de commits e inclua testes para novas funcionalidades.

---

## Licença
Adicione aqui a licença do projeto (por exemplo, MIT). Se não houver, recomendo `MIT` para projetos open-source.

---

## Contato
Para dúvidas sobre a documentação gerada, ou para que eu gere o README finalizado com exemplos extraídos automaticamente do código (endpoints, amostras de payloads, esquema do BD), responda com **"Gerar automático com extração de endpoints e modelos"**.

