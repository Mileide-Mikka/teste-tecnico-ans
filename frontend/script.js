// ============================================
// VARIÁVEIS GLOBAIS
// ============================================
let todasOperadoras = [];
let operadorasFiltradas = [];
let paginaAtual = 1;
const itensPorPagina = 5;
let operadoraSelecionada = null;

// ============================================
// TRADE-OFF: Busca no cliente vs servidor
// ============================================
console.log("🤔 TRADE-OFF TÉCNICO: Onde fazer a busca?");
console.log("   Opção A: No servidor → Mais lento, precisa de internet");
console.log("   Opção B: No cliente → Mais rápido, funciona offline");
console.log("   Opção C: Híbrido → Complexo");
console.log("   ✅ ESCOLHI: Busca no cliente");
console.log("   POR QUÊ: Dados pequenos, melhor experiência do usuário");

// ============================================
// 1. CARREGAR DADOS DA API
// ============================================
async function carregarDados() {
    mostrarLoading(true);
    esconderErro();

    try {
        console.log("📥 Carregando dados da API...");

        // Carrega operadoras
        const resposta = await fetch('http://localhost:5001/api/operadoras?limit=100');
        const dados = await resposta.json();

        if (dados.success) {
            todasOperadoras = dados.data;
            operadorasFiltradas = [...todasOperadoras];
            console.log(`✅ ${todasOperadoras.length} operadoras carregadas`);
            atualizarTabela();
            carregarEstatisticas();
        } else {
            throw new Error(dados.error || 'Erro ao carregar dados');
        }

    } catch (erro) {
        console.error("❌ Erro:", erro);
        mostrarErro("Não foi possível conectar à API. Certifique-se que o servidor Flask está rodando.");

        // Dados de exemplo (fallback)
        console.log("⚠️  Usando dados de exemplo...");
        todasOperadoras = [
            { CNPJ: "11222333000144", RazaoSocial: "Hospital Sao Paulo", UF: "SP", ValorDespesas: 150000.50 },
            { CNPJ: "22333444000155", RazaoSocial: "Clinica Saude Total", UF: "RJ", ValorDespesas: 75000.00 },
            { CNPJ: "33444555000166", RazaoSocial: "Laboratorio Diagnostico", UF: "MG", ValorDespesas: 50000.25 },
            { CNPJ: "44555666000177", RazaoSocial: "Plano Saúde Excel", UF: "SP", ValorDespesas: 120000.00 },
            { CNPJ: "55666777000188", RazaoSocial: "Assistência Médica", UF: "RS", ValorDespesas: 85000.75 },
        ];
        operadorasFiltradas = [...todasOperadoras];
        atualizarTabela();
        carregarEstatisticas();

    } finally {
        mostrarLoading(false);
    }
}

// ============================================
// 2. FILTRAR TABELA (busca local)
// ============================================
function filtrarTabela() {
    const termo = document.getElementById('searchInput').value.toLowerCase();

    if (!termo) {
        operadorasFiltradas = [...todasOperadoras];
    } else {
        operadorasFiltradas = todasOperadoras.filter(op =>
            op.RazaoSocial.toLowerCase().includes(termo) ||
            op.CNPJ.includes(termo) ||
            op.UF.toLowerCase().includes(termo)
        );
    }

    paginaAtual = 1;
    atualizarTabela();
}

// ============================================
// 3. ATUALIZAR TABELA
// ============================================
function atualizarTabela() {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    // Calcula itens da página atual
    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const itensPagina = operadorasFiltradas.slice(inicio, fim);

    // Preenche a tabela
    itensPagina.forEach(operadora => {
        const tr = document.createElement('tr');

        tr.innerHTML = `
                    <td>${operadora.RazaoSocial}</td>
                    <td><span class="cnpj">${formatarCNPJ(operadora.CNPJ)}</span></td>
                    <td>${operadora.UF}</td>
                    <td class="valor">R$ ${operadora.ValorDespesas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                    <td>
                        <button onclick="verDetalhes('${operadora.CNPJ}')" style="
                            background: #48bb78;
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 5px;
                            cursor: pointer;
                        ">
                            Ver Detalhes
                        </button>
                    </td>
                `;

        tbody.appendChild(tr);
    });

    // Atualiza paginação
    atualizarPaginacao();

    // Se não houver resultados
    if (operadorasFiltradas.length === 0) {
        tbody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; padding: 40px; color: #6c757d;">
                            📭 Nenhuma operadora encontrada
                        </td>
                    </tr>
                `;
    }
}

// ============================================
// 4. PAGINAÇÃO
// ============================================
function atualizarPaginacao() {
    const totalPaginas = Math.ceil(operadorasFiltradas.length / itensPorPagina);
    const pageInfo = document.getElementById('pageInfo');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    pageInfo.textContent = `Página ${paginaAtual} de ${totalPaginas}`;
    prevBtn.disabled = paginaAtual === 1;
    nextBtn.disabled = paginaAtual === totalPaginas || totalPaginas === 0;
}

function mudarPagina(direcao) {
    const totalPaginas = Math.ceil(operadorasFiltradas.length / itensPorPagina);
    const novaPagina = paginaAtual + direcao;

    if (novaPagina >= 1 && novaPagina <= totalPaginas) {
        paginaAtual = novaPagina;
        atualizarTabela();
    }
}

// ============================================
// 5. VER DETALHES DA OPERADORA
// ============================================
async function verDetalhes(cnpj) {
    mostrarLoading(true);

    try {
        console.log(`🔍 Buscando detalhes do CNPJ: ${cnpj}`);

        // Busca na API
        const resposta = await fetch(`http://localhost:5001/api/operadoras/${cnpj}`);
        const dados = await resposta.json();

        if (dados.success) {
            operadoraSelecionada = dados.data;
            mostrarDetalhes();
            criarGraficoUF();
        } else {
            throw new Error(dados.error);
        }

    } catch (erro) {
        console.error("❌ Erro ao buscar detalhes:", erro);

        // Dados de exemplo
        operadoraSelecionada = {
            cnpj: cnpj,
            razao_social: "Operadora de Exemplo",
            UF: "SP",
            despesas: 100000,
            agregado: [{ TotalDespesas: 100000, UF: "SP" }]
        };
        mostrarDetalhes();
        criarGraficoUF();

    } finally {
        mostrarLoading(false);
    }
}

function mostrarDetalhes() {
    const detailsCard = document.getElementById('detailsCard');
    const detailsContent = document.getElementById('detailsContent');

    detailsCard.style.display = 'block';

    detailsContent.innerHTML = `
                <div class="details-card">
                    <h3>${operadoraSelecionada.razao_social}</h3>
                    <p><strong>CNPJ:</strong> <span class="cnpj">${formatarCNPJ(operadoraSelecionada.cnpj)}</span></p>
                    <p><strong>UF:</strong> ${operadoraSelecionada.UF}</p>
                    <p><strong>Total de Despesas:</strong> <span class="valor">R$ ${operadoraSelecionada.despesas.toFixed(2)}</span></p>
                    
                    <h3 style="margin-top: 20px;">📊 Dados Agregados</h3>
                    ${operadoraSelecionada.agregado && operadoraSelecionada.agregado.length > 0 ?
            `<p>Total consolidado: R$ ${operadoraSelecionada.agregado[0].TotalDespesas.toFixed(2)}</p>` :
            `<p style="color: #6c757d;">Nenhum dado agregado disponível</p>`
        }
                </div>
            `;

    // Rola até os detalhes
    detailsCard.scrollIntoView({ behavior: 'smooth' });
}

// ============================================
// 6. CRIAR GRÁFICO
// ============================================
function criarGraficoUF() {
    const chartPlaceholder = document.getElementById('chartPlaceholder');
    const canvas = document.getElementById('ufChart');

    // Simula dados para o gráfico
    const dadosUF = {
        'SP': 450000,
        'RJ': 155000,
        'MG': 50000,
        'RS': 85000,
        'PR': 65000
    };

    // Mostra canvas, esconde placeholder
    chartPlaceholder.style.display = 'none';
    canvas.style.display = 'block';

    // Cria contexto do gráfico
    const ctx = canvas.getContext('2d');

    // Limpa gráfico anterior
    if (window.meuGrafico) {
        window.meuGrafico.destroy();
    }

    // Cria novo gráfico (simplificado - na prática use Chart.js)
    canvas.width = canvas.parentElement.offsetWidth;
    canvas.height = 300;

    const ufs = Object.keys(dadosUF);
    const valores = Object.values(dadosUF);
    const maxValor = Math.max(...valores);

    // Desenha gráfico de barras simples
    const barWidth = canvas.width / ufs.length * 0.8;
    const espaco = canvas.width / ufs.length * 0.2;
    const escala = (canvas.height - 50) / maxValor;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Desenha barras
    ufs.forEach((uf, i) => {
        const x = i * (barWidth + espaco) + espaco / 2;
        const altura = valores[i] * escala;
        const y = canvas.height - altura - 30;

        // Barra
        ctx.fillStyle = '#667eea';
        ctx.fillRect(x, y, barWidth, altura);

        // Valor
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(
            `R$ ${(valores[i] / 1000).toFixed(0)}K`,
            x + barWidth / 2,
            y - 5
        );

        // Label UF
        ctx.fillText(uf, x + barWidth / 2, canvas.height - 10);
    });

    window.meuGrafico = { destroy: () => { } }; // Simulação
}

// ============================================
// 7. CARREGAR ESTATÍSTICAS
// ============================================
async function carregarEstatisticas() {
    try {
        const resposta = await fetch('http://localhost:5001/api/estatisticas');
        const dados = await resposta.json();

        if (dados.success) {
            document.getElementById('totalOperadoras').textContent =
                dados.data.total_operadoras;
            document.getElementById('totalDespesas').textContent =
                `R$ ${dados.data.total_despesas.toFixed(2)}`;
            document.getElementById('mediaDespesas').textContent =
                `R$ ${dados.data.media_despesas.toFixed(2)}`;
        }
    } catch (erro) {
        console.log("⚠️  Usando estatísticas locais...");
        // Calcula estatísticas dos dados locais
        const total = todasOperadoras.length;
        const soma = todasOperadoras.reduce((acc, op) => acc + op.ValorDespesas, 0);
        const media = total > 0 ? soma / total : 0;

        document.getElementById('totalOperadoras').textContent = total;
        document.getElementById('totalDespesas').textContent = `R$ ${soma.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}`;
        document.getElementById('mediaDespesas').textContent = `R$ ${media.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}`;
    }
}

// ============================================
// 8. FUNÇÕES AUXILIARES
// ============================================
function formatarCNPJ(cnpj) {
    // Transformamos em string e garantimos que tenha 14 dígitos
    const cnpjTexto = String(cnpj).padStart(14, '0');
    return cnpjTexto.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5");
}

function mostrarLoading(mostrar) {
    document.getElementById('loading').style.display =
        mostrar ? 'block' : 'none';
}

function mostrarErro(mensagem) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = mensagem;
    errorDiv.style.display = 'block';
}

function esconderErro() {
    document.getElementById('error').style.display = 'none';
}

// ============================================
// 9. INICIAR APLICAÇÃO
// ============================================
document.addEventListener('DOMContentLoaded', function () {
    console.log("🚀 Aplicação iniciada!");
    console.log("🧠 Desenvolvido por Mileide Silva de Arruda");
    carregarDados();
});