"""JacaStock — interfaz renovada de Jacaranda Labs.

Mantiene sin modificaciones las operaciones de src/inventario.py.
"""
import os
import sys
import html
import re
from pathlib import Path

import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "src"))
from inventario import (  # noqa: E402
    conectar, productos, alta, editar, desactivar, reactivar, movimiento,
    historial, resumen, exportar_csv,
)

ICONO = BASE / "assets" / "jacaranda_icon.png"
FAVICON = BASE / "assets" / "jacaranda.ico"
st.set_page_config(
    page_title="JacaStock | Jacaranda Labs",
    page_icon=str(FAVICON) if FAVICON.exists() else "🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
/* Identidad — contraste legible en widgets y tablas */
:root { --ink:#29233A; --muted:#756B88; --purple:#6D46AD; --line:#E8DFF4; }
.stApp, [data-testid="stAppViewContainer"] {background:#FAF8FE; color:var(--ink);}
[data-testid="stHeader"] {background:rgba(250,248,254,.94);}
[data-testid="stSidebar"] {background:#F0EAF9; border-right:1px solid #E3D6F2;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#392C52;}
.block-container {max-width:1240px; padding-top:2.1rem; padding-bottom:3rem;}
h1,h2,h3 {color:#39205F !important; letter-spacing:-.025em;}
h1 {font-weight:800 !important;} h2 {font-weight:750 !important;}
p,li,label {color:#393247;}
[data-testid="stCaptionContainer"] p {color:#756B88 !important;}
[data-testid="stMetric"] {background:#FFFFFF; border:1px solid #E8DFF4;
  border-radius:18px; padding:19px 21px; box-shadow:0 5px 18px rgba(71,36,117,.055);}
[data-testid="stMetricLabel"] p {color:#756B88 !important; font-size:.91rem;}
[data-testid="stMetricValue"] {color:#3C2066 !important; font-weight:800; font-size:clamp(1.4rem, 2.1vw, 2rem) !important; overflow-wrap:anywhere;}
[data-testid="stMetricDelta"] {color:#2D7F66;}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
 background:#6D46AD !important; color:white !important; border:1px solid #6D46AD !important;
 border-radius:11px !important; font-weight:700;}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {
 background:#51318D !important; color:white !important;}
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
 border-radius:11px; border-color:#D7C8E9; color:#543482;}
[data-testid="stExpander"] {border:1px solid #E8DFF4; background:white; border-radius:16px;}
[data-testid="stDataFrame"] {border:1px solid #E8DFF4; border-radius:14px; overflow:hidden;}
[data-testid="stAlert"] {border-radius:12px;}
[data-testid="stRadio"] label {border-radius:9px;}
/* Header ilustrado */
.jaca-hero {padding:26px 28px; background:linear-gradient(110deg,#FFFFFF 10%,#F1E9FC 100%);
  border:1px solid #E8DFF4; border-radius:23px; margin:2px 0 23px; box-shadow:0 8px 28px rgba(89,53,130,.06);}
.jaca-eyebrow {font-size:.78rem; color:#805EB4; font-weight:750; text-transform:uppercase;
 letter-spacing:.13em; margin-bottom:7px;}
.jaca-title {font-size:2.65rem; font-weight:850; line-height:1.05; letter-spacing:-.045em; color:#492776;}
.jaca-tagline {color:#6E6083; margin-top:10px; font-size:1rem;}
.jaca-pill {display:inline-block; padding:5px 11px; background:#E7DCF6; color:#583586;
 font-size:.76rem; border-radius:30px; margin-top:12px; font-weight:650;}
.jaca-subhead {font-size:.83rem; font-weight:750; letter-spacing:.12em; color:#7A5BA1;
 text-transform:uppercase; margin:11px 0 5px;}
.jaca-soft {background:#F3EDF9; padding:15px 18px; border-radius:13px;
 border:1px solid #E7DDF3; color:#4E3C65;}
.jaca-footer {margin-top:30px; padding:14px 0; border-top:1px solid #E8DFF4;
 color:#82768F; font-size:.8rem;}
@media (max-width:700px) {.jaca-title {font-size:2rem;} .jaca-hero {padding:18px;}}
/* Color de los títulos de sección, independiente del tema de Streamlit. */
.stApp h2.jaca-page-title {
  color:#39205F !important; -webkit-text-fill-color:#39205F !important;
}
/* El texto de Streamlit se renderiza dentro de p/span: el color del botón
   no se heredaba porque hay una regla general para los párrafos. */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"],
.stButton > button[kind="primary"] *,
.stFormSubmitButton > button[kind="primary"] *,
button[data-testid="stBaseButton-primary"] *,
button[data-testid="stBaseButton-primaryFormSubmit"] * {
  color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# La apariencia se controla por sesión y no altera el inventario.
if st.session_state.get("modo_oscuro", False):
    st.markdown("""
    <style>
    /* JacaStock: modo oscuro de alto contraste */
    :root {color-scheme: dark; --ink:#F7F2FF; --muted:#D0C3DF; --purple:#B992F5; --line:#635376;}
    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
      background-color:#191522 !important; color:#F7F2FF !important;
    }
    [data-testid="stHeader"] {background:rgba(25,21,34,.98) !important;}
    [data-testid="stSidebar"],section[data-testid="stSidebar"] {
      background:#282035 !important; border-right:1px solid #514062 !important;
    }
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,[data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#F0E6FF !important;}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:#CABDDA !important;}
    [data-testid="stSidebar"] [role="radiogroup"] label {color:#F0E6FF !important;}
    h1,h2,h3,h4,h5,h6, [data-testid="stHeading"] *,
    [data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {color:#F4E8FF !important;}
    .stApp p,.stApp li,.stApp label,.stApp small,
    [data-testid="stWidgetLabel"] *,[data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] strong {color:#F1EBF8 !important;}
    [data-testid="stCaptionContainer"] p {color:#C8BBD7 !important;}
    /* Respaldo para versiones de Streamlit que cambian la jerarquia del DOM */
    [data-testid="stHeading"], [data-testid="stHeading"] *,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {color:#F7F2FF !important;}
    [data-testid="stAlert"] div, [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {color:#FFF9FF !important;}
    /* Métricas y paneles */
    [data-testid="stMetric"],[data-testid="metric-container"] {
      background:#30263E !important; border:1px solid #5B4970 !important;
      box-shadow:0 5px 14px rgba(0,0,0,.18) !important;
    }
    [data-testid="stMetricLabel"] p {color:#D4C8E0 !important;}
    [data-testid="stMetricValue"] {color:#FFF9FF !important;}
    [data-testid="stExpander"],[data-testid="stForm"],
    [data-testid="stDataFrame"],[data-testid="stTable"] {
      background:#282035 !important; border-color:#605073 !important;
    }
    /* Campos y listas: fondo y letras deben tener contraste juntos */
    [data-baseweb="input"],[data-baseweb="select"],
    [data-baseweb="textarea"],[data-baseweb="base-input"],
    [data-baseweb="popover"],[data-baseweb="menu"],[data-baseweb="list"],
    [data-testid="stNumberInput"] [data-baseweb="input"] {
      background:#382D48 !important; color:#FFFFFF !important;
      border-color:#79668F !important;
    }
    [data-baseweb="input"] input,[data-baseweb="textarea"] textarea,
    [data-baseweb="base-input"] input,[data-baseweb="select"] input,
    [data-baseweb="select"] [role="combobox"],
    [data-baseweb="select"] [data-testid="stMarkdownContainer"],
    [data-baseweb="select"] span,[data-baseweb="select"] div,
    [data-baseweb="input"] div,[data-baseweb="input"] span {
      color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
    }
    [data-baseweb="input"] input::placeholder, textarea::placeholder {
      color:#CBB9DD !important; -webkit-text-fill-color:#CBB9DD !important;
    }
    [data-testid="stNumberInput"] button {
      background:#49385D !important; color:#FFFFFF !important; border-color:#79668F !important;
    }
    [data-testid="stNumberInput"] button svg,
    [data-baseweb="select"] svg {fill:#F5EBFF !important; color:#F5EBFF !important;}
    [role="option"],[role="listbox"] {background:#382D48 !important; color:#FFFFFF !important;}
    [role="option"]:hover {background:#56406E !important;}
    /* Avisos: no reutilizar el texto blanco sobre fondos pálidos */
    [data-testid="stAlert"], [data-testid="stNotification"] {
      background:#30293C !important; border:1px solid #73618A !important;
    }
    [data-testid="stAlert"] *, [data-testid="stNotification"] * {
      color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
    }
    [data-testid="stAlert"] svg {color:#CEAFE8 !important;}
    /* Tablas: respeta el tema oscuro de la grilla */
    [data-testid="stDataFrame"] {color-scheme:dark;}
    [data-testid="stDataFrame"] [role="grid"] {background:#282035 !important; color:#F6EFFD !important;}
    /* Botones */
    .stButton > button,.stDownloadButton > button,.stFormSubmitButton > button {
      background:#3B2F4B !important; color:#FFFFFF !important;
      border:1px solid #79668F !important;
    }
    .stButton > button[kind="primary"],.stFormSubmitButton > button[kind="primary"] {
      background:#8255BE !important; color:#FFFFFF !important;
      border-color:#A781DD !important;
    }
    .stButton > button:hover,.stDownloadButton > button:hover,.stFormSubmitButton > button:hover {
      background:#62477C !important; color:#FFFFFF !important;
      border-color:#C4A0F3 !important;
    }
    hr {border-color:#514062 !important;}
    .jaca-hero {background:linear-gradient(110deg,#2D233B,#3A294D) !important; border-color:#5D4C70 !important;}
    .jaca-eyebrow,.jaca-subhead {color:#D7B9FF !important;}
    .jaca-title {color:#F6EBFF !important;}
    .jaca-tagline {color:#E1D3F0 !important;}
    .jaca-pill {background:#60467C !important; color:#FFF8FF !important;}
    .jaca-soft {background:#382B49 !important; border-color:#625071 !important;
      color:#F5EDFF !important;}
    .jaca-soft strong {color:#FFFFFF !important;}
    .jaca-footer {border-color:#514062 !important;color:#D1C4E0 !important;}
    .stApp h2.jaca-page-title {
      color:#F7F2FF !important; -webkit-text-fill-color:#F7F2FF !important;
    }
    </style>
    """, unsafe_allow_html=True)


def dinero(centavos):
    return f"${centavos / 100:,.2f}"


def elegir_producto(items, key):
    opciones = {f"{p['nombre']} · ID {p['id']}": p["id"] for p in items}
    if not opciones:
        st.info("Primero registra un producto en Inventario.")
        return None
    elegido = st.selectbox("Producto", list(opciones), key=key)
    return opciones[elegido]


def titulo_pagina(titulo, descripcion):
    # Color explicito: los estilos globales de Streamlit pueden cambiar con la version.
    texto_titulo = "#F7F2FF" if st.session_state.get("modo_oscuro", False) else "#39205F"
    st.markdown(
        f'<h2 class="jaca-page-title" style="color:{texto_titulo} !important; font-size:2.05rem; '
        f'font-weight:800; margin:0 0 0.3rem;">{html.escape(titulo)}</h2>',
        unsafe_allow_html=True,
    )
    st.caption(descripcion)
    st.write("")


def subtitulo(texto):
    color = "#F7F2FF" if st.session_state.get("modo_oscuro", False) else "#39205F"
    st.markdown(
        f'<h3 style="color:{color} !important; font-size:1.52rem; '
        f'font-weight:750; margin:0.5rem 0 0.8rem;">{html.escape(texto)}</h3>',
        unsafe_allow_html=True,
    )


def aviso(tipo, mensaje, icon=None):
    """Avisos legibles en modo oscuro sin depender del CSS interno de st.info."""
    oscuro = st.session_state.get("modo_oscuro", False)
    if not oscuro:
        funciones = {"info": st.info, "exito": st.success,
                     "error": st.error, "advertencia": st.warning}
        if icon is None:
            funciones[tipo](mensaje)
        else:
            funciones[tipo](mensaje, icon=icon)
        return

    colores = {
        "info": ("#252F46", "#A8C6FF", "ℹ️"),
        "exito": ("#1D3B33", "#95E1BE", "✅"),
        "error": ("#452633", "#FFB3C6", "⛔"),
        "advertencia": ("#443725", "#FFD598", "⚠️"),
    }
    fondo, borde, emoji = colores[tipo]
    contenido = html.escape(str(mensaje))
    contenido = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", contenido)
    st.markdown(
        '<div style="background:' + fondo + ';color:#FFF9FF !important;'
        'border:1px solid ' + borde + ';border-left:5px solid ' + borde + ';'
        'border-radius:12px;padding:16px 18px;margin:0.65rem 0 1rem;'
        'line-height:1.55;font-size:0.96rem;">'
        '<span style="margin-right:10px">' + (html.escape(icon) if icon else emoji) + '</span>'
        '<span style="color:#FFF9FF !important">' + contenido + '</span></div>',
        unsafe_allow_html=True,
    )


def aviso_info(mensaje, icon=None):
    aviso("info", mensaje, icon)


def aviso_exito(mensaje, icon=None):
    aviso("exito", mensaje, icon)


def aviso_error(mensaje, icon=None):
    aviso("error", mensaje, icon)


def aviso_advertencia(mensaje, icon=None):
    aviso("advertencia", mensaje, icon)


PAGINAS = ["Inicio", "Inventario", "Movimientos", "Historial y reportes", "Acerca de"]
with st.sidebar:
    if ICONO.exists():
        st.image(str(ICONO), width=74)
    st.markdown("### JacaStock")
    st.caption("JACARANDA LABS")
    st.divider()
    pagina = st.radio("Navegación", PAGINAS, label_visibility="collapsed")
    st.divider()
    st.caption("PROTITIPO ACADÉMICO")
    st.markdown("Control sencillo para tiendas de abarrotes.")
    st.divider()
    st.toggle("🌙 Modo oscuro", key="modo_oscuro", help="Cambiar entre apariencia clara y oscura")

hero_img, hero_text = st.columns([1, 7], gap="medium")
with hero_img:
    if ICONO.exists():
        st.image(str(ICONO), use_container_width=True)
with hero_text:
    st.markdown("""
    <div class="jaca-hero">
      <div class="jaca-eyebrow">Jacaranda Labs · Inventario inteligente y accesible</div>
      <div class="jaca-title">JacaStock</div>
      <div class="jaca-tagline">Organiza tu inventario, mejora tu negocio.</div>
      <span class="jaca-pill">Prototipo académico</span>
    </div>
    """, unsafe_allow_html=True)

# Guardamos la confirmación antes de recargar la interfaz.
# aviso_exito() inmediatamente seguido de st.rerun() desaparecía demasiado rápido.
def confirmar_cambio(mensaje):
    st.session_state["jacastock_confirmacion"] = mensaje
    st.rerun()

mensaje_confirmacion = st.session_state.pop("jacastock_confirmacion", None)
if mensaje_confirmacion:
    aviso_exito(mensaje_confirmacion, icon="✅")
    st.toast(mensaje_confirmacion, icon="✅")

ruta_db = os.getenv("ABARRO_DB", str(BASE / "datos" / "inventario.db"))
conexion = conectar(ruta_db)
try:
    actuales = productos(conexion)

    if pagina == "Inicio":
        titulo_pagina("Resumen de tu tienda", "Una vista rápida de lo que tienes y lo que necesitas reponer.")
        r = resumen(conexion)
        a, b, c, d = st.columns(4)
        a.metric("Productos registrados", r["productos"])
        b.metric("Unidades en existencia", r["unidades"])
        c.metric("Productos por reponer", r["bajos"])
        d.metric("Valor del inventario", dinero(r["valor_costo_centavos"]))

        st.write("")
        izq, der = st.columns([1.65, 1], gap="large")
        with izq:
            subtitulo("Atención al inventario")
            bajos = [p for p in actuales if p["existencias"] <= p["minimo"]]
            if bajos:
                tabla = pd.DataFrame([
                    {"Producto": p["nombre"], "Existencias": p["existencias"],
                     "Mínimo": p["minimo"], "Estado": "Agotado" if p["existencias"] == 0 else "Reponer"}
                    for p in bajos
                ])
                st.dataframe(tabla, hide_index=True, use_container_width=True)
            else:
                aviso_exito("¡Todo en orden! No hay productos en su nivel mínimo.")
        with der:
            subtitulo("¿Cómo empezar?")
            st.markdown("""
            <div class="jaca-soft">
            <strong>01</strong> · Registra productos en <strong>Inventario</strong>.<br><br>
            <strong>02</strong> · Anota compras y ventas en <strong>Movimientos</strong>.<br><br>
            <strong>03</strong> · Descarga tus reportes cuando los necesites.
            </div>
            """, unsafe_allow_html=True)
        st.write("")
        aviso_info("Los montos de la demostración son ilustrativos. El sistema no emite facturas.")

    elif pagina == "Inventario":
        titulo_pagina("Mi inventario", "Consulta tus productos, agrega nuevos, edita y recupera productos archivados.")
        archivados = [p for p in productos(conexion, incluir_inactivos=True) if not p["activo"]]
        if actuales:
            tabla = [{
                "ID": p["id"], "Producto": p["nombre"], "Categoría": p["categoria"],
                "Costo": dinero(p["costo_centavos"]), "Precio": dinero(p["precio_centavos"]),
                "Existencias": p["existencias"], "Mínimo": p["minimo"],
                "Estado": "Reponer" if p["existencias"] <= p["minimo"] else "Disponible",
            } for p in actuales]
            st.dataframe(pd.DataFrame(tabla), hide_index=True, use_container_width=True)
        else:
            aviso_info("Tu inventario aún está vacío. Puedes agregar tu primer producto abajo.")

        st.write("")
        with st.expander("＋ Agregar un producto", expanded=not bool(actuales)):
            with st.form("alta", clear_on_submit=False):
                nombre = st.text_input("Nombre del producto", placeholder="Ej. Leche entera 1 L")
                categoria = st.selectbox("Categoría", ["Abarrotes", "Bebidas", "Lácteos", "Limpieza", "Higiene", "Otros"])
                c1, c2 = st.columns(2)
                costo = c1.number_input("Costo de compra (MXN)", min_value=0.0, step=0.5)
                precio = c2.number_input("Precio de venta (MXN)", min_value=0.0, step=0.5)
                c3, c4 = st.columns(2)
                cantidad = c3.number_input("Existencias iniciales", min_value=0, step=1)
                minimo = c4.number_input("Avisar cuando queden", min_value=0, value=5, step=1)
                if st.form_submit_button("Guardar producto", type="primary"):
                    try:
                        alta(conexion, nombre, categoria, costo, precio, int(cantidad), int(minimo))
                        confirmar_cambio(f"Producto «{nombre.strip()}» agregado correctamente al inventario.")
                    except ValueError as e:
                        aviso_error(str(e))

        if actuales:
            with st.expander("✎ Editar o desactivar un producto"):
                ident = elegir_producto(actuales, "producto_edicion")
                if ident is not None:
                    p = next(x for x in actuales if x["id"] == ident)
                    # Edición y archivo comparten un formulario: marcar la
                    # confirmación no provoca una recarga ni cierra el panel.
                    with st.form(f"editar_{ident}"):
                        nombre = st.text_input("Nombre", value=p["nombre"])
                        categoria = st.text_input("Categoría", value=p["categoria"])
                        c1, c2, c3 = st.columns(3)
                        costo = c1.number_input("Costo (MXN)", min_value=0.0, value=p["costo_centavos"] / 100)
                        precio = c2.number_input("Precio (MXN)", min_value=0.0, value=p["precio_centavos"] / 100)
                        minimo = c3.number_input("Mínimo", min_value=0, value=p["minimo"], step=1)
                        guardar = st.form_submit_button("Guardar cambios", type="primary")
                        st.divider()
                        st.caption("Archivar lo oculta del inventario, pero conserva sus existencias y su historial. Podrás reactivarlo después.")
                        confirmar = st.checkbox("Confirmo que quiero archivar este producto")
                        archivar = st.form_submit_button("Archivar producto", type="secondary")

                        if guardar:
                            try:
                                editar(conexion, ident, nombre, categoria, costo, precio, int(minimo))
                                confirmar_cambio(f"Cambios guardados correctamente en «{nombre.strip()}».")
                            except ValueError as e:
                                aviso_error(str(e))
                        elif archivar:
                            if not confirmar:
                                aviso_advertencia("Marca la casilla de confirmación para archivar el producto.")
                            else:
                                try:
                                    desactivar(conexion, ident)
                                    confirmar_cambio(f"«{p['nombre']}» se archivó correctamente. Puedes reactivarlo cuando quieras.")
                                except ValueError as e:
                                    aviso_error(str(e))

        with st.expander(f"↺ Productos archivados · {len(archivados)}", expanded=False):
            st.caption("Si desactivaste unas galletas u otro producto, recupéralo aquí en vez de crear uno duplicado.")
            if archivados:
                tabla_archivados = pd.DataFrame([{
                    "ID": p["id"], "Producto": p["nombre"], "Categoría": p["categoria"],
                    "Existencias conservadas": p["existencias"], "Precio": dinero(p["precio_centavos"])
                } for p in archivados])
                st.dataframe(tabla_archivados, hide_index=True, use_container_width=True)
                opciones_archivados = {f"{p['nombre']} · ID {p['id']}": p["id"] for p in archivados}
                etiqueta_archivada = st.selectbox("¿Qué producto quieres recuperar?", list(opciones_archivados), key="seleccion_archivado")
                if st.button("↺ Reactivar producto", type="primary", key="reactivar_producto"):
                    try:
                        reactivar(conexion, opciones_archivados[etiqueta_archivada])
                        confirmar_cambio(f"Producto «{etiqueta_archivada.split(' · ID ')[0]}» reactivado correctamente.")
                    except ValueError as e:
                        aviso_error(str(e))
            else:
                aviso_info("No hay productos archivados.")

    elif pagina == "Movimientos":
        titulo_pagina("Entradas y salidas", "Consulta las existencias antes de registrar compras o ventas.")
        left, right = st.columns([1.3, 1], gap="large")
        with left:
            # Controles fuera del formulario para actualizar la vista previa de
            # existencias en cuanto cambia el producto, tipo o cantidad.
            ident = elegir_producto(actuales, "producto_movimiento")
            tipo_visible = st.radio("¿Qué quieres registrar?", ["Entrada · compra", "Salida · venta"], horizontal=True)
            tipo = "entrada" if tipo_visible.startswith("Entrada") else "salida"
            cantidad = st.number_input("Cantidad de unidades", min_value=1, step=1, key="cantidad_movimiento")
            nota = st.text_input("Nota (opcional)", placeholder="Ej. Compra al proveedor / venta")

            elegido = next((p for p in actuales if p["id"] == ident), None)
            stock = elegido["existencias"] if elegido else 0
            excede = bool(elegido and tipo == "salida" and cantidad > stock)
            if elegido:
                st.markdown(f"**Existencias actuales:** {stock} unidad(es)")
                if excede:
                    aviso_error(f"No puedes vender {int(cantidad)} unidad(es) de «{elegido['nombre']}»: solo hay {stock} disponibles. No se registrará la salida.", icon="🚫")
                else:
                    quedarian = stock + int(cantidad) if tipo == "entrada" else stock - int(cantidad)
                    aviso_exito(f"Después del movimiento quedarían **{quedarian} unidades** de «{elegido['nombre']}».", icon="✅")
                    if tipo == "salida":
                        st.caption(f"Total estimado de venta: {dinero(elegido['precio_centavos'] * int(cantidad))}")
            else:
                aviso_info("Primero agrega un producto en Inventario.")
            if st.button("Registrar movimiento", type="primary", disabled=ident is None or excede,
                         key="registrar_movimiento_boton", use_container_width=True):
                # Reconsultar existencias al confirmar, por seguridad.
                try:
                    movimiento(conexion, ident, tipo, int(cantidad), nota)
                    operacion = "Entrada" if tipo == "entrada" else "Salida"
                    confirmar_cambio(f"{operacion} registrada: {int(cantidad)} unidad(es) de «{elegido['nombre']}». Inventario actualizado.")
                except ValueError as e:
                    aviso_error(str(e))
        with right:
            st.markdown("""
            <div class="jaca-soft">
            <strong>Entrada</strong>: mercancía nueva que llega a la tienda.<br><br>
            <strong>Salida</strong>: mercancía que se vende.<br><br>
            <strong>Control de existencias</strong>: puedes revisar el saldo antes de guardar;
            el sistema bloquea ventas superiores al inventario disponible.
            </div>
            """, unsafe_allow_html=True)

    elif pagina == "Historial y reportes":
        titulo_pagina("Historial y reportes", "Revisa los movimientos y descarga la información de tu tienda.")
        r = resumen(conexion)
        c1, c2 = st.columns(2)
        c1.metric("Ventas registradas (acumuladas)", dinero(r["ventas_centavos"]))
        c2.metric("Margen bruto estimado", dinero(r["margen_bruto_centavos"]))
        st.write("")
        movimientos = historial(conexion)
        if movimientos:
            df = pd.DataFrame(movimientos)
            df = df.rename(columns={
                "fecha": "Fecha", "nombre": "Producto", "tipo": "Tipo",
                "cantidad": "Cantidad", "nota": "Nota",
                "precio_venta_centavos": "Precio unitario",
                "costo_unitario_centavos": "Costo unitario",
                "existencias_despues": "Existencias después",
            })
            if "Precio unitario" in df.columns:
                # Solo las salidas de venta generan ingreso en el prototipo actual.
                # No se altera la base de datos ni el CSV de exportación.
                df["Total de venta"] = df.apply(
                    lambda fila: fila["Precio unitario"] * fila["Cantidad"]
                    if fila["Tipo"] == "salida" and pd.notna(fila["Precio unitario"])
                    else None, axis=1,
                )
            for campo in ["Precio unitario", "Total de venta", "Costo unitario"]:
                if campo in df.columns:
                    df[campo] = df[campo].apply(
                        lambda cent: dinero(cent) if pd.notna(cent) else "—"
                    )
            if "Fecha" in df.columns:
                df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.strftime("%d/%m/%Y %H:%M")
            if "Nota" in df.columns:
                df["Nota"] = df.apply(
                    lambda fila: fila["Nota"]
                    if pd.notna(fila["Nota"]) and str(fila["Nota"]).strip()
                    else ("Venta registrada" if fila["Tipo"] == "salida" else "Entrada de mercancía"),
                    axis=1,
                )
            columnas = ["Fecha", "Producto", "Tipo", "Cantidad", "Precio unitario",
                        "Total de venta", "Costo unitario", "Existencias después", "Nota"]
            st.dataframe(df[[c for c in columnas if c in df.columns]],
                         hide_index=True, use_container_width=True)
        else:
            aviso_info("Todavía no se registran movimientos.")
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("↓ Descargar movimientos CSV", exportar_csv(movimientos).encode("utf-8"),
                               file_name="jacastock_movimientos.csv", mime="text/csv", disabled=not bool(movimientos), use_container_width=True)
        with c2:
            st.download_button("↓ Descargar inventario CSV", exportar_csv(actuales).encode("utf-8"),
                               file_name="jacastock_inventario.csv", mime="text/csv", disabled=not bool(actuales), use_container_width=True)
        st.caption("El margen bruto no incluye gastos como renta, salarios, servicios e impuestos.")

    else:
        titulo_pagina("Sobre JacaStock", "Tecnología práctica para negocios.")
        st.markdown("""
        **JacaStock** es un prototipo de Jacaranda Labs para la materia de Introducción a la Economía.
        Este permite registrar productos, actualizar existencias y consultar reportes en una sola interfaz.

        **Lo que incluye:** inventario, entradas, salidas, alertas de stock y exportación de datos.
        """)
        aviso_advertencia("Este proyecto es un prototipo: no incluye usuarios, facturación, respaldos automáticos ni control de caducidades.")

    st.markdown('<div class="jaca-footer">JacaStock · Jacaranda Labs</div>', unsafe_allow_html=True)
finally:
    conexion.close()
