/*
TESTE 3: Banco de Dados PostgreSQL
Autora: Mileide Silva de Arruda

*/

-- ============================================
-- PASSO 1: CRIAR TABELAS
-- ============================================

-- PASSO 1: Criando tabelas...

-- Tabela de operadoras (dados cadastrais)
CREATE TABLE IF NOT EXISTS operadoras (
    cnpj VARCHAR(14) PRIMARY KEY,           -- CNPJ é a chave primária
    registro_ans VARCHAR(20),               -- Número do registro
    razao_social VARCHAR(200) NOT NULL,     -- Nome da empresa
    modalidade VARCHAR(100),                -- Tipo de plano
    uf CHAR(2),                             -- Estado (SP, RJ, etc.)
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Data automática
);

-- Tabela de despesas
CREATE TABLE IF NOT EXISTS despesas (
    id SERIAL PRIMARY KEY,                  -- Número automático
    cnpj VARCHAR(14) REFERENCES operadoras(cnpj),  -- Link para operadoras
    trimestre INTEGER NOT NULL CHECK (trimestre BETWEEN 1 AND 4), -- Só 1-4
    ano INTEGER NOT NULL,
    valor_despesas DECIMAL(15,2) NOT NULL,  -- Dinheiro com 2 casas decimais
    suspeito BOOLEAN DEFAULT FALSE,         -- Marca dados suspeitos
    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de dados agregados (pré-calculados)
CREATE TABLE IF NOT EXISTS despesas_agregadas (
    cnpj VARCHAR(14) REFERENCES operadoras(cnpj),
    uf CHAR(2),
    total_despesas DECIMAL(15,2),
    media_trimestral DECIMAL(15,2),
    desvio_padrao DECIMAL(15,2),
    PRIMARY KEY (cnpj, uf)  -- Chave composta
);

-- ============================================
-- TRADE-OFF TÉCNICO: Normalização
-- ============================================
PRINT '
TRADE-OFF TÉCNICO: Como organizar as tabelas?
Opção A: Uma tabela gigante com tudo
Opção B: Várias tabelas especializadas

ESCOLHI: Opção B (3 tabelas separadas)
POR QUÊ:
1. Despesas mudam todo trimestre
2. Cadastro muda pouco
3. Facilita manutenção
4. Evita duplicação de dados';

-- ============================================
-- TRADE-OFF TÉCNICO: Tipos de dados
-- ============================================
PRINT '
TRADE-OFF TÉCNICO: Que tipo usar para dinheiro?
Opção A: FLOAT → Mais rápido, menos preciso
Opção B: DECIMAL → Mais preciso, um pouco mais lento
Opção C: INTEGER (centavos) → Mais exato, menos legível

SCOLHI: DECIMAL(15,2)
POR QUÊ:
1. Precisão absoluta (importante para dinheiro)
2. Fácil de entender (R$ 100.50)
3. Performance boa para nosso volume';

-- ============================================
-- PASSO 2: CRIAR ÍNDICES (para performance)
-- ============================================

-- PASSO 2: Criando índices para acelerar buscas...

-- Índice para buscar despesas por período
CREATE INDEX IF NOT EXISTS idx_despesas_periodo 
ON despesas(ano, trimestre);

-- Índice para buscar por CNPJ
CREATE INDEX IF NOT EXISTS idx_despesas_cnpj 
ON despesas(cnpj);

-- Índice para ordenar por valor
CREATE INDEX IF NOT EXISTS idx_despesas_valor 
ON despesas(valor_despesas DESC);

-- Índices criados com sucesso!

-- ============================================
-- PASSO 3: IMPORTAR DADOS (simulação)
-- ============================================

-- PASSO 3: Importando dados de exemplo...

-- Inserir operadoras de exemplo
INSERT INTO operadoras (cnpj, registro_ans, razao_social, modalidade, UF) VALUES
('11222333000144', '123456', 'Hospital Sao Paulo', 'Hospitalar', 'SP'),
('22333444000155', '234567', 'Clinica Saude Total', 'Ambulatorial', 'RJ'),
('33444555000166', '345678', 'Laboratorio Diagnostico', 'Diagnóstico', 'MG')
ON CONFLICT (cnpj) DO NOTHING;

-- Inserir despesas de exemplo
INSERT INTO despesas (cnpj, trimestre, ano, valor_despesas) VALUES
('11222333000144', 1, 2024, 150000.50),
('11222333000144', 2, 2024, 180000.75),
('22333444000155', 1, 2024, 75000.00),
('22333444000155', 2, 2024, 80000.00),
('33444555000166', 1, 2024, 50000.25)
ON CONFLICT DO NOTHING;

-- Dados de exemplo inseridos!

-- ============================================
-- PASSO 4: QUERIES ANALÍTICAS
-- ============================================

-- PASSO 4: Executando queries analíticas...

-- -------------------------------------------------
-- QUERY 1: Top 5 operadoras com maior crescimento
-- -------------------------------------------------
-- QUERY 1: Top 5 operadoras com maior crescimento percentual

WITH primeiro_trimestre AS (
    SELECT cnpj, AVG(valor_despesas) as inicio
    FROM despesas 
    WHERE ano = 2024 AND trimestre = 1
    GROUP BY cnpj
),
ultimo_trimestre AS (
    SELECT cnpj, AVG(valor_despesas) as fim
    FROM despesas 
    WHERE ano = 2024 AND trimestre = 2
    GROUP BY cnpj
)
SELECT 
    o.razao_social,
    o.uf,
    COALESCE(p.inicio, 0) as valor_inicial,
    COALESCE(u.fim, 0) as valor_final,
    CASE 
        WHEN COALESCE(p.inicio, 0) = 0 THEN 0
        ELSE ROUND((COALESCE(u.fim, 0) - COALESCE(p.inicio, 0)) / p.inicio * 100, 2)
    END as crescimento_percentual
FROM operadoras o
LEFT JOIN primeiro_trimestre p ON o.cnpj = p.cnpj
LEFT JOIN ultimo_trimestre u ON o.cnpj = u.cnpj
ORDER BY crescimento_percentual DESC
LIMIT 5;

-- -------------------------------------------------
-- QUERY 2: Top 5 estados com maiores despesas
-- -------------------------------------------------
-- QUERY 2: Top 5 estados com maiores despesas

SELECT 
    o.uf,
    SUM(d.valor_despesas) as total_despesas,
    COUNT(DISTINCT o.cnpj) as qtd_operadoras,
    ROUND(AVG(d.valor_despesas), 2) as media_por_operadora
FROM operadoras o
JOIN despesas d ON o.cnpj = d.cnpj
GROUP BY o.uf
ORDER BY total_despesas DESC
LIMIT 5;

-- -------------------------------------------------
-- QUERY 3: Operadoras acima da média
-- -------------------------------------------------
-- QUERY 3: Operadoras com despesas acima da média

-- Calcula média geral por trimestre
WITH media_geral AS (
    SELECT 
        trimestre,
        ano,
        AVG(valor_despesas) as media_trimestral
    FROM despesas
    GROUP BY trimestre, ano
),
operadoras_acima AS (
    SELECT 
        d.cnpj,
        d.trimestre,
        COUNT(CASE WHEN d.valor_despesas > m.media_trimestral THEN 1 END) as vezes_acima
    FROM despesas d
    JOIN media_geral m ON d.trimestre = m.trimestre AND d.ano = m.ano
    GROUP BY d.cnpj, d.trimestre
)
SELECT 
    o.razao_social,
    COUNT(DISTINCT oa.trimestre) as trimestres_com_dados,
    SUM(oa.vezes_acima) as vezes_acima_da_media
FROM operadoras o
JOIN operadoras_acima oa ON o.cnpj = oa.cnpj
GROUP BY o.cnpj, o.razao_social
HAVING SUM(oa.vezes_acima) >= 2  -- Acima da média em pelo menos 2 trimestres
ORDER BY vezes_acima_da_media DESC;

PRINT '
============================================
    TESTE 3 CONCLUÍDO!
============================================';