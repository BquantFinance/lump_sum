"""
LUMP SUM vs DCA - Interactive Backtest Dashboard
=================================================
App de Streamlit con estética dark mode para análisis
de estrategias de inversión.

Requisitos: pip install streamlit yfinance pandas numpy plotly

Ejecutar: streamlit run app_lumpsum_dca.py

Autor: BQuant Finance
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURACIÓN DE PÁGINA
# =============================================================================

st.set_page_config(
    page_title="Lump Sum vs DCA | BQuant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# ESTILOS CSS - DARK MODE
# =============================================================================

st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d0d14 100%);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f18 0%, #151520 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.15);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #f8fafc !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        background: linear-gradient(135deg, #818cf8 0%, #6366f1 50%, #4f46e5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
    }
    
    /* Text */
    p, span, label, .stMarkdown {
        font-family: 'JetBrains Mono', monospace !important;
        color: #cbd5e1;
    }
    
    /* Metrics containers */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #1a1a2e 0%, #16162a 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    div[data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Positive/Negative delta colors */
    div[data-testid="stMetricDelta"] > div {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(145deg, #1e1e32 0%, #1a1a2e 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .metric-card-highlight {
        background: linear-gradient(145deg, #1e1e3f 0%, #252547 100%);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }
    
    .metric-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }
    
    .metric-value-green {
        color: #4ade80;
    }
    
    .metric-value-red {
        color: #f87171;
    }
    
    .metric-value-blue {
        color: #818cf8;
    }
    
    .metric-value-amber {
        color: #fbbf24;
    }
    
    .metric-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    /* Separator */
    .separator {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(99, 102, 241, 0.3) 50%, transparent 100%);
        margin: 32px 0;
    }
    
    /* Section headers */
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Slider styling */
    .stSlider > div > div {
        background-color: rgba(99, 102, 241, 0.3) !important;
    }
    
    .stSlider > div > div > div {
        background-color: #6366f1 !important;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background-color: #1a1a2e !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
        color: #e2e8f0 !important;
    }
    
    /* Number input */
    .stNumberInput > div > div > input {
        background-color: #1a1a2e !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
        color: #e2e8f0 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0f;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3730a3;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4338ca;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a2e;
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3730a3 !important;
        border-color: #6366f1 !important;
        color: #f8fafc !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a2e !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #e2e8f0 !important;
    }
    
    /* Winner badge */
    .winner-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .winner-ls {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        color: #a7f3d0;
        border: 1px solid #34d399;
    }
    
    .winner-dca {
        background: linear-gradient(135deg, #7c2d12 0%, #9a3412 100%);
        color: #fed7aa;
        border: 1px solid #fb923c;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# FUNCIONES DE CÁLCULO
# =============================================================================

# Tramos IRPF España
TRAMOS_IRPF = [
    (6_000, 0.19),
    (44_000, 0.21),
    (150_000, 0.23),
    (float('inf'), 0.27)
]

def calcular_impuestos_españa(plusvalia):
    """Calcula impuestos sobre plusvalías según tramos IRPF España."""
    if plusvalia <= 0:
        return 0, {}
    
    impuesto = 0
    restante = plusvalia
    limite_anterior = 0
    desglose = {}
    
    for limite, tipo in TRAMOS_IRPF:
        tramo = min(restante, limite - limite_anterior)
        if tramo > 0:
            imp_tramo = tramo * tipo
            impuesto += imp_tramo
            desglose[f"{int(tipo*100)}%"] = imp_tramo
            restante -= tramo
            limite_anterior = limite
        if restante <= 0:
            break
    
    return impuesto, desglose


def simular_estrategia(precios, capital, comision, slippage, meses_dca=None):
    """
    Simula Lump Sum (meses_dca=None) o DCA.
    Retorna serie temporal de valor y desglose de costes.
    """
    coste_op = comision + slippage
    
    if meses_dca is None or meses_dca == 0:
        # LUMP SUM
        capital_efectivo = capital * (1 - coste_op)
        comisiones_totales = capital * comision
        slippage_total = capital * slippage
        
        participaciones = capital_efectivo / precios.iloc[0]
        valores = participaciones * precios
        
        num_operaciones = 1
        
    else:
        # DCA
        aportacion = capital / meses_dca
        dias_entre = 21
        
        participaciones = 0
        comisiones_totales = 0
        slippage_total = 0
        valores = pd.Series(index=precios.index, dtype=float)
        capital_invertido_acum = 0
        num_operaciones = 0
        
        for mes in range(meses_dca):
            idx = mes * dias_entre
            if idx >= len(precios):
                break
            
            comision_op = aportacion * comision
            slippage_op = aportacion * slippage
            capital_efectivo = aportacion - comision_op - slippage_op
            
            participaciones += capital_efectivo / precios.iloc[idx]
            comisiones_totales += comision_op
            slippage_total += slippage_op
            capital_invertido_acum += aportacion
            num_operaciones += 1
        
        valores = participaciones * precios
    
    # Calcular valor final y costes de venta
    valor_bruto_final = valores.iloc[-1]
    comision_venta = valor_bruto_final * comision
    slippage_venta = valor_bruto_final * slippage
    valor_tras_venta = valor_bruto_final - comision_venta - slippage_venta
    
    comisiones_totales += comision_venta
    slippage_total += slippage_venta
    num_operaciones += 1
    
    # Impuestos
    plusvalia = valor_tras_venta - capital
    impuestos, desglose_imp = calcular_impuestos_españa(plusvalia)
    
    valor_neto = valor_tras_venta - impuestos
    rentabilidad = (valor_neto / capital - 1) * 100
    
    return {
        'valores': valores,
        'valor_bruto': valor_bruto_final,
        'valor_neto': valor_neto,
        'rentabilidad': rentabilidad,
        'plusvalia': plusvalia,
        'comisiones': comisiones_totales,
        'slippage': slippage_total,
        'impuestos': impuestos,
        'desglose_impuestos': desglose_imp,
        'num_operaciones': num_operaciones,
        'coste_total': comisiones_totales + slippage_total + impuestos
    }


@st.cache_data(ttl=3600)
def descargar_datos(ticker, fecha_inicio):
    """Descarga datos con caché."""
    data = yf.download(ticker, start=fecha_inicio, progress=False, multi_level_index=False)
    return data['Close'].dropna()


# =============================================================================
# SIDEBAR - PARÁMETROS
# =============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="margin: 0; font-size: 1.5rem;">📊 BQuant Finance</h2>
        <p style="color: #64748b; font-size: 0.8rem; margin-top: 8px;">Lump Sum vs DCA Backtest</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Capital
    st.markdown("##### 💰 Capital inicial")
    capital = st.number_input(
        "Capital (€)",
        min_value=1000,
        max_value=10_000_000,
        value=100_000,
        step=10000,
        label_visibility="collapsed"
    )
    
    st.markdown("##### 📅 Horizonte temporal")
    horizonte = st.slider(
        "Años de inversión",
        min_value=1,
        max_value=30,
        value=10,
        label_visibility="collapsed"
    )
    
    st.markdown("##### 🔄 Período DCA")
    meses_dca = st.selectbox(
        "Meses para DCA",
        options=[6, 12, 18, 24, 36],
        index=1,
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    st.markdown("##### 💸 Costes de transacción")
    
    comision = st.slider(
        "Comisión (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.05,
        format="%.2f%%"
    ) / 100
    
    slippage = st.slider(
        "Slippage (%)",
        min_value=0.0,
        max_value=0.5,
        value=0.05,
        step=0.01,
        format="%.2f%%"
    ) / 100
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    st.markdown("##### 📈 Activo")
    ticker_options = {
        "S&P 500": "^GSPC",
        "NASDAQ 100": "^NDX",
        "MSCI World (VT)": "VT",
        "Euro Stoxx 50": "^STOXX50E"
    }
    ticker_name = st.selectbox(
        "Índice",
        options=list(ticker_options.keys()),
        index=0,
        label_visibility="collapsed"
    )
    ticker = ticker_options[ticker_name]
    
    fecha_inicio = st.date_input(
        "Fecha inicio simulación",
        value=datetime(2010, 1, 1),
        min_value=datetime(1980, 1, 1),
        max_value=datetime.now() - timedelta(days=365*horizonte)
    )


# =============================================================================
# MAIN CONTENT
# =============================================================================

# Header
st.markdown("""
<h1 style="font-size: 2.5rem; margin-bottom: 8px;">
    Lump Sum vs Dollar Cost Averaging
</h1>
<p style="color: #64748b; font-size: 1rem; margin-bottom: 32px;">
    Análisis con costes reales: comisiones, slippage e impuestos IRPF España
</p>
""", unsafe_allow_html=True)

# Cargar datos
try:
    with st.spinner("Descargando datos..."):
        precios_full = descargar_datos(ticker, str(fecha_inicio))
    
    # Recortar al horizonte
    dias_horizonte = horizonte * 252
    if len(precios_full) < dias_horizonte:
        st.error(f"No hay suficientes datos para {horizonte} años desde {fecha_inicio}")
        st.stop()
    
    precios = precios_full.iloc[:dias_horizonte+1]
    
    # Simular estrategias
    resultado_ls = simular_estrategia(precios, capital, comision, slippage, meses_dca=None)
    resultado_dca = simular_estrategia(precios, capital, comision, slippage, meses_dca=meses_dca)
    
    # Determinar ganador
    ganador = "LS" if resultado_ls['rentabilidad'] > resultado_dca['rentabilidad'] else "DCA"
    diferencia = resultado_ls['rentabilidad'] - resultado_dca['rentabilidad']
    
    # ==========================================================================
    # MÉTRICAS PRINCIPALES
    # ==========================================================================
    
    st.markdown('<div class="section-header">📊 Resultados de la simulación</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        color_ls = "metric-value-green" if resultado_ls['rentabilidad'] > 0 else "metric-value-red"
        badge_ls = '<span class="winner-badge winner-ls">GANADOR</span>' if ganador == "LS" else ""
        st.markdown(f"""
        <div class="metric-card-highlight">
            <div class="metric-title">LUMP SUM {badge_ls}</div>
            <div class="metric-value {color_ls}">{resultado_ls['rentabilidad']:+.1f}%</div>
            <div class="metric-subtitle">{resultado_ls['valor_neto']:,.0f}€ neto</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color_dca = "metric-value-green" if resultado_dca['rentabilidad'] > 0 else "metric-value-red"
        badge_dca = '<span class="winner-badge winner-dca">GANADOR</span>' if ganador == "DCA" else ""
        st.markdown(f"""
        <div class="metric-card-highlight">
            <div class="metric-title">DCA {meses_dca} MESES {badge_dca}</div>
            <div class="metric-value {color_dca}">{resultado_dca['rentabilidad']:+.1f}%</div>
            <div class="metric-subtitle">{resultado_dca['valor_neto']:,.0f}€ neto</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color_diff = "metric-value-blue" if diferencia > 0 else "metric-value-amber"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">DIFERENCIA (LS - DCA)</div>
            <div class="metric-value {color_diff}">{diferencia:+.1f} pp</div>
            <div class="metric-subtitle">{abs(resultado_ls['valor_neto'] - resultado_dca['valor_neto']):,.0f}€</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # ==========================================================================
    # GRÁFICO PRINCIPAL
    # ==========================================================================
    
    st.markdown('<div class="section-header">📈 Evolución del patrimonio</div>', unsafe_allow_html=True)
    
    # Preparar datos para gráfico
    rentabilidad_ls = (resultado_ls['valores'] / capital - 1) * 100
    rentabilidad_dca = (resultado_dca['valores'] / capital - 1) * 100
    
    fig = go.Figure()
    
    # Área bajo LS
    fig.add_trace(go.Scatter(
        x=rentabilidad_ls.index,
        y=rentabilidad_ls.values,
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.15)',
        line=dict(color='#818cf8', width=2.5),
        name='Lump Sum',
        hovertemplate='<b>Lump Sum</b><br>%{x|%Y-%m-%d}<br>Rentabilidad: %{y:.1f}%<extra></extra>'
    ))
    
    # Área bajo DCA
    fig.add_trace(go.Scatter(
        x=rentabilidad_dca.index,
        y=rentabilidad_dca.values,
        fill='tozeroy',
        fillcolor='rgba(251, 146, 60, 0.15)',
        line=dict(color='#fb923c', width=2.5),
        name=f'DCA {meses_dca}m',
        hovertemplate=f'<b>DCA {meses_dca}m</b><br>%{{x|%Y-%m-%d}}<br>Rentabilidad: %{{y:.1f}}%<extra></extra>'
    ))
    
    # Línea de 0
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(148, 163, 184, 0.5)", line_width=1)
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="JetBrains Mono", color="#e2e8f0"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(99, 102, 241, 0.1)',
            zeroline=False,
            title=None
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(99, 102, 241, 0.1)',
            zeroline=False,
            title="Rentabilidad (%)",
            ticksuffix="%"
        ),
        margin=dict(l=60, r=20, t=40, b=40),
        height=450,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # ==========================================================================
    # DESGLOSE DE COSTES
    # ==========================================================================
    
    st.markdown('<div class="section-header">💸 Desglose de costes</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Lump Sum", "📊 DCA"])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">COMISIONES</div>
                <div class="metric-value metric-value-amber">{resultado_ls['comisiones']:,.0f}€</div>
                <div class="metric-subtitle">{resultado_ls['num_operaciones']} operaciones</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">SLIPPAGE</div>
                <div class="metric-value metric-value-amber">{resultado_ls['slippage']:,.0f}€</div>
                <div class="metric-subtitle">{slippage*100:.2f}% por op.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">IMPUESTOS IRPF</div>
                <div class="metric-value metric-value-red">{resultado_ls['impuestos']:,.0f}€</div>
                <div class="metric-subtitle">Plusvalía: {resultado_ls['plusvalia']:,.0f}€</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            pct_coste = (resultado_ls['coste_total'] / resultado_ls['valor_bruto']) * 100 if resultado_ls['valor_bruto'] > 0 else 0
            st.markdown(f"""
            <div class="metric-card-highlight">
                <div class="metric-title">COSTE TOTAL</div>
                <div class="metric-value">{resultado_ls['coste_total']:,.0f}€</div>
                <div class="metric-subtitle">{pct_coste:.1f}% del valor bruto</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Desglose impuestos
        if resultado_ls['desglose_impuestos']:
            with st.expander("📋 Desglose IRPF por tramos"):
                for tramo, importe in resultado_ls['desglose_impuestos'].items():
                    st.markdown(f"**Tramo {tramo}:** {importe:,.0f}€")
    
    with tab2:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">COMISIONES</div>
                <div class="metric-value metric-value-amber">{resultado_dca['comisiones']:,.0f}€</div>
                <div class="metric-subtitle">{resultado_dca['num_operaciones']} operaciones</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">SLIPPAGE</div>
                <div class="metric-value metric-value-amber">{resultado_dca['slippage']:,.0f}€</div>
                <div class="metric-subtitle">{slippage*100:.2f}% por op.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">IMPUESTOS IRPF</div>
                <div class="metric-value metric-value-red">{resultado_dca['impuestos']:,.0f}€</div>
                <div class="metric-subtitle">Plusvalía: {resultado_dca['plusvalia']:,.0f}€</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            pct_coste_dca = (resultado_dca['coste_total'] / resultado_dca['valor_bruto']) * 100 if resultado_dca['valor_bruto'] > 0 else 0
            st.markdown(f"""
            <div class="metric-card-highlight">
                <div class="metric-title">COSTE TOTAL</div>
                <div class="metric-value">{resultado_dca['coste_total']:,.0f}€</div>
                <div class="metric-subtitle">{pct_coste_dca:.1f}% del valor bruto</div>
            </div>
            """, unsafe_allow_html=True)
        
        if resultado_dca['desglose_impuestos']:
            with st.expander("📋 Desglose IRPF por tramos"):
                for tramo, importe in resultado_dca['desglose_impuestos'].items():
                    st.markdown(f"**Tramo {tramo}:** {importe:,.0f}€")
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # ==========================================================================
    # GRÁFICO COMPARATIVO DE COSTES
    # ==========================================================================
    
    st.markdown('<div class="section-header">📊 Comparativa de costes</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras de costes
        categorias = ['Comisiones', 'Slippage', 'Impuestos']
        valores_ls = [resultado_ls['comisiones'], resultado_ls['slippage'], resultado_ls['impuestos']]
        valores_dca = [resultado_dca['comisiones'], resultado_dca['slippage'], resultado_dca['impuestos']]
        
        fig_costes = go.Figure()
        
        fig_costes.add_trace(go.Bar(
            name='Lump Sum',
            x=categorias,
            y=valores_ls,
            marker_color='#818cf8',
            text=[f'{v:,.0f}€' for v in valores_ls],
            textposition='auto',
            textfont=dict(color='white', size=12)
        ))
        
        fig_costes.add_trace(go.Bar(
            name=f'DCA {meses_dca}m',
            x=categorias,
            y=valores_dca,
            marker_color='#fb923c',
            text=[f'{v:,.0f}€' for v in valores_dca],
            textposition='auto',
            textfont=dict(color='white', size=12)
        ))
        
        fig_costes.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="JetBrains Mono", color="#e2e8f0"),
            barmode='group',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(showgrid=False),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(99, 102, 241, 0.1)',
                title="€"
            ),
            margin=dict(l=60, r=20, t=60, b=40),
            height=350
        )
        
        st.plotly_chart(fig_costes, use_container_width=True)
    
    with col2:
        # Donut chart de distribución de costes LS
        fig_donut = go.Figure()
        
        labels = ['Comisiones', 'Slippage', 'Impuestos', 'Neto']
        values_ls = [
            resultado_ls['comisiones'],
            resultado_ls['slippage'],
            resultado_ls['impuestos'],
            resultado_ls['valor_neto']
        ]
        colors = ['#fbbf24', '#f97316', '#ef4444', '#4ade80']
        
        fig_donut.add_trace(go.Pie(
            labels=labels,
            values=values_ls,
            hole=0.6,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=11, color='#e2e8f0'),
            hovertemplate='<b>%{label}</b><br>%{value:,.0f}€<br>%{percent}<extra></extra>'
        ))
        
        fig_donut.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="JetBrains Mono", color="#e2e8f0"),
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
            height=350,
            annotations=[dict(
                text=f'<b>LS</b><br>{resultado_ls["valor_neto"]:,.0f}€',
                x=0.5, y=0.5,
                font_size=16,
                font_color='#e2e8f0',
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
    
    # ==========================================================================
    # RESUMEN FINAL
    # ==========================================================================
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">📝 Resumen de la simulación</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p><strong>📅 Período:</strong> {precios.index[0].strftime('%Y-%m-%d')} → {precios.index[-1].strftime('%Y-%m-%d')}</p>
            <p><strong>📈 Activo:</strong> {ticker_name} ({ticker})</p>
            <p><strong>💰 Capital inicial:</strong> {capital:,.0f}€</p>
            <p><strong>⏱️ Horizonte:</strong> {horizonte} años</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p><strong>🏆 Ganador:</strong> {'Lump Sum' if ganador == 'LS' else f'DCA {meses_dca} meses'}</p>
            <p><strong>📊 Ventaja:</strong> {abs(diferencia):.1f} puntos porcentuales</p>
            <p><strong>💵 Diferencia neta:</strong> {abs(resultado_ls['valor_neto'] - resultado_dca['valor_neto']):,.0f}€</p>
            <p><strong>📉 Coste total LS/DCA:</strong> {resultado_ls['coste_total']:,.0f}€ / {resultado_dca['coste_total']:,.0f}€</p>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")
    st.info("Verifica que el ticker sea válido y tengas conexión a internet.")

# Footer
st.markdown("""
<div style="text-align: center; padding: 40px 0 20px 0; color: #475569;">
    <p style="font-size: 0.8rem;">Desarrollado por <strong>BQuant Finance</strong> | Los resultados pasados no garantizan rendimientos futuros</p>
</div>
""", unsafe_allow_html=True)
