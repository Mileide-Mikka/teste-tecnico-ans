# 🚀 Teste Técnico - Estágio de Desenvolvimento

Este repositório contém a resolução do teste técnico para a vaga de estágio. O projeto consiste em uma esteira completa de dados, desde a coleta via Web Scraping até a exibição em uma interface Web através de uma API REST.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Framework Web:** Flask
* **Banco de Dados:** PostgreSQL (Estrutura preparada)
* **Manipulação de Dados:** Pandas
* **Frontend:** HTML5, CSS3 e JavaScript (Vanilla)

## 📂 Estrutura do Projeto

* `teste1_api.py`: Script de coleta de dados.
* `teste2_validacao.py`: Processamento, limpeza e geração de arquivos CSV de apoio.
* `teste3_banco.sql`: Scripts de criação e população das tabelas do banco.
* `teste4_api.py`: Servidor Flask que disponibiliza os endpoints JSON.
* `index.html` / `script.js`: Interface visual para consumo dos dados.

## ⚙️ Como Executar

### 1. Preparação do Ambiente

Certifique-se de ter as bibliotecas necessárias instaladas:

```bash
pip install flask flask-cors pandas

```

### 2. Executando a API

Inicie o servidor Python:

```bash
python3 teste4_api.py

```

> **Nota de Configuração:** No ambiente macOS, a porta padrão 5000 pode estar ocupada pelo sistema (AirPlay). Por isso, a API foi configurada para rodar na porta **5001**.

### 3. Acessando a Interface

Abra o arquivo `index.html` em seu navegador. A interface irá consumir automaticamente os dados do endpoint:
`http://localhost:5001/api/estatisticas`

## 🧠 Trade-offs e Decisões Técnicas

* **Arquitetura Resiliente:** A API foi desenvolvida para priorizar a leitura do banco de dados PostgreSQL. No entanto, foi implementado um sistema de *fallback* (contingência) que utiliza os arquivos CSV gerados no **Teste 2**. Isso garante que o sistema permaneça funcional mesmo em casos de instabilidade na conexão com o banco.
* **Escolha do Framework:** Optei pelo **Flask** por ser um micro-framework leve e eficiente para o escopo de um teste técnico, permitindo uma implementação rápida e modular.
* **CORS:** Implementei o suporte a *Cross-Origin Resource Sharing* para permitir que o frontend se comunique de forma segura com a API em diferentes portas.

---

**Desenvolvido por:** Mileide Silva de Arruda