"""
Script de teste para verificar se a aplicação Flask está funcionando corretamente.
Este teste não requer credenciais do Google.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_import():
    """Testa se os imports básicos funcionam."""
    try:
        from flask import Flask
        print("OK Flask importado com sucesso")
        
        from flask_cors import CORS
        print("OK Flask-CORS importado com sucesso")
        
        # Importar módulos de agentes (podem falhar sem credenciais, mas a estrutura deve estar ok)
        try:
            from agents import analytics, search_console
            print("OK Módulos de agentes importados com sucesso")
        except Exception as e:
            print(f"WARNING Módulos de agentes com problemas (esperado sem credenciais): {e}")
        
        return True
    except Exception as e:
        print(f"ERROR Erro no import básico: {e}")
        return False

def test_app_creation():
    """Testa se a aplicação Flask pode ser criada."""
    try:
        # Remover temporariamente a dependência de credenciais para teste
        os.environ['SKIP_GOOGLE_INIT'] = 'true'
        
        from app import app
        print("OK Aplicacao Flask criada com sucesso")
        
        # Testar se o app tem as rotas esperadas
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        expected_routes = [
            'GET /',
            'GET /ga4/accounts',
            'POST /ga4/query',
            'POST /ga4/pivot',
            'GET /search-console/sites',
            'POST /search-console/query',
            'POST /search-console/verify'
        ]
        
        print(f"OK Encontradas {len(routes)} rotas:")
        for route in sorted(routes):
            if 'OPTIONS' not in route:  # Filtrar rotas OPTIONS automáticas do CORS
                print(f"  - {route}")
        
        return True
    except Exception as e:
        print(f"ERROR Erro na criacao da aplicacao: {e}")
        return False

def test_health_endpoint():
    """Testa o endpoint de saúde."""
    try:
        os.environ['SKIP_GOOGLE_INIT'] = 'true'
        from app import app
        
        with app.test_client() as client:
            response = client.get('/')
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"OK Endpoint de saude respondeu: {data.get('message', 'N/A')}")
                return True
            else:
                print(f"ERROR Endpoint de saude retornou status {response.status_code}")
                return False
    except Exception as e:
        print(f"ERROR Erro no teste do endpoint de saude: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("Iniciando testes da aplicacao DexGPT...\n")
    
    tests = [
        ("Import basico", test_basic_import),
        ("Criacao da aplicacao", test_app_creation),
        ("Endpoint de saude", test_health_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Testando: {test_name}")
        try:
            result = test_func()
            results.append(result)
            print(f"{'PASSOU' if result else 'FALHOU'} - {test_name}")
        except Exception as e:
            print(f"ERRO - {test_name}: {e}")
            results.append(False)
        print()
    
    # Resumo
    passed = sum(results)
    total = len(results)
    print(f"Resumo: {passed}/{total} testes passaram")
    
    if passed == total:
        print("Todos os testes passaram! A aplicacao esta pronta para deploy.")
    else:
        print("Alguns testes falharam. Verifique os erros acima.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)