"""Dashboard ReverseMilk — Edição Bento Box (Alto Contraste & Tela Cheia Corrigida)
Rode com: streamlit run app.py
"""
from datetime import datetime, time, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

from agendamento import BUFFER_MIN, agendamento_reverso, reprogramar
from gerar_dados import ROTEIROS, gerar
from indicadores import classificar_etapas, distribuicao_mc, resumo_ops

st.set_page_config(page_title="ReverseMilk", page_icon="🥛", layout="wide", initial_sidebar_state="expanded")

components.html("""<script>
const d = window.parent.document;
d.documentElement.setAttribute('translate', 'no'); d.documentElement.lang = 'pt-BR';
</script>""", height=0)

# ---------------------------------------------------------------- CSS BENTO BOX & ALTO CONTRASTE
css_bento = r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    footer {visibility: hidden;}
    
    .block-container {
        padding: 2rem 1.5rem;
        max-width: 1600px;
    }

    /* =========================================================
       TABS: CENTRALIZADAS, LETRA MAIOR E ALTO CONTRASTE
       ========================================================= */
    
    /* 1. Força o container das abas a ir para o centro da tela */
    div[data-testid="stTabs"] > div[data-baseweb="tab-list"],
    div[data-testid="stTabs"] > div:first-child {
        display: flex !important;
        justify-content: center !important;
        flex-wrap: wrap !important;
        gap: 16px !important;
        padding-bottom: 24px !important;
        width: 100% !important;
    }

    /* 2. Remove a linha colorida inferior padrão do Streamlit */
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] div[data-baseweb="tab-border"] {
        display: none !important;
    }

    /* 3. Estilo da aba INATIVA (Formato de pílula) */
    div[data-testid="stTabs"] button[role="tab"] {
        background-color: var(--secondary-background-color) !important;
        border: 2px solid rgba(128, 128, 128, 0.3) !important;
        border-radius: 99px !important;
        padding: 14px 28px !important;
        margin: 0 !important;
        transition: all 0.2s ease;
    }
    
    /* 4. Letra da aba INATIVA (Maior e preta/branca dependendo do tema) */
    div[data-testid="stTabs"] button[role="tab"] div[data-testid="stMarkdownContainer"] p {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: var(--text-color) !important;
        margin: 0 !important;
    }

    /* Ícones do Bootstrap nas abas INATIVAS */
    div[data-testid="stTabs"] button[role="tab"]:nth-child(1)::before { content: "\F143"; font-family: "bootstrap-icons"; margin-right: 10px; font-size: 20px; color: var(--text-color) !important; }
    div[data-testid="stTabs"] button[role="tab"]:nth-child(2)::before { content: "\F225"; font-family: "bootstrap-icons"; margin-right: 10px; font-size: 20px; color: var(--text-color) !important; }
    div[data-testid="stTabs"] button[role="tab"]:nth-child(3)::before { content: "\F294"; font-family: "bootstrap-icons"; margin-right: 10px; font-size: 20px; color: var(--text-color) !important; }
    div[data-testid="stTabs"] button[role="tab"]:nth-child(4)::before { content: "\F5EA"; font-family: "bootstrap-icons"; margin-right: 10px; font-size: 20px; color: var(--text-color) !important; }
    div[data-testid="stTabs"] button[role="tab"]:nth-child(5)::before { content: "\F2EE"; font-family: "bootstrap-icons"; margin-right: 10px; font-size: 20px; color: var(--text-color) !important; }

    /* 5. Estilo da aba ATIVA (Inverte as cores) */
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background-color: var(--text-color) !important;
        border: 2px solid var(--text-color) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        transform: scale(1.05) !important;
    }
    
    /* 6. Letra e ícone da aba ATIVA (Cor invertida) */
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] div[data-testid="stMarkdownContainer"] p {
        color: var(--background-color) !important;
        font-weight: 900 !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]::before {
        color: var(--background-color) !important;
    }

    /* =========================================================
       TABELAS E EXPANSORES
       ========================================================= */
    [data-testid="stDataFrame"] {
        background-color: var(--secondary-background-color);
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 2px solid rgba(128, 128, 128, 0.2);
        box-sizing: border-box !important;
        overflow: hidden !important; /* Corta o que vazar da borda arredondada */
        /* Padding removido para tabela encaixar perfeitamente */
    }
    .stExpander {
        background-color: var(--secondary-background-color) !important;
        border-radius: 16px !important;
        border: 2px solid rgba(128, 128, 128, 0.2) !important;
    }
    
    /* =========================================================
       CORREÇÃO DO MODO TELA CHEIA (FULLSCREEN)
       ========================================================= */
    /* Garante que o container ocupe toda a tela */
    [data-testid="stFullScreenFrame"], 
    [data-testid="stFullScreenFrame"] > div {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        flex: 1 !important;
    }

    /* Força as tabelas a ignorarem a trava de altura quando em tela cheia */
    [data-testid="stFullScreenFrame"] [data-testid="stDataFrame"],
    [data-testid="stFullScreenFrame"] [data-testid="stDataFrame"] > div {
        height: 100% !important;
        min-height: 100% !important;
        max-height: 100% !important;
        flex: 1 !important;
    }
    
    @media (max-width: 768px) {
        div[data-testid="stTabs"] button[role="tab"] {
            padding: 10px 16px !important;
        }
        div[data-testid="stTabs"] button[role="tab"] div[data-testid="stMarkdownContainer"] p {
            font-size: 15px !important;
        }
        div[data-testid="stTabs"] button[role="tab"]::before {
            font-size: 16px !important;
        }
    }
</style>
"""
st.markdown(css_bento, unsafe_allow_html=True)

CORES = {"No prazo": "#2e9e5b", "Em risco": "#f0a30a", "Atrasada": "#d64545",
         "Concluída no prazo": "#1f6f43", "Concluída com atraso": "#8c5a2b"}
ICONES = {"No prazo": "🟢", "Em risco": "🟡", "Atrasada": "🔴",
          "Concluída no prazo": "✅", "Concluída com atraso": "🟤"}
COLS_DATA = ["prazo", "plan_inicio", "plan_fim", "real_inicio", "real_fim"]


# ---------------------------------------------------------------- FUNÇÕES HTML (ALTO CONTRASTE, SEM OPACITY)
def bento_kpi(titulo, valor, subtitulo):
    html = f"""<div style="background-color: var(--secondary-background-color); border-radius: 24px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 2px solid rgba(128, 128, 128, 0.15); height: 100%; display: flex; flex-direction: column; justify-content: center;">
<div style="color: var(--text-color); font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">{titulo}</div>
<div style="color: var(--text-color); font-size: clamp(36px, 4vw, 48px); font-weight: 900; margin: 8px 0; line-height: 1;">{valor}</div>
<div style="color: var(--text-color); font-size: 15px; font-weight: 600;">{subtitulo}</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)

def bento_alerta(op, produto, etapa, hora, margem, critico=True):
    cor_borda = "#dc2626" if critico else "#d97706"
    html = f"""<div style="background-color: var(--secondary-background-color); border-left: 8px solid {cor_borda}; border-radius: 16px; padding: 20px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-top: 2px solid rgba(128,128,128,0.15); border-right: 2px solid rgba(128,128,128,0.15); border-bottom: 2px solid rgba(128,128,128,0.15);">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; margin-bottom: 8px; gap: 8px;">
<div style="color: var(--text-color); font-weight: 900; font-size: 18px;">OP {op} • {produto}</div>
<div style="background-color: {cor_borda}; color: #ffffff; padding: 6px 14px; border-radius: 99px; font-size: 13px; font-weight: 800; white-space: nowrap;">{margem:.0f} min margem</div>
</div>
<div style="color: var(--text-color); font-size: 15px; font-weight: 600;">Etapa atual: <span style="font-weight: 800;">{etapa}</span></div>
<div style="color: var(--text-color); font-size: 15px; font-weight: 600; margin-top: 4px;">Projeção de término: <span style="font-weight: 800;">{hora}</span></div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------------------------------------------- DADOS
@st.cache_data
def dados_sinteticos(n, seed):
    return gerar(int(n), int(seed), base=datetime(2026, 10, 5, 6, 0))

@st.cache_data
def calcular(df, agora, tol, limite, n_sim):
    d = classificar_etapas(df, agora, tol)
    return d, resumo_ops(d, agora, limite, n_sim=n_sim)


# ---------------------------------------------------------------- SIDEBAR
st.sidebar.markdown("<h2 style='font-weight: 900; color: var(--text-color);'><i class='bi bi-droplet-fill' style='color: #2563eb; margin-right: 8px;'></i>ReverseMilk</h2>", unsafe_allow_html=True)

with st.sidebar.expander("Entenda as Premissas", expanded=False):
    st.markdown("""
    **Critérios de Alertas:**
    - 🔴 **Atrasada:** Margem < 0.
    - 🟡 **Em Risco:** Margem positiva, mas abaixo do limite.
    - 🟢 **No Prazo:** Margem segura.
    
    **Simulação Monte Carlo:**
    Simula centenas de cenários aplicando distribuição Lognormal nos tempos, prevendo probabilidade de atraso.
    """)

st.sidebar.markdown("---")
arq = st.sidebar.file_uploader("Usar CSV próprio", type="csv")
n_ops = st.sidebar.number_input("Nº de ordens (sintéticos)", 10, 200, 40, 5)
seed = st.sidebar.number_input("Semente aleatória", 0, 9999, 42)

df = pd.read_csv(arq, parse_dates=COLS_DATA) if arq else dados_sinteticos(n_ops, seed)
dmin = df.plan_inicio.min().floor("30min").to_pydatetime()
dmax = df.prazo.max().ceil("30min").to_pydatetime()
padrao = min(dmin + timedelta(hours=24), dmax)

st.sidebar.markdown("---")
agora = pd.Timestamp(st.sidebar.slider(
    "Horário atual (simulado)", min_value=dmin, max_value=dmax, value=padrao, step=timedelta(minutes=30), format="DD/MM HH:mm"))
tol = st.sidebar.slider("Tolerância (min)", 5, 120, 30)
limite = st.sidebar.slider("Margem alerta (min)", 15, 240, 30)
n_sim = st.sidebar.select_slider("Simulações", [200, 500, 1000, 2000], 1000)

d, r = calcular(df, agora, tol, limite, n_sim)

# ---------------------------------------------------------------- CABEÇALHO MAIN CENTRALIZADO
st.markdown(f"""
<div style="margin-bottom: 48px; display: flex; flex-direction: column; align-items: center; text-align: center; width: 100%;">
    <div style="font-size: clamp(36px, 5vw, 54px); font-weight: 900; letter-spacing: -1.5px; line-height: 1.2; color: var(--text-color);">Planejamento Reverso & Cenários</div>
    <div style="font-size: 18px; font-weight: 600; margin-top: 12px; color: var(--text-color);">Status simulado: <b>{agora:%d/%m/%Y às %H:%M}</b></div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- ABAS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Visão geral", "Linha do tempo", "Agendamento reverso", "Simular atraso", "Dados"
])

# ------------------------------------------------------------ VISÃO GERAL
with tab1:
    produtos = sorted(r.produto.unique())
    r1 = r.copy()
    d1 = d.copy()
    em_and = r1[~r1.status.str.startswith("Concluída")]
    conc = r1[r1.status.str.startswith("Concluída")]
    impacto = (-em_and.margem_min).clip(lower=0)

    # GRID ASSIMÉTRICO DE KPIS
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2], gap="large")
    with c1: bento_kpi("OPs Ativas", str(len(em_and)), "Em andamento")
    with c2: bento_kpi("Críticas", str(int((r1.status.isin(["Atrasada", "Em risco"])).sum())), "Atraso ou Risco")
    with c3: 
        taxa = f"{(conc.status == 'Concluída no prazo').mean() * 100:.0f}%" if len(conc) else "—"
        bento_kpi("Sucesso", taxa, "Entregas no prazo")
    with c4: bento_kpi("Desvio Médio", f"{impacto.mean():.0f} min" if len(em_and) else "0 min", "Atraso projetado")
    
    st.write("")
    st.write("")

    col_alertas, col_gargalos = st.columns([1, 1.3], gap="large")
    
    with col_alertas:
        st.markdown("<h3 style='font-weight: 900; font-size: 22px; margin-bottom: 20px; color: var(--text-color);'><i class='bi bi-exclamation-octagon-fill' style='color: #dc2626; margin-right: 10px;'></i>Alertas Preventivos</h3>", unsafe_allow_html=True)
        crit = em_and[em_and.status.isin(["Atrasada", "Em risco"])].sort_values("margem_min")
        if crit.empty:
            st.success("Tudo sob controle. Nenhuma OP crítica.")
        for _, x in crit.head(4).iterrows():
            bento_alerta(x.op, x.produto, x.etapa_atual, f"{x.projecao_conclusao:%H:%M}", x.margem_min, critico=(x.status=="Atrasada"))
        if len(crit) > 4:
            with st.expander(f"Ver mais {len(crit) - 4} alertas"):
                for _, x in crit.iloc[4:].iterrows():
                    bento_alerta(x.op, x.produto, x.etapa_atual, f"{x.projecao_conclusao:%H:%M}", x.margem_min, critico=(x.status=="Atrasada"))

    with col_gargalos:
        st.markdown("<h3 style='font-weight: 900; font-size: 22px; margin-bottom: 20px; color: var(--text-color);'><i class='bi bi-search' style='color: #2563eb; margin-right: 10px;'></i>Análise de Gargalos</h3>", unsafe_allow_html=True)
        
        iniciadas = d1[d1.situacao != "Pendente"].copy()
        iniciadas["gargalo"] = iniciadas.produto + " - " + iniciadas.etapa
        garg = (iniciadas.assign(atraso=iniciadas.atraso_min.clip(lower=0))
                .groupby("gargalo", as_index=False).atraso.mean().sort_values("atraso", ascending=True).tail(5))
        
        fig_garg = px.bar(garg, x="atraso", y="gargalo", orientation="h", title="Etapas de maior atraso (min)")
        fig_garg.update_traces(marker_color="#2563eb")
        fig_garg.update_layout(margin=dict(l=0, r=0, t=30, b=0), title_font=dict(size=16, family="Inter", color="#000000"))
        st.plotly_chart(fig_garg, use_container_width=True, theme="streamlit")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    with st.expander("Ver Tabela Completa de Ordens de Produção", expanded=False):
        st_sel = st.multiselect("Filtrar por status", list(CORES), default=list(CORES)) or list(CORES)
        tab = r1[r1.status.isin(st_sel)].copy()
        tab["prob_atraso"] = tab.prob_atraso * 100
        tab["status"] = tab.status.map(lambda s: f"{ICONES[s]} {s}")
        tab["progresso"] = tab.etapas_concluidas.astype(str) + "/" + tab.total_etapas.astype(str)
        st.dataframe(
            tab[["op", "produto", "status", "etapa_atual", "progresso", "prazo",
                 "projecao_conclusao", "p90_conclusao", "margem_min", "prob_atraso"]].sort_values("margem_min"),
            hide_index=True, use_container_width=True, height=300,
            column_config={
                "op": "OP", "produto": "Produto", "status": "Status", "etapa_atual": "Etapa atual",
                "progresso": "Etapas", "prazo": st.column_config.DatetimeColumn("Prazo", format="DD/MM HH:mm"),
                "projecao_conclusao": st.column_config.DatetimeColumn("Projeção", format="DD/MM HH:mm"),
                "p90_conclusao": st.column_config.DatetimeColumn("Pessimista (P90)", format="DD/MM HH:mm"),
                "margem_min": st.column_config.NumberColumn("Margem", format="%.0f"),
                "prob_atraso": st.column_config.ProgressColumn("Risco", min_value=0, max_value=100, format="%.0f%%"),
            })

# --------------------------------------------------------- LINHA DO TEMPO
with tab2:
    st.markdown("<h3 style='font-weight: 900; color: var(--text-color);'><i class='bi bi-calendar2-check-fill' style='color: #2563eb; margin-right: 10px;'></i>Auditoria de Ordem: Planejado vs Realizado</h3>", unsafe_allow_html=True)
    op = st.selectbox("Selecione a Ordem de produção:", r.sort_values("margem_min").op)
    g = d[d.op == op].sort_values("ordem_etapa")
    prazo_op = g.prazo.iloc[0]
    
    plan = g.assign(Tipo="Planejado", ini=g.plan_inicio, fim=g.plan_fim)
    real = g[g.situacao != "Pendente"].assign(Tipo="Realizado", ini=lambda x: x.real_inicio, fim=lambda x: x.real_fim.clip(upper=agora))

    fig_gantt = px.timeline(pd.concat([plan, real]), x_start="ini", x_end="fim", y="etapa", color="Tipo",
                            color_discrete_map={"Planejado": "#9ca3af", "Realizado": "#2563eb"}, category_orders={"etapa": list(g.etapa)})
    fig_gantt.update_yaxes(autorange="reversed", title="")
    fig_gantt.update_traces(width=0.6) 
    fig_gantt.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    for x_val, nome, cor in [(agora, "Agora", "#dc2626"), (prazo_op, "Prazo", "#16a34a")]:
        fig_gantt.add_shape(type="line", x0=x_val, x1=x_val, y0=0, y1=1, yref="paper", line=dict(color=cor, dash="dot", width=2))
        fig_gantt.add_annotation(x=x_val, y=1.05, yref="paper", text=nome, showarrow=False, font=dict(color=cor, weight="bold"))
    st.plotly_chart(fig_gantt, use_container_width=True, theme="streamlit")
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("<h3 style='font-weight: 900; color: var(--text-color);'><i class='bi bi-dice-5-fill' style='color: #2563eb; margin-right: 10px;'></i>Simulação de Monte Carlo</h3>", unsafe_allow_html=True)
    
    t0_mc, tot_mc = distribuicao_mc(d, agora, op)
    if tot_mc is None:
        st.info("Esta ordem já foi concluída — não há o que simular.")
    else:
        concl = t0_mc + pd.to_timedelta(tot_mc, unit="m")
        prob = float(np.mean(concl > prazo_op))
        p50 = t0_mc + pd.Timedelta(minutes=float(np.percentile(tot_mc, 50)))
        p90 = t0_mc + pd.Timedelta(minutes=float(np.percentile(tot_mc, 90)))
        
        mc1, mc2, mc3 = st.columns(3)
        with mc1: bento_kpi("Risco de Atraso", f"{prob:.0%}", "Probabilidade")
        with mc2: bento_kpi("Conclusão Estimada", f"{p50:%H:%M}", "Cenário P50")
        with mc3: bento_kpi("Cenário Pessimista", f"{p90:%H:%M}", "Cenário P90")
        
        st.write("")
        h = px.histogram(x=pd.Series(concl), nbins=40)
        h.update_traces(marker_color="#2563eb")
        h.add_shape(type="line", x0=prazo_op, x1=prazo_op, y0=0, y1=1, yref="paper", line=dict(color="#dc2626", dash="dash", width=2))
        h.add_annotation(x=prazo_op, y=1.05, yref="paper", text="Prazo Limite", showarrow=False, font=dict(color="#dc2626", weight="bold"))
        h.update_layout(yaxis_title="Simulações", xaxis_title="Horário de Término", showlegend=False, height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(h, use_container_width=True, theme="streamlit")

# ------------------------------------------------------ AGENDAMENTO REVERSO
with tab3:
    st.markdown("<h3 style='font-weight: 900; color: var(--text-color);'><i class='bi bi-clock-history' style='color: #2563eb; margin-right: 10px;'></i>Calculadora de Planejamento Reverso</h3>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    prod = c1.selectbox("Produto", list(ROTEIROS))
    dia = c2.date_input("Data de entrega", datetime(2026, 10, 6).date())
    hora = c3.time_input("Hora de entrega", time(18, 0))
    buf = c4.number_input("Folga (min)", 0, 120, BUFFER_MIN)
    st.markdown("</div>", unsafe_allow_html=True)
    
    prazo = datetime.combine(dia, hora)
    plano = pd.DataFrame(agendamento_reverso(prazo, ROTEIROS[prod], buf))
    inicio_total = plano.plan_inicio.min()
    
    m1, m2, m3 = st.columns([1,1,2])
    with m1: bento_kpi("Início Limite", f"{inicio_total:%H:%M}", f"Dia {inicio_total:%d/%m}")
    with m2: bento_kpi("Duração Total", f"{(prazo - inicio_total).total_seconds() / 3600:.1f} h", "Lead Time")
    
    st.write("")
    f = px.timeline(plano, x_start="plan_inicio", x_end="plan_fim", y="etapa", color="recurso", category_orders={"etapa": list(plano.etapa)})
    f.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(f.update_yaxes(autorange="reversed", title=""), use_container_width=True, theme="streamlit")

# ------------------------------------------------------------ SIMULAR ATRASO
with tab4:
    st.markdown("<h3 style='font-weight: 900; color: var(--text-color);'><i class='bi bi-sliders' style='color: #2563eb; margin-right: 10px;'></i>Cenário 'What-if' (E se...)</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    op_s = c1.selectbox("Ordem", r.op, key="op_sim")
    plano_op = (df[df.op == op_s].sort_values("ordem_etapa"))
    etapa_s = c2.selectbox("Etapa afetada", list(plano_op.etapa))
    atraso = c3.slider("Atraso inserido (min)", 0, 600, 120, 15)
    st.markdown("</div>", unsafe_allow_html=True)
    
    ordem_s = int(plano_op[plano_op.etapa == etapa_s].ordem_etapa.iloc[0])
    novo = reprogramar(plano_op, ordem_s, atraso)
    prazo_s = plano_op.prazo.iloc[0]
    estouro = (novo.novo_fim.iloc[-1] - prazo_s).total_seconds() / 60
    
    if estouro > 0:
        st.error(f"🛑 O atraso propaga em cascata! Conclusão passa para **{novo.novo_fim.iloc[-1]:%H:%M}** ({estouro:.0f} min após o prazo).")
    else:
        st.success("✅ O atraso é absorvido pelas folgas e não compromete o prazo de entrega.")
        
    st.dataframe(novo[["etapa", "recurso", "plan_inicio", "novo_inicio", "plan_fim", "novo_fim"]].round(1), hide_index=True, use_container_width=True, height=500)

# ------------------------------------------------------------------ DADOS
with tab5:
    st.markdown("<h3 style='font-weight: 900; color: var(--text-color);'><i class='bi bi-database-fill' style='color: #2563eb; margin-right: 10px;'></i>Base de Dados</h3>", unsafe_allow_html=True)
    st.dataframe(d, hide_index=True, use_container_width=True, height=500)
    st.download_button("Baixar dados (CSV)", d.to_csv(index=False).encode("utf-8"), "dados_reversemilk.csv", "text/csv")