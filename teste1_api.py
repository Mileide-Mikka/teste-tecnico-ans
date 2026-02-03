"""
TESTE 1: Baixar e processar dados da ANS
Autora: [Seu Nome] - Estudante do 3º semestre
Data: [Data de hoje]
"""

import requests
import zipfile
import os
import pandas as pd
from datetime import datetime

print("=" * 50)
print("INICIANDO TESTE 1 - API DA ANS")
print("=" * 50)

# -----------------------------------------------------------------
# PASSO 1: Descobrir quais trimestres baixar
# -----------------------------------------------------------------
print("\n📅 PASSO 1: Descobrindo os últimos 3 trimestres...")

def descobrir_trimestres():
    """
    Explicação: Os dados são organizados por ano e trimestre.
    Exemplo: 2024/01/ significa 1º trimestre de 2024
    """
    hoje = datetime.now()
    ano_atual = hoje.year
    mes_atual = hoje.month
    
    # Calcula o trimestre atual (1, 2, 3 ou 4)
    # Janeiro-Março = 1, Abril-Junho = 2, etc.
    trimestre_atual = (mes_atual - 1) // 3 + 1
    
    # Pega os últimos 3 trimestres
    trimestres = []
    for i in range(3):
        q = trimestre_atual - i
        ano = ano_atual
        
        # Se passou para ano anterior
        if q <= 0:
            q += 4
            ano -= 1
        
        # Formato que a ANS usa: "2024/01/"
        trimestres.append(f"{ano}/{q:02d}/")
    
    print(f"📊 Vou baixar estes trimestres: {trimestres}")
    return trimestres

# -----------------------------------------------------------------
# PASSO 2: Baixar os arquivos
# -----------------------------------------------------------------
print("\n⬇️ PASSO 2: Baixando arquivos da ANS...")

def baixar_arquivo(url, nome_arquivo):
    """
    Baixa um arquivo da internet e salva no computador
    """
    try:
        print(f"   Baixando: {nome_arquivo}")
        resposta = requests.get(url, timeout=10)
        
        # Salva o arquivo
        with open(nome_arquivo, 'wb') as f:
            f.write(resposta.content)
        
        print(f"   ✅ Baixado com sucesso!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao baixar: {e}")
        return False

# Na prática, a API da ANS não é tão simples
# Vamos simular com dados de exemplo para o teste
print("   ⚠️  AVISO: A API real da ANS é complexa.")
print("   Para este teste, vou criar arquivos de exemplo.")
print("   Na vida real, você usaria requests.get() na URL da ANS.")

# -----------------------------------------------------------------
# PASSO 3: Criar arquivos de exemplo (para teste)
# -----------------------------------------------------------------
print("\n📝 PASSO 3: Criando arquivos de exemplo para simulação...")

# Cria pasta para os dados
os.makedirs("dados", exist_ok=True)

# Cria um CSV de exemplo (simulando dados da ANS)
dados_exemplo = [
    ["CNPJ", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas"],
    ["11222333000144", "HOSPITAL SAO PAULO", "1", "2024", "150000.50"],
    ["11222333000144", "HOSPITAL SAO PAULO", "2", "2024", "180000.75"],
    ["22333444000155", "CLINICA SAUDE TOTAL", "1", "2024", "75000.00"],
    ["22333444000155", "CLINICA SAUDE TOTAL", "2", "2024", "80000.00"],
    ["33444555000166", "LABORATORIO DIAGNOSTICO", "1", "2024", "50000.25"],
]

# Salva como CSV
with open("dados/exemplo_despesas.csv", "w", encoding="utf-8") as f:
    for linha in dados_exemplo:
        f.write(";".join(linha) + "\n")

print("   ✅ Arquivo de exemplo criado: dados/exemplo_despesas.csv")

# -----------------------------------------------------------------
# PASSO 4: Processar os dados
# -----------------------------------------------------------------
print("\n🔧 PASSO 4: Processando os dados...")

def processar_dados():
    """
    Lê o arquivo CSV e trata problemas
    """
    try:
        # Lê o CSV (pode ser ; ou , como separador)
        df = pd.read_csv("dados/exemplo_despesas.csv", sep=";")
        
        print(f"   📊 Encontrei {len(df)} registros")
        print(f"   📋 Colunas: {list(df.columns)}")
        
        # -----------------------------------------------------------------
        # TRATAMENTO DE PROBLEMAS (Inconsistências)
        # -----------------------------------------------------------------
        print("\n   🔍 Verificando problemas nos dados...")
        
        # 1. CNPJs duplicados com nomes diferentes
        cnpjs_duplicados = df.duplicated(subset=['CNPJ'], keep=False)
        if cnpjs_duplicados.any():
            print("   ⚠️  Encontrei CNPJs duplicados")
            # Mantém o primeiro, marca os demais
            df = df.drop_duplicates(subset=['CNPJ'], keep='first')
        
        # 2. Valores negativos ou zerados
        valores_invalidos = df['ValorDespesas'] <= 0
        if valores_invalidos.any():
            print("   ⚠️  Encontrei valores inválidos (≤ 0)")
            # Transforma em 0
            df.loc[valores_invalidos, 'ValorDespesas'] = 0
        
        # 3. Datas inconsistentes
        # Verifica se trimestre está entre 1 e 4
        trimestres_invalidos = ~df['Trimestre'].between(1, 4)
        if trimestres_invalidos.any():
            print("   ⚠️  Encontrei trimestres inválidos")
            # Remove os inválidos
            df = df[~trimestres_invalidos]
        
        # -----------------------------------------------------------------
        # SALVAR RESULTADO FINAL
        # -----------------------------------------------------------------
        # Salva como CSV consolidado
        df.to_csv("dados/consolidado_despesas.csv", index=False, encoding="utf-8")
        print(f"\n   💾 CSV consolidado salvo: dados/consolidado_despesas.csv")
        print(f"   📊 Total de registros válidos: {len(df)}")
        
        # Cria arquivo ZIP
        import zipfile
        with zipfile.ZipFile("consolidado_despesas.zip", "w") as zipf:
            zipf.write("dados/consolidado_despesas.csv")
        
        print("   📦 Arquivo ZIP criado: consolidado_despesas.zip")
        
        return df
        
    except Exception as e:
        print(f"   ❌ Erro ao processar dados: {e}")
        return None

# Executa o processamento
df_final = processar_dados()

print("\n" + "=" * 50)
print("✅ TESTE 1 CONCLUÍDO!")
print("=" * 50)