"""
LUMP SUM vs DCA - Interactive Backtest Dashboard v2
====================================================
App de Streamlit con estética dark mode para análisis
de estrategias de inversión.

CORRECCIONES v2:
- Tramos IRPF España 2024 actualizados
- Validación dinámica del horizonte temporal
- Mejor manejo de DCA con datos insuficientes
- Cálculo correcto de plusvalía en DCA
- Métricas adicionales (CAGR, Max Drawdown)

Requisitos: pip install streamlit yfinance pandas numpy plotly

Ejecutar: streamlit run app_lumpsum_dca_v2.py

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
    
    /* Hide Streamlit branding but keep sidebar functional */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Keep header visible for sidebar toggle, just hide the decoration */
    header[data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: none !important;
    }
    
    /* Ensure sidebar is always visible and styled */
    section[data-testid="stSidebar"] {
        display: block !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #0f0f18 0%, #151520 100%);
    }
    
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
        color: #e2e8f0 !important;
    }
    
    .streamlit-expanderHeader p {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .streamlit-expanderContent {
        background-color: #12121a !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
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
    
    /* Info box */
    .info-box {
        background: linear-gradient(145deg, #1e3a5f 0%, #1e3a8a 100%);
        border: 1px solid rgba(59, 130, 246, 0.4);
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        font-size: 0.85rem;
    }
    
    .warning-box {
        background: linear-gradient(145deg, #78350f 0%, #92400e 100%);
        border: 1px solid rgba(251, 191, 36, 0.4);
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# FUNCIONES DE CÁLCULO
# =============================================================================

# Tramos IRPF España 2024 - Base del Ahorro (plusvalías)
# Fuente: Agencia Tributaria
TRAMOS_IRPF_2024 = [
    (6_000, 0.19),       # Hasta 6.000€: 19%
    (50_000, 0.21),      # De 6.000€ a 50.000€: 21%
    (200_000, 0.23),     # De 50.000€ a 200.000€: 23%
    (300_000, 0.27),     # De 200.000€ a 300.000€: 27%
    (float('inf'), 0.28) # Más de 300.000€: 28%
]


def calcular_impuestos_españa(plusvalia: float) -> tuple[float, dict]:
    """
    Calcula impuestos sobre plusvalías según tramos IRPF España 2024.
    
    La base del ahorro tributa de forma progresiva por tramos.
    Solo se pagan impuestos si hay plusvalía positiva.
    
    Args:
        plusvalia: Ganancia patrimonial (puede ser negativa)
    
    Returns:
        tuple: (impuesto_total, desglose_por_tramo)
    """
    if plusvalia <= 0:
        return 0.0, {}
    
    impuesto_total = 0.0
    restante = plusvalia
    limite_anterior = 0.0
    desglose = {}
    
    for limite_superior, tipo_marginal in TRAMOS_IRPF_2024:
        # Calcular el ancho del tramo actual
        ancho_tramo = limite_superior - limite_anterior
        
        # Cuánto de la plusvalía cae en este tramo
        base_en_tramo = min(restante, ancho_tramo)
        
        if base_en_tramo > 0:
            impuesto_tramo = base_en_tramo * tipo_marginal
            impuesto_total += impuesto_tramo
            
            # Guardar desglose
            pct_str = f"{int(tipo_marginal * 100)}%"
            desglose[pct_str] = {
                'base': base_en_tramo,
                'impuesto': impuesto_tramo
            }
            
            restante -= base_en_tramo
            limite_anterior = limite_superior
        
        if restante <= 0:
            break
    
    return impuesto_total, desglose


def calcular_max_drawdown(serie_valores: pd.Series) -> tuple[float, datetime, datetime]:
    """
    Calcula el Maximum Drawdown de una serie de valores.
    
    Args:
        serie_valores: Serie temporal de valores del portfolio
    
    Returns:
        tuple: (max_drawdown_pct, fecha_pico, fecha_valle)
    """
    # Calcular máximo acumulado (high water mark)
    rolling_max = serie_valores.expanding().max()
    
    # Drawdown en cada punto
    drawdowns = (serie_valores - rolling_max) / rolling_max
    
    # Máximo drawdown
    max_dd = drawdowns.min()
    
    # Encontrar fechas
    idx_valle = drawdowns.idxmin()
    # El pico es el máximo antes del valle
    serie_hasta_valle = serie_valores.loc[:idx_valle]
    idx_pico = serie_hasta_valle.idxmax()
    
    return max_dd * 100, idx_pico, idx_valle


def calcular_cagr(valor_inicial: float, valor_final: float, años: float) -> float:
    """
    Calcula la Tasa de Crecimiento Anual Compuesta (CAGR).
    
    Args:
        valor_inicial: Valor al inicio
        valor_final: Valor al final
        años: Número de años
    
    Returns:
        CAGR en porcentaje
    """
    if valor_inicial <= 0 or años <= 0:
        return 0.0
    
    cagr = (valor_final / valor_inicial) ** (1 / años) - 1
    return cagr * 100


def simular_estrategia(
    precios: pd.Series,
    capital: float,
    comision: float,
    slippage: float,
    meses_dca: int = None
) -> dict:
    """
    Simula estrategia Lump Sum (meses_dca=None) o DCA.
    
    LÓGICA DE COSTES:
    - Comisión: Se aplica sobre el importe de cada operación (compra y venta)
    - Slippage: Se aplica sobre el importe de cada operación (compra y venta)
    - Los costes reducen el capital efectivo invertido
    
    LÓGICA DE IMPUESTOS:
    - Plusvalía = Valor neto tras venta - Capital invertido (base de coste)
    - En LS: Base de coste = Capital inicial
    - En DCA: Base de coste = Suma de aportaciones efectivamente realizadas
    
    Args:
        precios: Serie de precios del activo
        capital: Capital inicial total
        comision: Comisión por operación (0.001 = 0.1%)
        slippage: Slippage por operación (0.0005 = 0.05%)
        meses_dca: Meses para distribuir DCA (None = Lump Sum)
    
    Returns:
        dict con resultados detallados
    """
    coste_operacion = comision + slippage
    
    if meses_dca is None or meses_dca == 0:
        # =====================================================================
        # LUMP SUM: Invertir todo el capital de golpe al inicio
        # =====================================================================
        
        # Costes de compra
        comision_compra = capital * comision
        slippage_compra = capital * slippage
        capital_efectivo = capital - comision_compra - slippage_compra
        
        # Comprar participaciones
        precio_compra = precios.iloc[0]
        participaciones = capital_efectivo / precio_compra
        
        # Evolución del valor (antes de vender)
        valores_brutos = participaciones * precios
        
        # Base de coste para impuestos = capital inicial invertido
        base_coste = capital
        
        # Registro de operaciones
        num_operaciones = 1  # Solo la compra por ahora
        capital_total_invertido = capital
        
        # Precio medio de compra
        precio_medio_compra = precio_compra
        
    else:
        # =====================================================================
        # DCA: Distribuir el capital en aportaciones periódicas
        # =====================================================================
        
        aportacion_mensual = capital / meses_dca
        dias_entre_aportaciones = 21  # ~1 mes en días de trading
        
        participaciones = 0.0
        capital_total_invertido = 0.0  # Lo que realmente se ha invertido
        comision_compra = 0.0
        slippage_compra = 0.0
        num_operaciones = 0
        precios_compra = []
        cantidades_compra = []
        
        # Serie para tracking del valor en cada momento
        valores_brutos = pd.Series(index=precios.index, dtype=float)
        
        for mes in range(meses_dca):
            idx_dia = mes * dias_entre_aportaciones
            
            # Verificar que hay datos suficientes
            if idx_dia >= len(precios):
                # No hay más datos, el DCA se corta aquí
                break
            
            # Costes de esta aportación
            comision_op = aportacion_mensual * comision
            slippage_op = aportacion_mensual * slippage
            capital_efectivo_op = aportacion_mensual - comision_op - slippage_op
            
            # Comprar participaciones
            precio_actual = precios.iloc[idx_dia]
            participaciones_nuevas = capital_efectivo_op / precio_actual
            
            participaciones += participaciones_nuevas
            capital_total_invertido += aportacion_mensual
            comision_compra += comision_op
            slippage_compra += slippage_op
            num_operaciones += 1
            
            # Guardar para cálculo de precio medio
            precios_compra.append(precio_actual)
            cantidades_compra.append(participaciones_nuevas)
        
        # Calcular valor en cada punto temporal
        valores_brutos = participaciones * precios
        
        # Para los días antes de la primera compra, el valor es 0
        # (o podríamos mostrar el capital en efectivo, pero es más limpio así)
        
        # Base de coste = capital efectivamente invertido
        base_coste = capital_total_invertido
        
        # Precio medio ponderado de compra
        if sum(cantidades_compra) > 0:
            precio_medio_compra = sum(p * c for p, c in zip(precios_compra, cantidades_compra)) / sum(cantidades_compra)
        else:
            precio_medio_compra = 0
    
    # =========================================================================
    # VENTA: Aplicar costes de venta
    # =========================================================================
    
    valor_bruto_final = valores_brutos.iloc[-1]
    
    comision_venta = valor_bruto_final * comision
    slippage_venta = valor_bruto_final * slippage
    valor_tras_venta = valor_bruto_final - comision_venta - slippage_venta
    
    num_operaciones += 1  # La venta
    
    # Totales de costes de transacción
    comisiones_totales = comision_compra + comision_venta
    slippage_total = slippage_compra + slippage_venta
    costes_transaccion = comisiones_totales + slippage_total
    
    # =========================================================================
    # IMPUESTOS
    # =========================================================================
    
    # Plusvalía = Valor obtenido - Base de coste
    plusvalia = valor_tras_venta - base_coste
    
    impuestos, desglose_impuestos = calcular_impuestos_españa(plusvalia)
    
    # =========================================================================
    # RESULTADO FINAL
    # =========================================================================
    
    valor_neto_final = valor_tras_venta - impuestos
    
    # Rentabilidad sobre capital inicial (no sobre base de coste)
    # Esto permite comparar LS vs DCA de forma justa
    rentabilidad_total = (valor_neto_final / capital - 1) * 100
    
    # Años de inversión
    dias_inversion = (precios.index[-1] - precios.index[0]).days
    años_inversion = dias_inversion / 365.25
    
    # CAGR neto
    cagr = calcular_cagr(capital, valor_neto_final, años_inversion)
    
    # Max Drawdown (sobre valores brutos, antes de impuestos)
    max_dd, fecha_pico, fecha_valle = calcular_max_drawdown(valores_brutos)
    
    # Tipo efectivo de impuestos
    tipo_efectivo = (impuestos / plusvalia * 100) if plusvalia > 0 else 0
    
    return {
        # Serie temporal
        'valores': valores_brutos,
        
        # Valores finales
        'valor_bruto': valor_bruto_final,
        'valor_tras_venta': valor_tras_venta,
        'valor_neto': valor_neto_final,
        
        # Rentabilidades
        'rentabilidad': rentabilidad_total,
        'cagr': cagr,
        
        # Riesgo
        'max_drawdown': max_dd,
        'fecha_pico_dd': fecha_pico,
        'fecha_valle_dd': fecha_valle,
        
        # Costes de compra
        'comision_compra': comision_compra,
        'slippage_compra': slippage_compra,
        
        # Costes de venta
        'comision_venta': comision_venta,
        'slippage_venta': slippage_venta,
        
        # Totales transacción
        'comisiones': comisiones_totales,
        'slippage': slippage_total,
        'costes_transaccion': costes_transaccion,
        
        # Impuestos
        'base_coste': base_coste,
        'plusvalia': plusvalia,
        'impuestos': impuestos,
        'tipo_efectivo_irpf': tipo_efectivo,
        'desglose_impuestos': desglose_impuestos,
        
        # Coste total
        'coste_total': costes_transaccion + impuestos,
        
        # Operaciones
        'num_operaciones': num_operaciones,
        'capital_invertido': capital_total_invertido if meses_dca else capital,
        'precio_medio_compra': precio_medio_compra,
        
        # Metadata
        'años': años_inversion
    }


@st.cache_data(ttl=3600)
def descargar_datos(ticker: str, fecha_inicio: str) -> pd.Series:
    """Descarga datos con caché de 1 hora."""
    data = yf.download(ticker, start=fecha_inicio, progress=False, multi_level_index=False)
    if data.empty:
        raise ValueError(f"No se encontraron datos para {ticker}")
    return data['Close'].dropna()


def calcular_años_disponibles(fecha_inicio: datetime) -> int:
    """Calcula cuántos años de datos hay disponibles desde la fecha de inicio."""
    hoy = datetime.now()
    diferencia = hoy - datetime.combine(fecha_inicio, datetime.min.time())
    return max(1, diferencia.days // 365)


# =============================================================================
# SIDEBAR - PARÁMETROS
# =============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="margin: 0; font-size: 1.5rem;">📊 BQuant Finance</h2>
        <p style="color: #64748b; font-size: 0.8rem; margin-top: 8px;">Lump Sum vs DCA Backtest v2</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Activo (movido arriba para calcular datos disponibles)
    st.markdown("##### 📈 Activo")
    ticker_options = {
        "S&P 500 (SPY)": "SPY",
        "NASDAQ 100 (QQQ)": "QQQ",
        "MSCI World (VT)": "VT",
        "Euro Stoxx 50": "^STOXX50E",
        "IBEX 35": "^IBEX",
        "S&P 500 Index": "^GSPC",
        "NASDAQ Index": "^NDX"
    }
    ticker_name = st.selectbox(
        "Índice",
        options=list(ticker_options.keys()),
        index=0,
        label_visibility="collapsed"
    )
    ticker = ticker_options[ticker_name]
    
    # Fecha inicio
    fecha_inicio = st.date_input(
        "Fecha inicio simulación",
        value=datetime(2010, 1, 1),
        min_value=datetime(1990, 1, 1),
        max_value=datetime.now() - timedelta(days=365)
    )
    
    # Calcular máximo horizonte disponible
    años_disponibles = calcular_años_disponibles(fecha_inicio)
    
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
    
    # Horizonte - AHORA CON LÍMITE DINÁMICO
    st.markdown("##### 📅 Horizonte temporal")
    
    if años_disponibles < 1:
        st.error("La fecha de inicio es muy reciente")
        st.stop()
    
    horizonte_max = min(30, años_disponibles)
    horizonte_default = min(10, horizonte_max)
    
    horizonte = st.slider(
        "Años de inversión",
        min_value=1,
        max_value=horizonte_max,
        value=horizonte_default,
        label_visibility="collapsed"
    )
    
    # Mostrar info si el horizonte está limitado
    if años_disponibles < 30:
        st.caption(f"ℹ️ Máx. {años_disponibles} años disponibles desde {fecha_inicio}")
    
    st.markdown("##### 🔄 Período DCA")
    meses_dca = st.selectbox(
        "Meses para DCA",
        options=[6, 12, 18, 24, 36, 48, 60],
        index=1,
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    st.markdown("##### 💸 Costes de transacción")
    
    comision = st.slider(
        "Comisión por operación (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.10,
        step=0.01,
        format="%.2f%%",
        help="Comisión del broker por cada compra/venta"
    ) / 100
    
    slippage = st.slider(
        "Slippage (%)",
        min_value=0.0,
        max_value=0.50,
        value=0.05,
        step=0.01,
        format="%.2f%%",
        help="Diferencia entre precio esperado y ejecutado"
    ) / 100
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Info sobre impuestos
    with st.expander("ℹ️ Tramos IRPF 2024"):
        st.markdown("""
        **Base del Ahorro (plusvalías):**
        - Hasta 6.000€: **19%**
        - 6.000€ - 50.000€: **21%**
        - 50.000€ - 200.000€: **23%**
        - 200.000€ - 300.000€: **27%**
        - Más de 300.000€: **28%**
        """)


# =============================================================================
# MAIN CONTENT
# =============================================================================

# Header
st.markdown("""
<h1 style="font-size: 2.5rem; margin-bottom: 8px;">
    Lump Sum vs Dollar Cost Averaging
</h1>
<p style="color: #64748b; font-size: 1rem; margin-bottom: 32px;">
    Análisis con costes reales: comisiones, slippage e impuestos IRPF España 2024
</p>
""", unsafe_allow_html=True)

# Cargar datos
try:
    with st.spinner("Descargando datos de mercado..."):
        precios_full = descargar_datos(ticker, str(fecha_inicio))
    
    if precios_full.empty:
        st.error(f"No se encontraron datos para {ticker}")
        st.stop()
    
    # Calcular días necesarios
    dias_horizonte = horizonte * 252  # Días de trading
    
    # Verificar datos suficientes
    if len(precios_full) < dias_horizonte:
        dias_disponibles = len(precios_full)
        años_reales = dias_disponibles / 252
        st.warning(f"""
        ⚠️ **Datos insuficientes**: Solo hay {dias_disponibles} días de trading 
        (~{años_reales:.1f} años) desde {fecha_inicio}.
        
        Ajustando horizonte automáticamente...
        """)
        dias_horizonte = dias_disponibles - 1
        horizonte = dias_horizonte / 252
    
    # Recortar al horizonte
    precios = precios_full.iloc[:dias_horizonte + 1]
    
    # Verificar que DCA es posible con los datos
    dias_necesarios_dca = meses_dca * 21
    if dias_necesarios_dca > len(precios):
        st.warning(f"""
        ⚠️ El período DCA de {meses_dca} meses requiere ~{dias_necesarios_dca} días de trading,
        pero solo hay {len(precios)} días en el horizonte seleccionado.
        
        Algunas aportaciones DCA podrían no completarse.
        """)
    
    # Simular estrategias
    resultado_ls = simular_estrategia(precios, capital, comision, slippage, meses_dca=None)
    resultado_dca = simular_estrategia(precios, capital, comision, slippage, meses_dca=meses_dca)
    
    # Determinar ganador
    ganador = "LS" if resultado_ls['rentabilidad'] > resultado_dca['rentabilidad'] else "DCA"
    diferencia_pp = resultado_ls['rentabilidad'] - resultado_dca['rentabilidad']
    diferencia_euros = resultado_ls['valor_neto'] - resultado_dca['valor_neto']
    
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
            <div class="metric-subtitle">{resultado_ls['valor_neto']:,.0f}€ neto | CAGR: {resultado_ls['cagr']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color_dca = "metric-value-green" if resultado_dca['rentabilidad'] > 0 else "metric-value-red"
        badge_dca = '<span class="winner-badge winner-dca">GANADOR</span>' if ganador == "DCA" else ""
        st.markdown(f"""
        <div class="metric-card-highlight">
            <div class="metric-title">DCA {meses_dca} MESES {badge_dca}</div>
            <div class="metric-value {color_dca}">{resultado_dca['rentabilidad']:+.1f}%</div>
            <div class="metric-subtitle">{resultado_dca['valor_neto']:,.0f}€ neto | CAGR: {resultado_dca['cagr']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color_diff = "metric-value-blue" if diferencia_pp > 0 else "metric-value-amber"
        ventaja_texto = "LS" if diferencia_pp > 0 else "DCA"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">VENTAJA {ventaja_texto}</div>
            <div class="metric-value {color_diff}">{abs(diferencia_pp):.1f} pp</div>
            <div class="metric-subtitle">{abs(diferencia_euros):,.0f}€ de diferencia</div>
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
            <div class="metric-value metric-value-blue">{resultado_ls['precio_medio_compra']:.2f}</div>
            <div class="metric-subtitle">1 operación de compra</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">PRECIO MEDIO DCA</div>
            <div class="metric-value metric-value-amber">{resultado_dca['precio_medio_compra']:.2f}</div>
            <div class="metric-subtitle">{resultado_dca['num_operaciones']-1} compras</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # ==========================================================================
    # GRÁFICO PRINCIPAL
    # ==========================================================================
    
    st.markdown('<div class="section-header">📈 Evolución del patrimonio (antes de impuestos)</div>', unsafe_allow_html=True)
    
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
    
    st.markdown('<div class="section-header">💸 Desglose detallado de costes</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Lump Sum", "📊 DCA"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Costes de Transacción**")
            
            st.markdown(f"""
            <div class="metric-card">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                        <td style="padding: 8px 0;">Comisión compra</td>
                        <td style="text-align: right; color: #fbbf24;">{resultado_ls['comision_compra']:,.2f}€</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                        <td style="padding: 8px 0;">Slippage compra</td>
                        <td style="text-align: right; color: #fbbf24;">{resultado_ls['slippage_compra']:,.2f}€</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                        <td style="padding: 8px 0;">Comisión venta</td>
                        <td style="text-align: right; color: #fbbf24;">{resultado_ls['comision_venta']:,.2f}€</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                        <td style="padding: 8px 0;">Slippage venta</td>
                        <td style="text-align: right; color: #fbbf24;">{resultado_ls['slippage_venta']:,.2f}€</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Total transacción</td>
                        <td style="text-align: right; color: #f97316; font-weight: bold;">{resultado_ls['costes_transaccion']:,.2f}€</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Impuestos IRPF**")
            
            desglose_html = ""
            for tramo, datos in resultado_ls['desglose_impuestos'].items():
                desglose_html += f"""
                <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                    <td style="padding: 8px 0;">Tramo {tramo}</td>
                    <td style="text-align: right; color: #94a3b8;">{datos['base']:,.0f}€ × {tramo}</td>
                    <td style="text-align: right; color: #ef4444;">{datos['impuesto']:,.2f}€</td>
                </tr>
                """
            
            st.markdown(f"""
            <div class="metric-card">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
                        <td style="padding: 8px 0;">Base coste</td>
                        <td colspan="2" style="text-align: right; color: #94a3b8;">{resultado_ls['base_coste']:,.0f}€</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
                        <td style="padding: 8px 0;">Valor tras venta</td>
                        <td colspan="2" style="text-align: right; color: #94a3b8;">{resultado_ls['valor_tras_venta']:,.0f}€</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
                        <td style="padding: 8px 0; font-weight: bold;">Plusvalía</td>
                        <td colspan="2" style="text-align: right; color: #4ade80; font-weight: bold;">{resultado_ls['plusvalia']:,.0f}€</td>
                    </tr>
                    {desglose_html}
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Total impuestos</td>
                        <td style="text-align: right; color: #94a3b8;">({resultado_ls['tipo_efectivo_irpf']:.1f}% efectivo)</td>
                        <td style="text-align: right; color: #ef4444; font-weight: bold;">{resultado_ls['impuestos']:,.2f}€</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        # Resumen LS
        pct_coste_ls = (resultado_ls['coste_total'] / resultado_ls['valor_bruto']) * 100 if resultado_ls['valor_bruto'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card-highlight">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div class="metric-title">COSTE TOTAL LUMP SUM</div>
                    <div class="metric-value">{resultado_ls['coste_total']:,.0f}€</div>
                </div>
                <div style="text-align: right;">
                    <div class="metric-subtitle">{pct_coste_ls:.1f}% del valor bruto</div>
                    <div class="metric-subtitle">Transacción: {resultado_ls['costes_transaccion']:,.0f}€ | IRPF: {resultado_ls['impuestos']:,.0f}€</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Costes de Transacción**")
            
            st.markdown(f"""
            <div class="metric-card">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                        <td style="padding: 8px 0;">Comisiones compra ({resultado_dca['num_operaciones']-1} ops)</td>
                        <td style="text-align: right; color: #fbbf24;">{resultado_dca['comision_compra']:,.2f}€</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                        <td style="padding: 8px 0;">Slippage compras</td>
                        <td style="text-align: right; color: #fbbf24;">{resultado_dca['slippage_compra']:,.2f}€</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                        <td style="padding: 8px 0;">Comisión venta</td>
                        <td style="text-align: right; color: #fbbf24;">{resultado_dca['comision_venta']:,.2f}€</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                        <td style="padding: 8px 0;">Slippage venta</td>
                        <td style="text-align: right; color: #fbbf24;">{resultado_dca['slippage_venta']:,.2f}€</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Total transacción</td>
                        <td style="text-align: right; color: #f97316; font-weight: bold;">{resultado_dca['costes_transaccion']:,.2f}€</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Impuestos IRPF**")
            
            desglose_html_dca = ""
            for tramo, datos in resultado_dca['desglose_impuestos'].items():
                desglose_html_dca += f"""
                <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                    <td style="padding: 8px 0;">Tramo {tramo}</td>
                    <td style="text-align: right; color: #94a3b8;">{datos['base']:,.0f}€ × {tramo}</td>
                    <td style="text-align: right; color: #ef4444;">{datos['impuesto']:,.2f}€</td>
                </tr>
                """
            
            st.markdown(f"""
            <div class="metric-card">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
                        <td style="padding: 8px 0;">Capital invertido</td>
                        <td colspan="2" style="text-align: right; color: #94a3b8;">{resultado_dca['capital_invertido']:,.0f}€</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
                        <td style="padding: 8px 0;">Valor tras venta</td>
                        <td colspan="2" style="text-align: right; color: #94a3b8;">{resultado_dca['valor_tras_venta']:,.0f}€</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.3);">
                        <td style="padding: 8px 0; font-weight: bold;">Plusvalía</td>
                        <td colspan="2" style="text-align: right; color: #4ade80; font-weight: bold;">{resultado_dca['plusvalia']:,.0f}€</td>
                    </tr>
                    {desglose_html_dca}
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Total impuestos</td>
                        <td style="text-align: right; color: #94a3b8;">({resultado_dca['tipo_efectivo_irpf']:.1f}% efectivo)</td>
                        <td style="text-align: right; color: #ef4444; font-weight: bold;">{resultado_dca['impuestos']:,.2f}€</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        # Resumen DCA
        pct_coste_dca = (resultado_dca['coste_total'] / resultado_dca['valor_bruto']) * 100 if resultado_dca['valor_bruto'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card-highlight">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div class="metric-title">COSTE TOTAL DCA {meses_dca}m</div>
                    <div class="metric-value">{resultado_dca['coste_total']:,.0f}€</div>
                </div>
                <div style="text-align: right;">
                    <div class="metric-subtitle">{pct_coste_dca:.1f}% del valor bruto</div>
                    <div class="metric-subtitle">Transacción: {resultado_dca['costes_transaccion']:,.0f}€ | IRPF: {resultado_dca['impuestos']:,.0f}€</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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
        # Donut chart de distribución del resultado final
        fig_donut = go.Figure()
        
        labels = ['Comisiones', 'Slippage', 'Impuestos', 'Neto para ti']
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
            <p><strong>📈 Activo:</strong> {ticker_name}</p>
            <p><strong>💰 Capital inicial:</strong> {capital:,.0f}€</p>
            <p><strong>⏱️ Horizonte:</strong> {resultado_ls['años']:.1f} años</p>
            <p><strong>💸 Costes:</strong> {comision*100:.2f}% comisión + {slippage*100:.2f}% slippage</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        ganador_texto = 'Lump Sum' if ganador == 'LS' else f'DCA {meses_dca} meses'
        st.markdown(f"""
        <div class="metric-card">
            <p><strong>🏆 Ganador:</strong> {ganador_texto}</p>
            <p><strong>📊 Ventaja:</strong> {abs(diferencia_pp):.1f} puntos porcentuales</p>
            <p><strong>💵 Diferencia neta:</strong> {abs(diferencia_euros):,.0f}€</p>
            <p><strong>📉 Coste total LS:</strong> {resultado_ls['coste_total']:,.0f}€ ({pct_coste_ls:.1f}%)</p>
            <p><strong>📉 Coste total DCA:</strong> {resultado_dca['coste_total']:,.0f}€ ({pct_coste_dca:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Info box con explicación
    st.markdown(f"""
    <div class="info-box">
        <strong>ℹ️ Notas metodológicas:</strong><br>
        • Los impuestos se calculan según tramos IRPF 2024 para rentas del ahorro (plusvalías).<br>
        • La plusvalía = Valor tras costes de venta - Capital invertido (base de coste).<br>
        • En DCA, la base de coste es la suma de aportaciones realizadas ({resultado_dca['capital_invertido']:,.0f}€).<br>
        • El slippage simula el coste de ejecución real vs. precio teórico.<br>
        • Días de trading estimados: 252/año, 21/mes para aportaciones DCA.
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error al procesar datos: {str(e)}")
    st.info("Verifica que el ticker sea válido y tengas conexión a internet.")
    st.exception(e)

# Footer
st.markdown("""
<div style="text-align: center; padding: 40px 0 20px 0; color: #475569;">
    <p style="font-size: 0.8rem;">Desarrollado por <strong>BQuant Finance</strong> | Los resultados pasados no garantizan rendimientos futuros</p>
    <p style="font-size: 0.7rem; color: #374151;">v2.0 - Tramos IRPF 2024 | Cálculos revisados</p>
</div>
""", unsafe_allow_html=True)
