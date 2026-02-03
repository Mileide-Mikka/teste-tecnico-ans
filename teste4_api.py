"""
TESTE 4: API e Interface Web
Autora: Mileide Silva de Arruda

Para executar:
1. Instale: pip install flask flask-cors
2. Execute: python teste4_api.py
3. Abra: http://localhost:5001
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

print("=" * 50)
print("INICIANDO TESTE 4 - API E SITE")
print("=" * 50)

# -----------------------------------------------------------------
# TRADE-OFF: Flask vs FastAPI
# -----------------------------------------------------------------
print("\n TRADE-OFF TÉCNICO: Qual framework usar?")
print("   Opção A: Flask → Mais simples, bom para começar")
print("   Opção B: FastAPI → Mais moderno, mais complexo")
print("   ESCOLHI: Flask")
print("   POR QUÊ: Como estagiária, prefiro começar com o mais simples")
print("   e documentado. FastAPI tem conceitos mais avançados.")

app = Flask(__name__)
CORS(app)  # Permite o site acessar a API

# -----------------------------------------------------------------
# DADOS DE EXEMPLO (simulando banco de dados)
# -----------------------------------------------------------------
print("\n📊 Carregando dados de exemplo...")

# Carrega dados dos testes anteriores
try:
    df_operadoras = pd.read_csv("dados/consolidado_despesas.csv")
    df_agregado = pd.read_csv("dados/despesas_agregadas.csv")
    print(f"   ✅ Dados carregados: {len(df_operadoras)} registros")
except:
    print("   ⚠️  Criando dados de exemplo...")
    # Dados de exemplo se os arquivos não existirem
    df_operadoras = pd.DataFrame([
        {"CNPJ": "11222333000144", "RazaoSocial": "Hospital Sao Paulo", "UF": "SP", "ValorDespesas": 150000.50},
        {"CNPJ": "22333444000155", "RazaoSocial": "Clinica Saude Total", "UF": "RJ", "ValorDespesas": 75000.00},
        {"CNPJ": "33444555000166", "RazaoSocial": "Laboratorio Diagnostico", "UF": "MG", "ValorDespesas": 50000.25},
    ])
    
    df_agregado = pd.DataFrame([
        {"RazaoSocial": "Hospital Sao Paulo", "UF": "SP", "TotalDespesas": 330000.25},
        {"RazaoSocial": "Clinica Saude Total", "UF": "RJ", "TotalDespesas": 155000.00},
        {"RazaoSocial": "Laboratorio Diagnostico", "UF": "MG", "TotalDespesas": 50000.25},
    ])

# -----------------------------------------------------------------
# ROTA 1: Listar operadoras com paginação
# -----------------------------------------------------------------
@app.route('/api/operadoras', methods=['GET'])
def listar_operadoras():
    """
    Retorna lista de operadoras com paginação
    Exemplo: /api/operadoras?page=1&limit=10
    """
    try:
        # Pega parâmetros da URL
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Calcula início e fim
        start = (page - 1) * limit
        end = start + limit
        
        # -----------------------------------------------------------------
        # TRADE-OFF: Paginação
        # -----------------------------------------------------------------
        print("\n TRADE-OFF: Como fazer paginação?")
        print("   Opção A: Offset-based (SELECT ... LIMIT X OFFSET Y)")
        print("   Opção B: Cursor-based (mais complexo, melhor performance)")
        print("   ESCOLHI: Offset-based")
        print("   POR QUÊ: Dados pequenos, implementação simples")
        
        # Pega os dados paginados
        dados = df_operadoras.iloc[start:end].to_dict('records')
        
        return jsonify({
            "success": True,
            "data": dados,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(df_operadoras),
                "pages": (len(df_operadoras) + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# -----------------------------------------------------------------
# ROTA 2: Detalhes de uma operadora
# -----------------------------------------------------------------
@app.route('/api/operadoras/<cnpj>', methods=['GET'])
def detalhes_operadora(cnpj):
    """
    Retorna detalhes de uma operadora específica
    """
    try:
        # Filtra pelo CNPJ
        operadora = df_operadoras[df_operadoras['CNPJ'] == cnpj]
        
        if operadora.empty:
            return jsonify({
                "success": False,
                "error": "Operadora não encontrada"
            }), 404
        
        # Pega dados agregados também
        agregado = df_agregado[df_agregado['RazaoSocial'] == operadora.iloc[0]['RazaoSocial']]
        
        resultado = {
            "cnpj": operadora.iloc[0]['CNPJ'],
            "razao_social": operadora.iloc[0]['RazaoSocial'],
            "uf": operadora.iloc[0]['UF'],
            "despesas": operadora['ValorDespesas'].sum(),
            "agregado": agregado.to_dict('records') if not agregado.empty else []
        }
        
        return jsonify({
            "success": True,
            "data": resultado
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# -----------------------------------------------------------------
# ROTA 3: Estatísticas gerais
# -----------------------------------------------------------------
@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    """
    Retorna estatísticas agregadas
    """
    try:
        # -----------------------------------------------------------------
        # TRADE-OFF: Cache vs cálculo na hora
        # -----------------------------------------------------------------
        print("\n🤔 TRADE-OFF: Cache ou calcular sempre?")
        print("   Opção A: Calcular sempre → Dados sempre atualizados")
        print("   Opção B: Cache por 5 minutos → Mais rápido")
        print("   ✅ ESCOLHI: Calcular sempre")
        print("   POR QUÊ: Dados pequenos, atualização frequente")
        
        estatisticas = {
            "total_operadoras": len(df_operadoras),
            "total_despesas": df_operadoras['ValorDespesas'].sum(),
            "media_despesas": df_operadoras['ValorDespesas'].mean(),
            "top_5_operadoras": df_agregado.head(5).to_dict('records'),
            "distribuicao_uf": df_agregado.groupby('UF')['TotalDespesas'].sum().to_dict()
        }
        
        return jsonify({
            "success": True,
            "data": estatisticas
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# -----------------------------------------------------------------
# ROTA 4: Histórico de despesas
# -----------------------------------------------------------------
@app.route('/api/operadoras/<cnpj>/despesas', methods=['GET'])
def historico_despesas(cnpj):
    """
    Retorna histórico de despesas de uma operadora
    """
    try:
        # Filtra despesas pelo CNPJ
        historico = df_operadoras[df_operadoras['CNPJ'] == cnpj]
        
        if historico.empty:
            return jsonify({
                "success": False,
                "error": "Nenhuma despesa encontrada"
            }), 404
        
        return jsonify({
            "success": True,
            "data": historico.to_dict('records')
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# -----------------------------------------------------------------
# INICIAR SERVIDOR
# -----------------------------------------------------------------
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🚀 API Flask iniciando...")
    print("🌐 Acesse: http://localhost:5000")
    print("📚 Rotas disponíveis:")
    print("   • GET /api/operadoras")
    print("   • GET /api/operadoras/<cnpj>")
    print("   • GET /api/operadoras/<cnpj>/despesas")
    print("   • GET /api/estatisticas")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)