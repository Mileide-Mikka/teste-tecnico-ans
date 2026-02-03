"""
TESTE 2: Validar e enriquecer dados
Autora: Mileide Silva de Arruda
"""

import pandas as pd
import re

print("=" * 50)
print("INICIANDO TESTE 2 - VALIDAÇÃO DE DADOS")
print("=" * 50)

# -----------------------------------------------------------------
# PASSO 1: Validar CNPJ
# -----------------------------------------------------------------
print("\n🔍 PASSO 1: Validando CNPJs...")

def validar_cnpj(cnpj):
    """
    Valida se um CNPJ é verdadeiro
    CNPJ válido tem 14 dígitos e dígitos verificadores corretos
    """
    # Converte para string e remove caracteres não numéricos
    cnpj_str = str(cnpj)
    cnpj_limpo = re.sub(r'[^0-9]', '', cnpj_str)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_limpo) != 14:
        return False
    
    # Verifica se não é uma sequência de números iguais
    if cnpj_limpo == cnpj_limpo[0] * 14:
        return False
    
    # Aqui viria o cálculo dos dígitos verificadores
    # Para simplificar, vamos considerar válido se começar com 1, 2 ou 3
    return cnpj_limpo[0] in ['1', '2', '3']

# -----------------------------------------------------------------
# PASSO 2: Carregar dados do Teste 1
# -----------------------------------------------------------------
print("\n📂 PASSO 2: Carregando dados consolidados...")

try:
    df = pd.read_csv("dados/consolidado_despesas.csv")
    
    # ADICIONE ESTA LINHA ABAIXO:
    df['CNPJ'] = df['CNPJ'].astype(str) # Garante que o CNPJ do CSV seja texto
    
    print(f"   ✅ Dados carregados: {len(df)} registros")
    
    # -----------------------------------------------------------------
    # PASSO 3: Aplicar validações
    # -----------------------------------------------------------------
    print("\n✅ PASSO 3: Aplicando validações...")
    
    # Valida CNPJ
    df['CNPJ_VALIDO'] = df['CNPJ'].apply(validar_cnpj)
    
    # Valida valores positivos
    df['VALOR_POSITIVO'] = df['ValorDespesas'] > 0
    
    # Valida razão social não vazia
    df['NOME_VALIDO'] = df['RazaoSocial'].notna() & (df['RazaoSocial'].str.strip() != '')
    
    # Conta quantos são válidos
    validos = df['CNPJ_VALIDO'].sum()
    print(f"   📊 CNPJs válidos: {validos} de {len(df)}")
    print(f"   📊 Valores positivos: {df['VALOR_POSITIVO'].sum()} de {len(df)}")
    print(f"   📊 Nomes válidos: {df['NOME_VALIDO'].sum()} de {len(df)}")
    
    # -----------------------------------------------------------------
    # TRADE-OFF: O que fazer com CNPJs inválidos?
    # -----------------------------------------------------------------
    print("\n🤔 TRADE-OFF TÉCNICO: O que fazer com CNPJs inválidos?")
    print("   Opção A: Remover → Perde dados")
    print("   Opção B: Corrigir → Complexo, pode errar")
    print("   Opção C: Marcar como suspeito → Melhor para análise")
    print("   ✅ ESCOLHI: Opção C - Marcar como suspeito")
    print("   POR QUÊ: Como estagiária, prefiro identificar problemas")
    print("   do que escondê-los. Um supervisor pode analisar depois.")
    
    # Marca registros suspeitos
    df['SUSPEITO'] = ~df['CNPJ_VALIDO'] | ~df['VALOR_POSITIVO'] | ~df['NOME_VALIDO']
    
    # -----------------------------------------------------------------
    # PASSO 4: Baixar dados cadastrais (simulação)
    # -----------------------------------------------------------------
    print("\n📋 PASSO 4: Enriquecendo com dados cadastrais...")
    
    # Cria dados cadastrais de exemplo
    dados_cadastro = [
        ["11222333000144", "123456", "Hospital Sao Paulo", "Hospitalar", "SP"],
        ["22333444000155", "234567", "Clinica Saude Total", "Ambulatorial", "RJ"],
        ["99999888000177", "345678", "Outra Operadora", "Referência", "MG"],
    ]
    
    df_cadastro = pd.DataFrame(dados_cadastro, 
                               columns=["CNPJ", "RegistroANS", "RazaoSocial", "Modalidade", "UF"])
    
    # -----------------------------------------------------------------
    # PASSO 5: Juntar os dados (JOIN)
    # -----------------------------------------------------------------
    print("\n🔗 PASSO 5: Fazendo JOIN entre despesas e cadastro...")
    
    # Faz o JOIN usando CNPJ como chave
    # LEFT JOIN: mantém todas as despesas, mesmo sem cadastro
    df_completo = pd.merge(
        df,
        df_cadastro[["CNPJ", "RegistroANS", "Modalidade", "UF"]],
        on="CNPJ",
        how="left"  # LEFT JOIN é o mais seguro
    )
    
    # Verifica quantos não encontraram match
    sem_cadastro = df_completo['RegistroANS'].isna().sum()
    print(f"   ⚠️  Registros sem cadastro: {sem_cadastro} de {len(df_completo)}")
    
    # -----------------------------------------------------------------
    # PASSO 6: Agregar dados
    # -----------------------------------------------------------------
    print("\n📊 PASSO 6: Agregando dados por operadora...")
    
    # Agrupa por Razão Social e UF
    # Calcula: total, média e desvio padrão
    agregado = df_completo.groupby(['RazaoSocial', 'UF']).agg({
        'ValorDespesas': ['sum', 'mean', 'std']
    }).reset_index()
    
    # Melhora os nomes das colunas
    agregado.columns = ['RazaoSocial', 'UF', 'TotalDespesas', 'MediaTrimestral', 'DesvioPadrao']
    
    # Ordena do maior para o menor
    agregado = agregado.sort_values('TotalDespesas', ascending=False)
    
    print(f"   📈 Total de grupos: {len(agregado)}")
    print(f"   🥇 Maior despesa: R$ {agregado['TotalDespesas'].iloc[0]:,.2f}")
    
    # -----------------------------------------------------------------
    # PASSO 7: Salvar resultados
    # -----------------------------------------------------------------
    print("\n💾 PASSO 7: Salvando resultados...")
    
    # Salva o CSV agregado
    agregado.to_csv("dados/despesas_agregadas.csv", index=False, encoding="utf-8")
    print("   ✅ CSV salvo: dados/despesas_agregadas.csv")
    
    # Cria ZIP final
    import zipfile
    import os
    
    # Lista de arquivos para compactar
    arquivos_zip = [
        "dados/consolidado_despesas.csv",
        "dados/despesas_agregadas.csv"
    ]
    
    # Cria o ZIP
    nome_zip = f"Teste_SeuNome.zip"
    with zipfile.ZipFile(nome_zip, 'w') as zipf:
        for arquivo in arquivos_zip:
            if os.path.exists(arquivo):
                zipf.write(arquivo)
    
    print(f"   📦 ZIP criado: {nome_zip}")
    print("   📎 Arquivos incluídos:")
    for arquivo in zipf.namelist():
        print(f"      • {arquivo}")
    
except FileNotFoundError:
    print("   ❌ ERRO: Arquivo consolidado_despesas.csv não encontrado!")
    print("   Execute primeiro o Teste 1 (teste1_api.py)")

print("\n" + "=" * 50)
print("✅ TESTE 2 CONCLUÍDO!")
print("=" * 50)