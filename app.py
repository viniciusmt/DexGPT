from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import sys

# Importar os módulos de agentes do projeto original
# Só importa se não estiver no modo de teste
if not os.environ.get('SKIP_GOOGLE_INIT'):
    from agents.analytics import (
        listar_contas_ga4, 
        consulta_ga4, 
        consulta_ga4_pivot,
        init_analytics_client
    )
    from agents.search_console import (
        listar_sites_search_console,
        consulta_search_console_custom,
        verificar_propriedade_site_search_console,
        init_search_console_service
    )

app = Flask(__name__)
CORS(app)

def log_info(message):
    """Log de informações."""
    print(f"[INFO] {message}", file=sys.stderr)

def log_error(message):
    """Log de erros."""
    print(f"[ERROR] {message}", file=sys.stderr)

@app.route('/', methods=['GET'])
def health_check():
    """Endpoint de saúde da API."""
    return jsonify({
        "status": "healthy",
        "message": "Dex Analytics API - GPT Compatible",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/ga4/accounts', methods=['GET'])
def get_ga4_accounts():
    """Lista contas do Google Analytics 4."""
    if os.environ.get('SKIP_GOOGLE_INIT'):
        return jsonify({"erro": "Modo de teste - Google APIs não disponíveis", "sucesso": False}), 503
    
    try:
        log_info("Solicitação para listar contas GA4")
        resultado = listar_contas_ga4()
        return jsonify(resultado)
    except Exception as e:
        log_error(f"Erro ao listar contas GA4: {str(e)}")
        return jsonify({
            "erro": f"Erro interno: {str(e)}",
            "sucesso": False
        }), 500

@app.route('/ga4/query', methods=['POST'])
def query_ga4_data():
    """Consulta dados do Google Analytics 4."""
    try:
        data = request.get_json()
        
        # Validações básicas
        if not data:
            return jsonify({
                "erro": "Dados da requisição não fornecidos",
                "sucesso": False
            }), 400
        
        property_id = data.get('property_id')
        dimensoes = data.get('dimensoes', [])
        metricas = data.get('metricas', [])
        
        if not property_id:
            return jsonify({
                "erro": "property_id é obrigatório",
                "sucesso": False
            }), 400
        
        if not dimensoes:
            return jsonify({
                "erro": "dimensoes é obrigatório",
                "sucesso": False
            }), 400
        
        if not metricas:
            return jsonify({
                "erro": "metricas é obrigatório",
                "sucesso": False
            }), 400
        
        # Parâmetros opcionais
        data_inicio = data.get('data_inicio', '7daysAgo')
        data_fim = data.get('data_fim', 'today')
        limite = data.get('limite', 100)
        filtros = data.get('filtros', [])
        
        log_info(f"Consulta GA4: {property_id}, dimensões: {dimensoes}, métricas: {metricas}")
        
        # Processar filtros se existirem
        filtro_campo = ""
        filtro_valor = ""
        filtro_condicao = "igual"
        
        if filtros and len(filtros) > 0:
            primeiro_filtro = filtros[0]
            filtro_campo = primeiro_filtro.get('campo', '')
            filtro_valor = primeiro_filtro.get('valor', '')
            filtro_condicao = primeiro_filtro.get('condicao', 'igual')
        
        # Executar consulta
        resultado_texto = consulta_ga4(
            dimensao=",".join(dimensoes),
            metrica=",".join(metricas),
            periodo=data_inicio,
            data_fim=data_fim,
            filtro_campo=filtro_campo,
            filtro_valor=filtro_valor,
            filtro_condicao=filtro_condicao,
            property_id=property_id
        )
        
        # Processar resultado para JSON estruturado
        if resultado_texto.startswith("[Erro]"):
            return jsonify({
                "erro": resultado_texto,
                "sucesso": False
            }), 500
        
        # Converter resultado texto em dados estruturados
        linhas = resultado_texto.split('\n')
        if len(linhas) < 2:
            return jsonify({
                "sucesso": True,
                "dados": [],
                "total_resultados": 0,
                "periodo": f"{data_inicio} a {data_fim}",
                "property_id": property_id
            })
        
        cabecalhos = linhas[0].split(' | ')
        dados = []
        
        for linha in linhas[1:]:
            if linha.strip():
                valores = linha.split(' | ')
                if len(valores) == len(cabecalhos):
                    registro = {}
                    for i, cabecalho in enumerate(cabecalhos):
                        registro[cabecalho] = valores[i]
                    dados.append(registro)
        
        # Criar summary para o GPT
        total_sessions = sum(int(d.get('sessions', 0)) for d in dados if 'sessions' in d)
        top_countries = dados[:10] if dados else []
        
        return jsonify({
            "sucesso": True,
            "resumo": {
                "total_sessoes": total_sessions,
                "periodo": f"{data_inicio} a {data_fim}",
                "property_id": property_id,
                "top_paises": top_countries
            },
            "dados": dados,
            "total_resultados": len(dados),
            "message": f"Consulta GA4 realizada com sucesso para {property_id}. Encontrados {len(dados)} resultados no período de {data_inicio} a {data_fim}."
        })
        
    except Exception as e:
        log_error(f"Erro na consulta GA4: {str(e)}")
        return jsonify({
            "erro": f"Erro interno: {str(e)}",
            "sucesso": False
        }), 500

@app.route('/ga4/pivot', methods=['POST'])
def query_ga4_pivot():
    """Consulta pivot no Google Analytics 4."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "erro": "Dados da requisição não fornecidos",
                "sucesso": False
            }), 400
        
        property_id = data.get('property_id')
        dimensao_principal = data.get('dimensao_principal')
        dimensao_pivot = data.get('dimensao_pivot')
        metricas = data.get('metricas', [])
        
        if not all([property_id, dimensao_principal, dimensao_pivot, metricas]):
            return jsonify({
                "erro": "property_id, dimensao_principal, dimensao_pivot e metricas são obrigatórios",
                "sucesso": False
            }), 400
        
        data_inicio = data.get('data_inicio', '7daysAgo')
        data_fim = data.get('data_fim', 'today')
        limite_linhas = data.get('limite_linhas', 30)
        filtros = data.get('filtros', [])
        
        log_info(f"Consulta GA4 Pivot: {property_id}, principal: {dimensao_principal}, pivot: {dimensao_pivot}")
        
        # Processar filtros
        filtro_campo = ""
        filtro_valor = ""
        filtro_condicao = "igual"
        
        if filtros and len(filtros) > 0:
            primeiro_filtro = filtros[0]
            filtro_campo = primeiro_filtro.get('campo', '')
            filtro_valor = primeiro_filtro.get('valor', '')
            filtro_condicao = primeiro_filtro.get('condicao', 'igual')
        
        resultado = consulta_ga4_pivot(
            dimensao=dimensao_principal,
            dimensao_pivot=dimensao_pivot,
            metrica=",".join(metricas),
            periodo=data_inicio,
            data_fim=data_fim,
            filtro_campo=filtro_campo,
            filtro_valor=filtro_valor,
            filtro_condicao=filtro_condicao,
            limite_linhas=limite_linhas,
            property_id=property_id
        )
        
        if resultado.startswith("[Erro]"):
            return jsonify({
                "erro": resultado,
                "sucesso": False
            }), 500
        
        return jsonify({
            "sucesso": True,
            "resultado": resultado,
            "periodo": f"{data_inicio} a {data_fim}",
            "property_id": property_id
        })
        
    except Exception as e:
        log_error(f"Erro na consulta GA4 Pivot: {str(e)}")
        return jsonify({
            "erro": f"Erro interno: {str(e)}",
            "sucesso": False
        }), 500

@app.route('/search-console/sites', methods=['GET'])
def get_search_console_sites():
    """Lista sites do Google Search Console."""
    try:
        log_info("Solicitação para listar sites do Search Console")
        resultado = listar_sites_search_console()
        return jsonify(resultado)
    except Exception as e:
        log_error(f"Erro ao listar sites do Search Console: {str(e)}")
        return jsonify({
            "erro": f"Erro interno: {str(e)}",
            "sucesso": False
        }), 500

@app.route('/search-console/query', methods=['POST'])
def query_search_console_data():
    """Consulta dados do Google Search Console."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "erro": "Dados da requisição não fornecidos",
                "sucesso": False
            }), 400
        
        site_url = data.get('site_url')
        if not site_url:
            return jsonify({
                "erro": "site_url é obrigatório",
                "sucesso": False
            }), 400
        
        # Parâmetros opcionais
        data_inicio = data.get('data_inicio', '30daysAgo')
        data_fim = data.get('data_fim', 'today')
        dimensoes = data.get('dimensoes', ['query'])
        metrica_extra = data.get('metrica_extra', True)
        limite = data.get('limite', 100)
        query_filtro = data.get('query_filtro', '')
        pagina_filtro = data.get('pagina_filtro', '')
        filtros_customizados = data.get('filtros', [])
        
        log_info(f"Consulta Search Console: {site_url}, dimensões: {dimensoes}")
        
        resultado = consulta_search_console_custom(
            site_url=site_url,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dimensoes=dimensoes,
            metrica_extra=metrica_extra,
            filtros=filtros_customizados,
            limite=limite,
            query_filtro=query_filtro,
            pagina_filtro=pagina_filtro
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        log_error(f"Erro na consulta Search Console: {str(e)}")
        return jsonify({
            "erro": f"Erro interno: {str(e)}",
            "sucesso": False
        }), 500

@app.route('/search-console/verify', methods=['POST'])
def verify_search_console_site():
    """Verifica propriedade de site no Search Console."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "erro": "Dados da requisição não fornecidos",
                "sucesso": False
            }), 400
        
        site_url = data.get('site_url')
        if not site_url:
            return jsonify({
                "erro": "site_url é obrigatório",
                "sucesso": False
            }), 400
        
        log_info(f"Verificando propriedade do site: {site_url}")
        
        resultado = verificar_propriedade_site_search_console(site_url)
        return jsonify(resultado)
        
    except Exception as e:
        log_error(f"Erro na verificação do site: {str(e)}")
        return jsonify({
            "erro": f"Erro interno: {str(e)}",
            "sucesso": False
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "erro": "Endpoint não encontrado",
        "sucesso": False
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "erro": "Método não permitido",
        "sucesso": False
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "erro": "Erro interno do servidor",
        "sucesso": False
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    log_info(f"Iniciando Dex Analytics API na porta {port}")
    log_info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)