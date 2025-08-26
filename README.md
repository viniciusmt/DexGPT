# Dex Analytics API - GPT Compatible

API otimizada para uso com GPTs personalizados, fornecendo acesso a dados do Google Analytics 4 (GA4) e Google Search Console.

## Funcionalidades

### Google Analytics 4
- **Lista de contas**: Obter todas as contas e propriedades GA4 disponíveis
- **Consultas customizadas**: Análise de dados com suporte a filtros, dimensões e métricas
- **Consultas pivot**: Análise cruzada de dimensões com tabelas pivot

### Google Search Console
- **Lista de sites**: Obter todos os sites disponíveis no Search Console
- **Consultas de dados**: Análise de performance de busca com filtros avançados
- **Verificação de propriedade**: Verificar se um site está disponível

## Endpoints da API

### Saúde da API
- `GET /` - Verificação de status da API

### Google Analytics 4
- `GET /ga4/accounts` - Lista contas e propriedades GA4
- `POST /ga4/query` - Consulta dados do GA4
- `POST /ga4/pivot` - Consulta pivot no GA4

### Google Search Console
- `GET /search-console/sites` - Lista sites disponíveis
- `POST /search-console/query` - Consulta dados do Search Console
- `POST /search-console/verify` - Verifica propriedade de site

## Configuração

### Variáveis de Ambiente
- `GOOGLE_CREDENTIALS`: JSON das credenciais da conta de serviço Google (obrigatório)
- `PORT`: Porta da aplicação (padrão: 5000)
- `DEBUG`: Modo debug (padrão: false)

### Deploy no Render

1. Faça o upload do projeto para um repositório GitHub
2. Crie um novo Web Service no Render
3. Configure a variável de ambiente `GOOGLE_CREDENTIALS` com o JSON das credenciais
4. O Render usará automaticamente o arquivo `render.yaml` para configuração

### Credenciais Google

Para usar esta API, você precisa:

1. Criar um projeto no Google Cloud Platform
2. Ativar as APIs do Google Analytics Data API e Search Console API
3. Criar uma conta de serviço e baixar o JSON das credenciais
4. Compartilhar suas propriedades GA4 e sites do Search Console com o email da conta de serviço

## Uso com GPTs

Esta API foi otimizada para uso com GPTs personalizados. O arquivo `openapi.json` contém todas as especificações necessárias para integração.

### Configuração no GPT

1. Acesse a configuração do seu GPT personalizado
2. Na seção "Actions", importe o arquivo `openapi.json`
3. Configure a URL do servidor para seu deployment no Render
4. Adicione instruções para o GPT sobre como usar a API

### Exemplos de Prompts

Para GA4:
- "Mostre as sessões por país nos últimos 7 dias"
- "Analise o comportamento dos usuários por dispositivo"
- "Crie uma tabela pivot de sessões por país e categoria de dispositivo"

Para Search Console:
- "Quais são as principais queries de busca do meu site?"
- "Mostre a performance de páginas específicas"
- "Analise o CTR por país"

## Estrutura do Projeto

```
DexGPT/
├── app.py              # Aplicação Flask principal
├── openapi.json        # Especificação OpenAPI 3.1.0
├── requirements.txt    # Dependências Python
├── render.yaml        # Configuração do Render
├── README.md          # Este arquivo
└── agents/
    ├── __init__.py
    ├── analytics.py    # Funções do Google Analytics 4
    └── search_console.py # Funções do Google Search Console
```

## Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Definir credenciais (substitua pelo seu JSON)
export GOOGLE_CREDENTIALS='{"type": "service_account", ...}'

# Executar aplicação
python app.py
```

A API estará disponível em `http://localhost:5000`

## Diferenças da Versão Original

Esta versão (2.0.0) inclui as seguintes melhorias:

1. **OpenAPI 3.1.0**: Especificação atualizada para compatibilidade total com GPTs
2. **API REST**: Interface HTTP padronizada substituindo o protocolo MCP
3. **Documentação completa**: Schemas detalhados para todas as operações
4. **Melhores práticas**: Estruturação adequada para APIs REST
5. **Deploy simplificado**: Configuração otimizada para Render
6. **Tratamento de erros**: Respostas padronizadas e logs detalhados

## Suporte

Para dúvidas ou problemas, consulte a documentação ou abra uma issue no repositório GitHub.