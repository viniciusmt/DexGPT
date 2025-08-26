# Guia de Deploy - DexGPT no Render

Este guia passo a passo mostra como fazer o deploy do DexGPT no Render para uso com GPTs personalizados.

## Pré-requisitos

1. **Conta no GitHub**: Para hospedar o código
2. **Conta no Render**: Para fazer o deploy da aplicação
3. **Credenciais do Google**: Service Account com acesso ao GA4 e Search Console

## Passo 1: Configurar o Repositório GitHub

1. Faça upload do projeto DexGPT para um repositório no GitHub
2. Certifique-se de que todos os arquivos estão incluídos:
   - `app.py`
   - `openapi.json`
   - `requirements.txt`
   - `render.yaml`
   - `README.md`
   - Pasta `agents/` com os módulos Python

## Passo 2: Obter Credenciais do Google

### 2.1 Criar Projeto no Google Cloud
1. Acesse o [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto ou selecione um existente
3. Anote o ID do projeto

### 2.2 Ativar APIs necessárias
1. Vá para "APIs & Services" > "Library"
2. Ative as seguintes APIs:
   - **Google Analytics Data API** (GA4)
   - **Google Search Console API**

### 2.3 Criar Service Account
1. Vá para "APIs & Services" > "Credentials"
2. Clique em "Create Credentials" > "Service Account"
3. Preencha o nome (ex: "dex-analytics-service")
4. Anote o email da service account criada

### 2.4 Gerar Chave JSON
1. Clique na service account criada
2. Vá na aba "Keys"
3. Clique "Add Key" > "Create new key" > "JSON"
4. Baixe o arquivo JSON - **GUARDE COM SEGURANÇA**

### 2.5 Configurar Permissões
1. **Para GA4**: 
   - Acesse o Google Analytics
   - Vá em "Admin" > "Account Access Management"
   - Adicione o email da service account como "Viewer"
   
2. **Para Search Console**:
   - Acesse o Google Search Console
   - Para cada propriedade, vá em "Settings" > "Users and permissions"
   - Adicione o email da service account como "Full" user

## Passo 3: Deploy no Render

### 3.1 Conectar Repositório
1. Acesse [Render.com](https://render.com)
2. Clique em "New" > "Web Service"
3. Conecte sua conta GitHub
4. Selecione o repositório do DexGPT

### 3.2 Configurar o Service
1. **Name**: `dex-analytics-gpt` (ou nome de sua escolha)
2. **Region**: Escolha a região mais próxima
3. **Branch**: `main` (ou branch principal)
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `python app.py`

### 3.3 Configurar Variáveis de Ambiente
1. Na seção "Environment Variables", adicione:
   - **Key**: `GOOGLE_CREDENTIALS`
   - **Value**: Cole todo o conteúdo do arquivo JSON baixado (incluindo as chaves `{}`)

2. Opcionalmente, adicione:
   - **Key**: `DEBUG`
   - **Value**: `false`

### 3.4 Deploy
1. Clique em "Create Web Service"
2. Aguarde o deploy completar (pode levar alguns minutos)
3. Anote a URL gerada (ex: `https://dex-analytics-gpt.onrender.com`)

## Passo 4: Verificar o Deploy

### 4.1 Teste Básico
1. Acesse a URL da aplicação
2. Você deve ver uma resposta JSON com status "healthy"

### 4.2 Teste da API
```bash
# Teste endpoint de saúde
curl https://sua-url.onrender.com/

# Teste lista de contas GA4
curl https://sua-url.onrender.com/ga4/accounts

# Teste lista de sites Search Console
curl https://sua-url.onrender.com/search-console/sites
```

## Passo 5: Configurar no GPT

### 5.1 Atualizar OpenAPI
1. Abra o arquivo `openapi.json` 
2. Substitua a URL do servidor:
   ```json
   "servers": [
     {
       "url": "https://sua-url.onrender.com",
       "description": "Servidor de produção no Render"
     }
   ]
   ```

### 5.2 Importar no GPT
1. Acesse a configuração do seu GPT personalizado
2. Na seção "Actions", clique "Create new action"
3. Cole o conteúdo atualizado do `openapi.json`
4. Clique "Save"

### 5.3 Testar Integração
Teste com prompts como:
- "Liste as contas GA4 disponíveis"
- "Mostre as sessões por país nos últimos 7 dias"
- "Quais são as principais queries do meu site no Search Console?"

## Solução de Problemas

### Deploy Falha
- Verifique se `requirements.txt` está correto
- Confirme se todos os arquivos estão no repositório
- Verifique os logs no painel do Render

### Erro de Credenciais
- Confirme se o JSON está correto na variável `GOOGLE_CREDENTIALS`
- Verifique se as APIs estão ativadas no Google Cloud
- Confirme se a service account tem as permissões corretas

### API Não Responde
- Verifique se a aplicação está "Running" no Render
- Teste a URL diretamente no navegador
- Verifique os logs da aplicação no Render

### GPT Não Funciona
- Confirme se a URL no `openapi.json` está correta
- Verifique se todas as rotas estão respondendo
- Teste as chamadas API manualmente primeiro

## URLs Importantes

- **Render Dashboard**: https://dashboard.render.com
- **Google Cloud Console**: https://console.cloud.google.com
- **Google Analytics**: https://analytics.google.com
- **Google Search Console**: https://search.google.com/search-console

## Próximos Passos

Após o deploy bem-sucedido:

1. Configure monitoramento no Render (opcional)
2. Adicione domínio customizado (opcional)
3. Configure alertas para erros (opcional)
4. Documente prompts úteis para o GPT
5. Treine o GPT com exemplos de uso

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs no painel do Render
2. Consulte a documentação da API no README.md
3. Teste manualmente os endpoints problemáticos