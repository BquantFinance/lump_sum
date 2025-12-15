"""
LUMP SUM vs DCA - Interactive Backtest Dashboard v3
====================================================
Comparativa realista con:
- Coste de oportunidad del capital no invertido (DCA)
- Ticker libre (cualquier activo de Yahoo Finance)
- Tramos IRPF España 2024
- Costes de transacción realistas

Autor: BQuant Finance
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d0d14 100%);
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f18 0%, #151520 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.15);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
    
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
    
    p, label, .stMarkdown {
        font-family: 'JetBrains Mono', monospace !important;
        color: #cbd5e1;
    }
    
    span:not([data-testid="stIconMaterial"]) {
        font-family: 'JetBrains Mono', monospace !important;
        color: #cbd5e1;
    }
    
    [data-testid="stIconMaterial"], 
    [data-testid="collapsedControl"],
    .material-symbols-rounded,
    .material-icons {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #1a1a2e 0%, #16162a 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .metric-card {
        background: linear-gradient(145deg, #1e1e32 0%, #1a1a2e 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    .metric-card-highlight {
        background: linear-gradient(145deg, #1e1e3f 0%, #252547 100%);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
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
    
    .metric-value-green { color: #4ade80; }
    .metric-value-red { color: #f87171; }
    .metric-value-blue { color: #818cf8; }
    .metric-value-amber { color: #fbbf24; }
    
    .metric-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    .separator {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(99, 102, 241, 0.3) 50%, transparent 100%);
        margin: 32px 0;
    }
    
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3);
    }
    
    .stSlider > div > div {
        background-color: rgba(99, 102, 241, 0.3) !important;
    }
    
    .stSlider > div > div > div {
        background-color: #6366f1 !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a2e;
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3730a3 !important;
        border-color: #6366f1 !important;
        color: #f8fafc !important;
    }
    
    .winner-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
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
    
    .disclaimer-box {
        background: linear-gradient(145deg, #1e1e32 0%, #1a1a2e 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 0 12px 12px 0;
        padding: 16px;
        margin: 16px 0;
        font-size: 0.85rem;
    }
    
    .info-box {
        background: linear-gradient(145deg, #1e3a5f 0%, #1e3a8a 100%);
        border: 1px solid rgba(59, 130, 246, 0.4);
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# CONSTANTES Y FUNCIONES DE CÁLCULO
# =============================================================================

# Tramos IRPF España 2024 - Base del Ahorro
TRAMOS_IRPF_2024 = [
    (6_000, 0.19),
    (50_000, 0.21),
    (200_000, 0.23),
    (300_000, 0.27),
    (float('inf'), 0.28)
]


def calcular_impuestos_españa(plusvalia: float) -> tuple[float, dict]:
    """
    Calcula impuestos sobre plusvalías según tramos IRPF España 2024.
    Solo se pagan impuestos si hay plusvalía positiva.
    """
    if plusvalia <= 0:
        return 0.0, {}
    
    impuesto_total = 0.0
    restante = plusvalia
    limite_anterior = 0.0
    desglose = {}
    
    for limite_superior, tipo in TRAMOS_IRPF_2024:
        ancho_tramo = limite_superior - limite_anterior
        base_en_tramo = min(restante, ancho_tramo)
        
        if base_en_tramo > 0:
            impuesto_tramo = base_en_tramo * tipo
            impuesto_total += impuesto_tramo
            desglose[f"{int(tipo * 100)}%"] = {
                'base': base_en_tramo,
                'impuesto': impuesto_tramo
            }
            restante -= base_en_tramo
            limite_anterior = limite_superior
        
        if restante <= 0:
            break
    
    return impuesto_total, desglose


def calcular_max_drawdown(serie: pd.Series) -> tuple[float, datetime, datetime]:
    """Calcula Maximum Drawdown de una serie."""
    rolling_max = serie.expanding().max()
    drawdowns = (serie - rolling_max) / rolling_max
    max_dd = drawdowns.min()
    idx_valle = drawdowns.idxmin()
    idx_pico = serie.loc[:idx_valle].idxmax()
    return max_dd * 100, idx_pico, idx_valle


def calcular_cagr(valor_inicial: float, valor_final: float, años: float) -> float:
    """Calcula CAGR (Tasa de Crecimiento Anual Compuesta)."""
    if valor_inicial <= 0 or años <= 0:
        return 0.0
    return ((valor_final / valor_inicial) ** (1 / años) - 1) * 100


def simular_lump_sum(
    precios: pd.Series,
    capital: float,
    comision: float,
    slippage: float
) -> dict:
    """
    Simula estrategia Lump Sum: invertir todo el capital al inicio.
    
    Flujo:
    1. Día 0: Comprar con todo el capital (menos costes)
    2. Día final: Vender todo (menos costes)
    3. Calcular impuestos sobre plusvalía
    """
    # === COMPRA ===
    coste_compra = capital * (comision + slippage)
    capital_invertido = capital - coste_compra
    
    precio_compra = precios.iloc[0]
    participaciones = capital_invertido / precio_compra
    
    # === EVOLUCIÓN ===
    valores = participaciones * precios
    
    # === VENTA ===
    valor_bruto_final = valores.iloc[-1]
    coste_venta = valor_bruto_final * (comision + slippage)
    valor_tras_venta = valor_bruto_final - coste_venta
    
    # === IMPUESTOS ===
    plusvalia = valor_tras_venta - capital  # Base de coste = capital inicial
    impuestos, desglose_imp = calcular_impuestos_españa(plusvalia)
    
    # === RESULTADO NETO ===
    valor_neto = valor_tras_venta - impuestos
    
    # === MÉTRICAS ===
    dias = (precios.index[-1] - precios.index[0]).days
    años = dias / 365.25
    rentabilidad = (valor_neto / capital - 1) * 100
    cagr = calcular_cagr(capital, valor_neto, años)
    max_dd, fecha_pico, fecha_valle = calcular_max_drawdown(valores)
    
    return {
        'valores': valores,
        'valor_bruto': valor_bruto_final,
        'valor_tras_venta': valor_tras_venta,
        'valor_neto': valor_neto,
        'rentabilidad': rentabilidad,
        'cagr': cagr,
        'max_drawdown': max_dd,
        'fecha_pico_dd': fecha_pico,
        'fecha_valle_dd': fecha_valle,
        'base_coste': capital,
        'plusvalia': plusvalia,
        'impuestos': impuestos,
        'desglose_impuestos': desglose_imp,
        'tipo_efectivo': (impuestos / plusvalia * 100) if plusvalia > 0 else 0,
        'comision_compra': capital * comision,
        'slippage_compra': capital * slippage,
        'comision_venta': valor_bruto_final * comision,
        'slippage_venta': valor_bruto_final * slippage,
        'costes_transaccion': coste_compra + coste_venta,
        'coste_total': coste_compra + coste_venta + impuestos,
        'num_operaciones': 2,
        'precio_medio': precio_compra,
        'años': años,
        'intereses_monetario': 0,  # No aplica a LS
        'capital_invertido': capital
    }


def simular_dca(
    precios: pd.Series,
    capital: float,
    meses_dca: int,
    comision: float,
    slippage: float,
    tasa_monetario: float
) -> dict:
    """
    Simula estrategia DCA con coste de oportunidad.
    
    Flujo:
    1. Cada mes: invertir capital/meses_dca (menos costes)
    2. Capital pendiente genera intereses en monetario
    3. Día final: Vender todo (menos costes)
    4. Calcular impuestos sobre plusvalía
    
    Args:
        tasa_monetario: Tasa anual del fondo monetario (ej: 0.035 = 3.5%)
    """
    aportacion = capital / meses_dca
    dias_entre_aportaciones = 21  # ~1 mes de trading
    tasa_mensual = tasa_monetario / 12
    
    # Tracking
    participaciones = 0.0
    capital_invertido_total = 0.0
    comisiones_compra = 0.0
    slippage_compra = 0.0
    intereses_monetario = 0.0
    precios_compra = []
    cantidades_compra = []
    num_compras = 0
    
    # Capital pendiente de invertir (empieza con todo)
    capital_pendiente = capital
    
    for mes in range(meses_dca):
        idx = mes * dias_entre_aportaciones
        if idx >= len(precios):
            break
        
        # Intereses del capital pendiente este mes
        # (el mes 0 no genera intereses, empieza a invertir inmediatamente)
        if mes > 0:
            interes_mes = capital_pendiente * tasa_mensual
            intereses_monetario += interes_mes
        
        # Realizar compra
        coste_op = aportacion * (comision + slippage)
        capital_efectivo = aportacion - coste_op
        
        precio = precios.iloc[idx]
        nuevas_participaciones = capital_efectivo / precio
        
        participaciones += nuevas_participaciones
        capital_invertido_total += aportacion
        capital_pendiente -= aportacion
        comisiones_compra += aportacion * comision
        slippage_compra += aportacion * slippage
        num_compras += 1
        
        precios_compra.append(precio)
        cantidades_compra.append(nuevas_participaciones)
    
    # Intereses del capital restante hasta el final del período DCA
    # (si no se completaron todas las aportaciones)
    meses_restantes_dca = meses_dca - num_compras
    if capital_pendiente > 0 and meses_restantes_dca > 0:
        intereses_monetario += capital_pendiente * tasa_mensual * meses_restantes_dca
    
    # === EVOLUCIÓN ===
    valores = participaciones * precios
    
    # === VENTA ===
    valor_bruto_final = valores.iloc[-1]
    coste_venta = valor_bruto_final * (comision + slippage)
    valor_tras_venta = valor_bruto_final - coste_venta
    
    # === IMPUESTOS ===
    # Base de coste = capital efectivamente invertido en el activo
    plusvalia = valor_tras_venta - capital_invertido_total
    impuestos_activo, desglose_imp = calcular_impuestos_españa(plusvalia)
    
    # Impuestos sobre intereses del monetario (tributan como rendimiento)
    # Simplificación: mismo tipo marginal máximo alcanzado
    impuestos_intereses, _ = calcular_impuestos_españa(intereses_monetario)
    
    impuestos_totales = impuestos_activo + impuestos_intereses
    
    # === RESULTADO NETO ===
    # Valor final = valor activo + intereses monetario - impuestos totales
    valor_neto = valor_tras_venta + intereses_monetario - impuestos_totales
    
    # === MÉTRICAS ===
    dias = (precios.index[-1] - precios.index[0]).days
    años = dias / 365.25
    rentabilidad = (valor_neto / capital - 1) * 100
    cagr = calcular_cagr(capital, valor_neto, años)
    max_dd, fecha_pico, fecha_valle = calcular_max_drawdown(valores)
    
    # Precio medio ponderado
    if sum(cantidades_compra) > 0:
        precio_medio = sum(p * c for p, c in zip(precios_compra, cantidades_compra)) / sum(cantidades_compra)
    else:
        precio_medio = 0
    
    costes_compra_total = comisiones_compra + slippage_compra
    
    return {
        'valores': valores,
        'valor_bruto': valor_bruto_final,
        'valor_tras_venta': valor_tras_venta,
        'valor_neto': valor_neto,
        'rentabilidad': rentabilidad,
        'cagr': cagr,
        'max_drawdown': max_dd,
        'fecha_pico_dd': fecha_pico,
        'fecha_valle_dd': fecha_valle,
        'base_coste': capital_invertido_total,
        'plusvalia': plusvalia,
        'impuestos': impuestos_totales,
        'impuestos_activo': impuestos_activo,
        'impuestos_intereses': impuestos_intereses,
        'desglose_impuestos': desglose_imp,
        'tipo_efectivo': (impuestos_activo / plusvalia * 100) if plusvalia > 0 else 0,
        'comision_compra': comisiones_compra,
        'slippage_compra': slippage_compra,
        'comision_venta': valor_bruto_final * comision,
        'slippage_venta': valor_bruto_final * slippage,
        'costes_transaccion': costes_compra_total + coste_venta,
        'coste_total': costes_compra_total + coste_venta + impuestos_totales,
        'num_operaciones': num_compras + 1,
        'precio_medio': precio_medio,
        'años': años,
        'intereses_monetario': intereses_monetario,
        'capital_invertido': capital_invertido_total,
        'capital_no_invertido': capital - capital_invertido_total
    }


@st.cache_data(ttl=3600)
def descargar_datos(ticker: str, fecha_inicio: str) -> tuple[pd.Series, dict]:
    """
    Descarga datos y metadata del activo.
    Returns: (serie_precios, info_activo)
    """
    try:
        activo = yf.Ticker(ticker)
        data = activo.history(start=fecha_inicio, auto_adjust=True)
        
        if data.empty:
            return None, None
        
        info = activo.info
        return data['Close'].dropna(), info
    except Exception as e:
        return None, None


def validar_ticker(ticker: str) -> bool:
    """Valida que el ticker existe en Yahoo Finance."""
    try:
        activo = yf.Ticker(ticker)
        info = activo.info
        return info.get('regularMarketPrice') is not None or info.get('previousClose') is not None
    except:
        return False


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("""
<div style="text-align: center; padding: 20px 0;">
<h2 style="margin: 0; font-size: 1.5rem;">📊 BQuant Finance</h2>
<p style="color: #64748b; font-size: 0.8rem; margin-top: 8px;">Lump Sum vs DCA Backtest v3</p>
</div>
""", unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # === ACTIVO ===
    st.markdown("##### 📈 Activo")
    
    col_ticker, col_validar = st.columns([3, 1])
    with col_ticker:
        ticker_input = st.text_input(
            "Ticker Yahoo Finance",
            value="SPY",
            placeholder="SPY, AAPL, ^GSPC...",
            label_visibility="collapsed"
        ).upper().strip()
    
    # Sugerencias
    with st.expander("💡 Ejemplos de tickers"):
        st.markdown("""
        **ETFs populares:**
        - `SPY` - S&P 500
        - `QQQ` - NASDAQ 100
        - `VT` - Total World
        - `EEM` - Emergentes
        
        **Índices:**
        - `^GSPC` - S&P 500 Index
        - `^IBEX` - IBEX 35
        - `^STOXX50E` - Euro Stoxx 50
        
        **Acciones:**
        - `AAPL`, `MSFT`, `GOOGL`
        - `SAN.MC` (Santander Madrid)
        """)
    
    # Fecha inicio
    fecha_inicio = st.date_input(
        "Fecha inicio",
        value=datetime(2010, 1, 1),
        min_value=datetime(1990, 1, 1),
        max_value=datetime.now() - timedelta(days=365)
    )
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # === CAPITAL ===
    st.markdown("##### 💰 Capital inicial")
    capital = st.number_input(
        "Capital",
        min_value=1000,
        max_value=10_000_000,
        value=100_000,
        step=10000,
        label_visibility="collapsed"
    )
    
    # === HORIZONTE ===
    st.markdown("##### 📅 Horizonte temporal")
    
    # Calcular años disponibles
    años_disponibles = max(1, (datetime.now() - datetime.combine(fecha_inicio, datetime.min.time())).days // 365)
    horizonte_max = min(30, años_disponibles)
    
    horizonte = st.slider(
        "Años",
        min_value=1,
        max_value=horizonte_max,
        value=min(10, horizonte_max),
        label_visibility="collapsed"
    )
    
    if años_disponibles < 30:
        st.caption(f"ℹ️ Máx. {años_disponibles} años desde {fecha_inicio}")
    
    # === DCA ===
    st.markdown("##### 🔄 Período DCA")
    
    meses_horizonte = horizonte * 12
    meses_dca_max = min(60, meses_horizonte // 2)
    opciones_dca = [m for m in [3, 6, 12, 18, 24, 36, 48, 60] if m <= meses_dca_max] or [3]
    idx_default = opciones_dca.index(12) if 12 in opciones_dca else 0
    
    meses_dca = st.selectbox(
        "Meses DCA",
        options=opciones_dca,
        index=idx_default,
        label_visibility="collapsed"
    )
    
    st.caption(f"ℹ️ {meses_dca} meses = {(meses_dca/meses_horizonte)*100:.0f}% del horizonte")
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # === COSTES ===
    st.markdown("##### 💸 Costes de transacción")
    
    comision = st.slider(
        "Comisión (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.10,
        step=0.01,
        format="%.2f%%"
    ) / 100
    
    slippage = st.slider(
        "Slippage (%)",
        min_value=0.0,
        max_value=0.50,
        value=0.05,
        step=0.01,
        format="%.2f%%"
    ) / 100
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # === MONETARIO ===
    st.markdown("##### 🏦 Fondo monetario (DCA)")
    
    tasa_monetario = st.slider(
        "Rentabilidad anual (%)",
        min_value=0.0,
        max_value=6.0,
        value=3.5,
        step=0.1,
        format="%.1f%%",
        help="Rentabilidad del capital pendiente de invertir durante el período DCA"
    ) / 100
    
    st.caption("💡 Capital no invertido genera intereses")
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Info IRPF
    with st.expander("ℹ️ Tramos IRPF 2024"):
        st.markdown("""
**Base del Ahorro:**
- Hasta 6.000€: **19%**
- 6.000 - 50.000€: **21%**
- 50.000 - 200.000€: **23%**
- 200.000 - 300.000€: **27%**
- Más de 300.000€: **28%**
""")


# =============================================================================
# MAIN
# =============================================================================

st.markdown("""
<h1 style="font-size: 2.5rem; margin-bottom: 8px;">
Lump Sum vs Dollar Cost Averaging
</h1>
<p style="color: #64748b; font-size: 1rem; margin-bottom: 16px;">
Análisis con costes reales, coste de oportunidad e impuestos IRPF España 2024
</p>
""", unsafe_allow_html=True)

# Disclaimer divisa
st.markdown("""
<div class="disclaimer-box">
⚠️ <strong>Nota sobre divisas:</strong> Los datos provienen de Yahoo Finance en la divisa original del activo. 
Si inviertes en USD (ej: SPY) desde España, el resultado real dependerá también del tipo de cambio EUR/USD, 
que no está modelado aquí. Los cálculos de impuestos asumen conversión a EUR al tipo de cambio del momento.
</div>
""", unsafe_allow_html=True)

# Cargar datos
if not ticker_input:
    st.warning("Introduce un ticker válido")
    st.stop()

with st.spinner(f"Cargando datos de {ticker_input}..."):
    precios_full, info_activo = descargar_datos(ticker_input, str(fecha_inicio))

if precios_full is None or precios_full.empty:
    st.error(f"❌ No se encontraron datos para '{ticker_input}'. Verifica que el ticker sea válido en Yahoo Finance.")
    st.stop()

# Info del activo
nombre_activo = info_activo.get('shortName', ticker_input) if info_activo else ticker_input
divisa = info_activo.get('currency', 'N/A') if info_activo else 'N/A'
tipo_activo = info_activo.get('quoteType', 'N/A') if info_activo else 'N/A'

st.markdown(f"""
<div class="info-box">
<strong>📊 {nombre_activo}</strong> ({ticker_input})<br>
Tipo: {tipo_activo} | Divisa: <strong>{divisa}</strong> | Datos desde: {precios_full.index[0].strftime('%Y-%m-%d')}
</div>
""", unsafe_allow_html=True)

# Verificar datos suficientes
dias_horizonte = horizonte * 252
if len(precios_full) < dias_horizonte:
    dias_disponibles = len(precios_full)
    años_reales = dias_disponibles / 252
    st.warning(f"⚠️ Solo hay {dias_disponibles} días de trading (~{años_reales:.1f} años). Ajustando horizonte.")
    dias_horizonte = dias_disponibles - 1

precios = precios_full.iloc[:dias_horizonte + 1]

# === SIMULACIONES ===
resultado_ls = simular_lump_sum(precios, capital, comision, slippage)
resultado_dca = simular_dca(precios, capital, meses_dca, comision, slippage, tasa_monetario)

# Ganador
ganador = "LS" if resultado_ls['rentabilidad'] > resultado_dca['rentabilidad'] else "DCA"
diferencia_pp = resultado_ls['rentabilidad'] - resultado_dca['rentabilidad']
diferencia_euros = resultado_ls['valor_neto'] - resultado_dca['valor_neto']

# =============================================================================
# RESULTADOS PRINCIPALES
# =============================================================================

st.markdown('<div class="section-header">📊 Resultados de la simulación</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    color = "metric-value-green" if resultado_ls['rentabilidad'] > 0 else "metric-value-red"
    badge = '<span class="winner-badge winner-ls">GANADOR</span>' if ganador == "LS" else ""
    st.markdown(f"""
<div class="metric-card-highlight">
<div class="metric-title">LUMP SUM {badge}</div>
<div class="metric-value {color}">{resultado_ls['rentabilidad']:+.1f}%</div>
<div class="metric-subtitle">{resultado_ls['valor_neto']:,.0f} {divisa} neto | CAGR: {resultado_ls['cagr']:.1f}%</div>
</div>
""", unsafe_allow_html=True)

with col2:
    color = "metric-value-green" if resultado_dca['rentabilidad'] > 0 else "metric-value-red"
    badge = '<span class="winner-badge winner-dca">GANADOR</span>' if ganador == "DCA" else ""
    st.markdown(f"""
<div class="metric-card-highlight">
<div class="metric-title">DCA {meses_dca} MESES {badge}</div>
<div class="metric-value {color}">{resultado_dca['rentabilidad']:+.1f}%</div>
<div class="metric-subtitle">{resultado_dca['valor_neto']:,.0f} {divisa} neto | CAGR: {resultado_dca['cagr']:.1f}%</div>
</div>
""", unsafe_allow_html=True)

with col3:
    color = "metric-value-blue" if diferencia_pp > 0 else "metric-value-amber"
    ventaja = "LS" if diferencia_pp > 0 else "DCA"
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">VENTAJA {ventaja}</div>
<div class="metric-value {color}">{abs(diferencia_pp):.1f} pp</div>
<div class="metric-subtitle">{abs(diferencia_euros):,.0f} {divisa} diferencia</div>
</div>
""", unsafe_allow_html=True)

# Métricas secundarias
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">MAX DRAWDOWN LS</div>
<div class="metric-value metric-value-red">{resultado_ls['max_drawdown']:.1f}%</div>
<div class="metric-subtitle">{resultado_ls['fecha_valle_dd'].strftime('%Y-%m-%d')}</div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">MAX DRAWDOWN DCA</div>
<div class="metric-value metric-value-red">{resultado_dca['max_drawdown']:.1f}%</div>
<div class="metric-subtitle">{resultado_dca['fecha_valle_dd'].strftime('%Y-%m-%d')}</div>
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">PRECIO MEDIO LS</div>
<div class="metric-value metric-value-blue">{resultado_ls['precio_medio']:.2f}</div>
<div class="metric-subtitle">1 compra</div>
</div>
""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">PRECIO MEDIO DCA</div>
<div class="metric-value metric-value-amber">{resultado_dca['precio_medio']:.2f}</div>
<div class="metric-subtitle">{resultado_dca['num_operaciones']-1} compras</div>
</div>
""", unsafe_allow_html=True)

# Intereses monetario DCA
if resultado_dca['intereses_monetario'] > 0:
    st.markdown(f"""
<div class="info-box">
💰 <strong>Intereses monetario DCA:</strong> +{resultado_dca['intereses_monetario']:,.2f} {divisa} 
(capital pendiente al {tasa_monetario*100:.1f}% anual)
— Impuestos sobre intereses: -{resultado_dca['impuestos_intereses']:,.2f} {divisa}
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# =============================================================================
# GRÁFICO EVOLUCIÓN
# =============================================================================

st.markdown('<div class="section-header">📈 Evolución del patrimonio (antes de impuestos)</div>', unsafe_allow_html=True)

rentabilidad_ls = (resultado_ls['valores'] / capital - 1) * 100
rentabilidad_dca = (resultado_dca['valores'] / capital - 1) * 100

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=rentabilidad_ls.index,
    y=rentabilidad_ls.values,
    fill='tozeroy',
    fillcolor='rgba(99, 102, 241, 0.15)',
    line=dict(color='#818cf8', width=2.5),
    name='Lump Sum',
    hovertemplate='<b>Lump Sum</b><br>%{x|%Y-%m-%d}<br>Rentabilidad: %{y:.1f}%<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=rentabilidad_dca.index,
    y=rentabilidad_dca.values,
    fill='tozeroy',
    fillcolor='rgba(251, 146, 60, 0.15)',
    line=dict(color='#fb923c', width=2.5),
    name=f'DCA {meses_dca}m',
    hovertemplate=f'<b>DCA {meses_dca}m</b><br>%{{x|%Y-%m-%d}}<br>Rentabilidad: %{{y:.1f}}%<extra></extra>'
))

fig.add_hline(y=0, line_dash="dash", line_color="rgba(148, 163, 184, 0.5)", line_width=1)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="JetBrains Mono", color="#e2e8f0"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(showgrid=True, gridcolor='rgba(99, 102, 241, 0.1)', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='rgba(99, 102, 241, 0.1)', zeroline=False, title="Rentabilidad (%)", ticksuffix="%"),
    margin=dict(l=60, r=20, t=40, b=40),
    height=450,
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# =============================================================================
# DESGLOSE DE COSTES
# =============================================================================

st.markdown('<div class="section-header">💸 Desglose detallado de costes</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Lump Sum", "📊 DCA"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Costes de Transacción**")
        html = f'''<div class="metric-card">
<table style="width: 100%; border-collapse: collapse;">
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<td style="padding: 8px 0;">Comisión compra</td>
<td style="text-align: right; color: #fbbf24;">{resultado_ls['comision_compra']:,.2f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<td style="padding: 8px 0;">Slippage compra</td>
<td style="text-align: right; color: #fbbf24;">{resultado_ls['slippage_compra']:,.2f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<td style="padding: 8px 0;">Comisión venta</td>
<td style="text-align: right; color: #fbbf24;">{resultado_ls['comision_venta']:,.2f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<td style="padding: 8px 0;">Slippage venta</td>
<td style="text-align: right; color: #fbbf24;">{resultado_ls['slippage_venta']:,.2f} {divisa}</td>
</tr>
<tr>
<td style="padding: 8px 0; font-weight: bold;">Total transacción</td>
<td style="text-align: right; color: #f97316; font-weight: bold;">{resultado_ls['costes_transaccion']:,.2f} {divisa}</td>
</tr>
</table>
</div>'''
        st.markdown(html, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Impuestos IRPF**")
        filas = ""
        for tramo, datos in resultado_ls['desglose_impuestos'].items():
            filas += f'''<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<td style="padding: 8px 0;">Tramo {tramo}</td>
<td style="text-align: right; color: #94a3b8;">{datos['base']:,.0f} × {tramo}</td>
<td style="text-align: right; color: #ef4444;">{datos['impuesto']:,.2f}</td>
</tr>'''
        
        html = f'''<div class="metric-card">
<table style="width: 100%; border-collapse: collapse;">
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
<td style="padding: 8px 0;">Base coste</td>
<td colspan="2" style="text-align: right; color: #94a3b8;">{resultado_ls['base_coste']:,.0f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
<td style="padding: 8px 0;">Valor tras venta</td>
<td colspan="2" style="text-align: right; color: #94a3b8;">{resultado_ls['valor_tras_venta']:,.0f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
<td style="padding: 8px 0; font-weight: bold;">Plusvalía</td>
<td colspan="2" style="text-align: right; color: #4ade80; font-weight: bold;">{resultado_ls['plusvalia']:,.0f} {divisa}</td>
</tr>
{filas}
<tr>
<td style="padding: 8px 0; font-weight: bold;">Total impuestos</td>
<td style="text-align: right; color: #94a3b8;">({resultado_ls['tipo_efectivo']:.1f}%)</td>
<td style="text-align: right; color: #ef4444; font-weight: bold;">{resultado_ls['impuestos']:,.2f} {divisa}</td>
</tr>
</table>
</div>'''
        st.markdown(html, unsafe_allow_html=True)
    
    pct = (resultado_ls['coste_total'] / resultado_ls['valor_bruto']) * 100 if resultado_ls['valor_bruto'] > 0 else 0
    html = f'''<div class="metric-card-highlight">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<div class="metric-title">COSTE TOTAL LUMP SUM</div>
<div class="metric-value">{resultado_ls['coste_total']:,.0f} {divisa}</div>
</div>
<div style="text-align: right;">
<div class="metric-subtitle">{pct:.1f}% del valor bruto</div>
<div class="metric-subtitle">Transacción: {resultado_ls['costes_transaccion']:,.0f} | IRPF: {resultado_ls['impuestos']:,.0f}</div>
</div>
</div>
</div>'''
    st.markdown(html, unsafe_allow_html=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Costes de Transacción**")
        html = f'''<div class="metric-card">
<table style="width: 100%; border-collapse: collapse;">
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<td style="padding: 8px 0;">Comisiones compra ({resultado_dca['num_operaciones']-1} ops)</td>
<td style="text-align: right; color: #fbbf24;">{resultado_dca['comision_compra']:,.2f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<td style="padding: 8px 0;">Slippage compras</td>
<td style="text-align: right; color: #fbbf24;">{resultado_dca['slippage_compra']:,.2f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<td style="padding: 8px 0;">Comisión venta</td>
<td style="text-align: right; color: #fbbf24;">{resultado_dca['comision_venta']:,.2f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<td style="padding: 8px 0;">Slippage venta</td>
<td style="text-align: right; color: #fbbf24;">{resultado_dca['slippage_venta']:,.2f} {divisa}</td>
</tr>
<tr>
<td style="padding: 8px 0; font-weight: bold;">Total transacción</td>
<td style="text-align: right; color: #f97316; font-weight: bold;">{resultado_dca['costes_transaccion']:,.2f} {divisa}</td>
</tr>
</table>
</div>'''
        st.markdown(html, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Impuestos IRPF**")
        filas = ""
        for tramo, datos in resultado_dca['desglose_impuestos'].items():
            filas += f'''<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<td style="padding: 8px 0;">Tramo {tramo}</td>
<td style="text-align: right; color: #94a3b8;">{datos['base']:,.0f} × {tramo}</td>
<td style="text-align: right; color: #ef4444;">{datos['impuesto']:,.2f}</td>
</tr>'''
        
        html = f'''<div class="metric-card">
<table style="width: 100%; border-collapse: collapse;">
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
<td style="padding: 8px 0;">Capital invertido</td>
<td colspan="2" style="text-align: right; color: #94a3b8;">{resultado_dca['capital_invertido']:,.0f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
<td style="padding: 8px 0;">Valor tras venta</td>
<td colspan="2" style="text-align: right; color: #94a3b8;">{resultado_dca['valor_tras_venta']:,.0f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
<td style="padding: 8px 0; font-weight: bold;">Plusvalía activo</td>
<td colspan="2" style="text-align: right; color: #4ade80; font-weight: bold;">{resultado_dca['plusvalia']:,.0f} {divisa}</td>
</tr>
{filas}
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
<td style="padding: 8px 0;">Impuestos activo</td>
<td colspan="2" style="text-align: right; color: #ef4444;">{resultado_dca['impuestos_activo']:,.2f} {divisa}</td>
</tr>
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
<td style="padding: 8px 0;">Intereses monetario</td>
<td colspan="2" style="text-align: right; color: #4ade80;">+{resultado_dca['intereses_monetario']:,.2f} {divisa}</td>
</tr>
<tr>
<td style="padding: 8px 0;">Impuestos intereses</td>
<td colspan="2" style="text-align: right; color: #ef4444;">-{resultado_dca['impuestos_intereses']:,.2f} {divisa}</td>
</tr>
</table>
</div>'''
        st.markdown(html, unsafe_allow_html=True)
    
    pct = (resultado_dca['coste_total'] / resultado_dca['valor_bruto']) * 100 if resultado_dca['valor_bruto'] > 0 else 0
    html = f'''<div class="metric-card-highlight">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<div class="metric-title">COSTE TOTAL DCA {meses_dca}m</div>
<div class="metric-value">{resultado_dca['coste_total']:,.0f} {divisa}</div>
</div>
<div style="text-align: right;">
<div class="metric-subtitle">{pct:.1f}% del valor bruto</div>
<div class="metric-subtitle">Transacción: {resultado_dca['costes_transaccion']:,.0f} | IRPF: {resultado_dca['impuestos']:,.0f}</div>
</div>
</div>
</div>'''
    st.markdown(html, unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# =============================================================================
# GRÁFICO COMPARATIVO
# =============================================================================

st.markdown('<div class="section-header">📊 Comparativa de costes</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    categorias = ['Comisiones', 'Slippage', 'Impuestos']
    valores_ls = [resultado_ls['comision_compra'] + resultado_ls['comision_venta'],
                  resultado_ls['slippage_compra'] + resultado_ls['slippage_venta'],
                  resultado_ls['impuestos']]
    valores_dca = [resultado_dca['comision_compra'] + resultado_dca['comision_venta'],
                   resultado_dca['slippage_compra'] + resultado_dca['slippage_venta'],
                   resultado_dca['impuestos']]
    
    fig_costes = go.Figure()
    fig_costes.add_trace(go.Bar(name='Lump Sum', x=categorias, y=valores_ls, marker_color='#818cf8',
                                 text=[f'{v:,.0f}' for v in valores_ls], textposition='auto'))
    fig_costes.add_trace(go.Bar(name=f'DCA {meses_dca}m', x=categorias, y=valores_dca, marker_color='#fb923c',
                                 text=[f'{v:,.0f}' for v in valores_dca], textposition='auto'))
    
    fig_costes.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="JetBrains Mono", color="#e2e8f0"), barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(99, 102, 241, 0.1)', title=divisa),
        margin=dict(l=60, r=20, t=60, b=40), height=350
    )
    st.plotly_chart(fig_costes, use_container_width=True)

with col2:
    labels = ['Comisiones', 'Slippage', 'Impuestos', 'Neto para ti']
    values = [resultado_ls['comision_compra'] + resultado_ls['comision_venta'],
              resultado_ls['slippage_compra'] + resultado_ls['slippage_venta'],
              resultado_ls['impuestos'],
              resultado_ls['valor_neto']]
    colors = ['#fbbf24', '#f97316', '#ef4444', '#4ade80']
    
    fig_donut = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.6, marker_colors=colors,
        textinfo='label+percent', textposition='outside',
        textfont=dict(size=11, color='#e2e8f0'),
        hovertemplate='<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>'
    ))
    
    fig_donut.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="JetBrains Mono", color="#e2e8f0"), showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20), height=350,
        annotations=[dict(text=f'<b>LS</b><br>{resultado_ls["valor_neto"]:,.0f}', x=0.5, y=0.5,
                          font_size=16, font_color='#e2e8f0', showarrow=False)]
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# =============================================================================
# RESUMEN
# =============================================================================

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header">📝 Resumen de la simulación</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
<div class="metric-card">
<p><strong>📅 Período:</strong> {precios.index[0].strftime('%Y-%m-%d')} → {precios.index[-1].strftime('%Y-%m-%d')}</p>
<p><strong>📈 Activo:</strong> {nombre_activo} ({ticker_input})</p>
<p><strong>💱 Divisa:</strong> {divisa}</p>
<p><strong>💰 Capital inicial:</strong> {capital:,.0f}</p>
<p><strong>⏱️ Horizonte:</strong> {resultado_ls['años']:.1f} años</p>
<p><strong>💸 Costes:</strong> {comision*100:.2f}% comisión + {slippage*100:.2f}% slippage</p>
</div>
""", unsafe_allow_html=True)

with col2:
    ganador_txt = 'Lump Sum' if ganador == 'LS' else f'DCA {meses_dca} meses'
    pct_ls = (resultado_ls['coste_total'] / resultado_ls['valor_bruto']) * 100 if resultado_ls['valor_bruto'] > 0 else 0
    pct_dca = (resultado_dca['coste_total'] / resultado_dca['valor_bruto']) * 100 if resultado_dca['valor_bruto'] > 0 else 0
    
    st.markdown(f"""
<div class="metric-card">
<p><strong>🏆 Ganador:</strong> {ganador_txt}</p>
<p><strong>📊 Ventaja:</strong> {abs(diferencia_pp):.1f} puntos porcentuales</p>
<p><strong>💵 Diferencia neta:</strong> {abs(diferencia_euros):,.0f} {divisa}</p>
<p><strong>📉 Coste total LS:</strong> {resultado_ls['coste_total']:,.0f} ({pct_ls:.1f}%)</p>
<p><strong>📉 Coste total DCA:</strong> {resultado_dca['coste_total']:,.0f} ({pct_dca:.1f}%)</p>
<p><strong>🏦 Intereses monetario DCA:</strong> +{resultado_dca['intereses_monetario']:,.0f} {divisa}</p>
</div>
""", unsafe_allow_html=True)

# Notas metodológicas
st.markdown(f"""
<div class="info-box">
<strong>ℹ️ Notas metodológicas:</strong><br>
• <strong>Lump Sum:</strong> Invierte todo el capital el día 1, vende todo al final.<br>
• <strong>DCA:</strong> Invierte capital/{meses_dca} cada mes durante {meses_dca} meses, vende todo al final.<br>
• <strong>Coste de oportunidad:</strong> El capital pendiente de invertir en DCA genera {tasa_monetario*100:.1f}% anual en monetario.<br>
• <strong>Impuestos:</strong> Tramos IRPF 2024 (base del ahorro). Se aplican sobre plusvalía al vender.<br>
• <strong>Divisa:</strong> Todos los cálculos están en {divisa}. Si inviertes en divisa extranjera, el tipo de cambio afectará tu resultado real en EUR.
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="text-align: center; padding: 40px 0 20px 0; color: #475569;">
<p style="font-size: 0.8rem;">Desarrollado por <strong>BQuant Finance</strong> | Los resultados pasados no garantizan rendimientos futuros</p>
<p style="font-size: 0.7rem; color: #374151;">v3.0 - Coste oportunidad + Ticker libre + IRPF 2024</p>
</div>
""", unsafe_allow_html=True)
