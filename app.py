import streamlit as st
import pandas as pd
import numpy as np
import re
import os

# Configuración de página mobile-first con identidad visual de deconfianza.uy
st.set_page_config(
    page_title="deconfianza.uy - Comercios de Confianza",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para integrar los colores del logo e íconos de redes
st.markdown("""
    <style>
        .main-title {
            color: #114294; /* Azul oscuro corporativo */
            font-family: 'Arial Black', sans-serif;
            text-align: center;
            margin-bottom: 0px;
        }
        .slogan {
            color: #555555;
            text-align: center;
            font-style: italic;
            font-size: 1.1rem;
            margin-bottom: 25px;
        }
        .stButton>button {
            background-color: #114294;
            color: white;
            border-radius: 8px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #f0ad11; /* Dorado deconfianza */
            color: #114294;
        }
    </style>
""", unsafe_allow_html=True)

# Imagen del Logo corporativo (Debe estar en tu repositorio)
LOGO_FILE = "WhatsApp Image 2026-05-24 at 23.46.20.jpeg"
if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, use_container_width=True)
else:
    st.markdown("<h1 class='main-title'>deconfianza.uy</h1>", unsafe_allow_html=True)

st.markdown("<p class='slogan'>Fácil... Rápido... Deconfianza.uy</p>", unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL AUTOMÁTICA Y AUTO-REPARABLE ---
DB_FILE = "clientes_deconfianza.csv"

def inicializar_base_datos():
    columnas_requeridas = ["Nombre", "Subdominio", "GoogleMaps", "Rubro", "Barrio/Zona", "WhatsApp", "Instagram"]
    
    if not os.path.exists(DB_FILE):
        # Crear base de datos de cero si no existe
        df_inicial = pd.DataFrame(columns=columnas_requeridas)
        df_inicial.loc[0] = ["Ejemplo Taller Mecánico", "https://taller.deconfianza.uy", "-34.9011,-56.1645", "Talleres", "Centro", "099123456", "taller.ejemplo"]
        df_inicial.loc[1] = ["Ejemplo Peluquería Pocitos", "https://pelu.deconfianza.uy", "-34.9150,-56.1500", "Estética", "Pocitos", "099654321", "pelu.ejemplo"]
        df_inicial.to_csv(DB_FILE, index=False)
    else:
        # SOLUCIÓN AL KEYERROR: Si el archivo existe pero es viejo, le inyectamos las columnas que le falten
        try:
            df_existente = pd.read_csv(DB_FILE)
            cambios = False
            for col in columnas_requeridas:
                if col not in df_existente.columns:
                    df_existente[col] = ""  # Agrega la columna vacía para que no tire KeyError
                    cambios = True
            if cambios:
                df_existente.to_csv(DB_FILE, index=False)
        except Exception:
            pass

inicializar_base_datos()

def cargar_clientes():
    return pd.read_csv(DB_FILE).fillna("")

def guardar_clientes(df):
    df.to_csv(DB_FILE, index=False)

# --- FUNCIONES DE CÁLCULO DE DISTANCIA ---
def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    return R * (2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))

def extraer_coordenadas(texto_maps):
    regex = r"(-?\\d+\\.\\d+),\\s*(-?\\d+\\.\\d+)"
    match = re.search(regex, str(texto_maps))
    if match:
        return float(match.group(1)), float(match.group(2))
    return None

# --- PANEL DE ADMINISTRACIÓN ---
st.sidebar.markdown("## 🔐 Acceso Administrador")
admin_pass = st.sidebar.text_input("Contraseña de gestión:", type="password")

df_actual = cargar_clientes()

if admin_pass == "1234":
    st.sidebar.success("🔑 Modo Editor Activado")
    st.markdown("---")
    st.markdown("### 🛠️ Panel de Gestión de Comercios")
    
    opcion = st.radio("Acción:", ["Agregar por Subdominio", "Editar / Eliminar existentes"], horizontal=True)
    
    if opcion == "Agregar por Subdominio":
        subdominio_ingresado = st.text_input("🌐 Ingresá el Subdominio del comercio:", placeholder="https://ejemplo.deconfianza.uy")
        
        with st.form("add_form", clear_on_submit=True):
            nuevo_nombre = st.text_input("Nombre comercial:")
            nuevo_rubro = st.text_input("Rubro / Categoría:")
            nuevo_barrio = st.text_input("Barrio o Zona:")
            nuevo_maps = st.text_input("Coordenadas o URL de Google Maps (Para el botón de mapa):")
            nuevo_wpp = st.text_input("Celular de WhatsApp (sin espacios, ej: 099123456):")
            nuevo_ig = st.text_input("Usuario de Instagram (sin el @, ej: comercio.uy):")
            
            enviado = st.form_submit_button("💾 Guardar en Planilla")
            if enviado:
                if nuevo_nombre and subdominio_ingresado:
                    nueva_fila = pd.DataFrame([{
                        "Nombre": nuevo_nombre, 
                        "Subdominio": subdominio_ingresado, 
                        "GoogleMaps": nuevo_maps, 
                        "Rubro": nuevo_rubro, 
                        "Barrio/Zona": nuevo_barrio,
                        "WhatsApp": nuevo_wpp,
                        "Instagram": nuevo_ig
                    }])
                    df_actual = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    guardar_clientes(df_actual)
                    st.success(f"✅ Ficha de '{nuevo_nombre}' vinculada correctamente al subdominio.")
                    st.rerun()
                else:
                    st.error("Por favor completa el Nombre y el Subdominio.")
                    
    else:
        if len(df_actual) > 0:
            comercio_sel = st.selectbox("Selecciona el comercio a modificar:", df_actual["Nombre"].tolist())
            idx_sel = df_actual[df_actual["Nombre"] == comercio_sel].index[0]
            
            with st.form("edit_form"):
                e_nombre = st.text_input("Nombre:", value=df_actual.loc[idx_sel, "Nombre"])
                e_subdom = st.text_input("Subdominio:", value=df_actual.loc[idx_sel, "Subdominio"])
                e_maps = st.text_input("Google Maps:", value=df_actual.loc[idx_sel, "GoogleMaps"])
                e_rubro = st.text_input("Rubro:", value=df_actual.loc[idx_sel, "Rubro"])
                e_barrio = st.text_input("Barrio/Zona:", value=df_actual.loc[idx_sel, "Barrio/Zona"])
                e_wpp = st.text_input("WhatsApp:", value=df_actual.loc[idx_sel, "WhatsApp"])
                e_ig = st.text_input("Instagram:", value=df_actual.loc[idx_sel, "Instagram"])
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    actualizar = st.form_submit_button("🔄 Actualizar Datos")
                with col_btn2:
                    eliminar = st.form_submit_button("🗑️ Eliminar Comercio")
                    
                if actualizar:
                    df_actual.loc[idx_sel] = [e_nombre, e_subdom, e_maps, e_rubro, e_barrio, e_wpp, e_ig]
                    guardar_clientes(df_actual)
                    st.success("Cambios guardados con éxito.")
                    st.rerun()
                if eliminar:
                    df_actual = df_actual.drop(idx_sel).reset_index(drop=True)
                    guardar_clientes(df_actual)
                    st.warning("Comercio eliminado.")
                    st.rerun()

# --- VISTA PÚBLICA DE USUARIO ---
st.markdown("### 🔍 Buscador Inteligente")
tab_rubro, tab_ubicacion = st.tabs(["🗂️ Filtrar por Rubro", "📍 Ordenar por Cercanía"])

with tab_rubro:
    rubros_disponibles = ["Todos"] + [r for r in df_actual["Rubro"].unique() if r]
    rubro_elegido = st.selectbox("Selecciona una categoría:", rubros_disponibles)

with tab_ubicacion:
    st.write("Ubicación para medir distancias reales:")
    col_lat, col_lng = st.columns(2)
    with col_lat:
        u_lat = st.number_input("Tu Latitud:", value=-34.9011, format="%.4f")
    with col_lng:
        u_lng = st.number_input("Tu Longitud:", value=-56.1645, format="%.4f")
    barrios_disponibles = ["Todos"] + [b for b in df_actual["Barrio/Zona"].unique() if b]
    barrio_elegido = st.selectbox("Filtrar por Barrio:", barrios_disponibles)

# Filtrado y ordenamiento por ubicación
lista_render = []
for _, row in df_actual.iterrows():
    if rubro_elegido != "Todos" and row["Rubro"] != rubro_elegido:
        continue
    if barrio_elegido != "Todos" and row["Barrio/Zona"] != barrio_elegido:
        continue
        
    coords = extraer_coordenadas(row["GoogleMaps"])
    distancia = calcular_distancia_km(u_lat, u_lng, coords[0], coords[1]) if coords else 9999.0
    
    lista_render.append({
        "Nombre": row["Nombre"], "Subdominio": row["Subdominio"],
        "Rubro": row["Rubro"], "Barrio": row["Barrio/Zona"], "Distancia": distancia,
        "WhatsApp": row["WhatsApp"], "Instagram": row["Instagram"], "GoogleMapsRaw": row["GoogleMaps"]
    })

df_render = pd.DataFrame(lista_render)
if not df_render.empty:
    df_render = df_render.sort_values(by="Distancia")

# Despliegue de tarjetas dinámicas con su botonera integrada
st.write("---")
if df_render.empty:
    st.info("No hay comercios que coincidan con la búsqueda.")
else:
    for idx, row in df_render.iterrows():
        dist_txt = f"📍 A {row['Distancia']:.1f} km" if row['Distancia'] < 5000 else f"🏙️ {row['Barrio']}"
        
        # Tarjeta Visual Base
        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border-left: 5px solid #114294; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 5px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #114294; font-size: 1.1rem;">{row['Nombre']}</h4>
                        <span style="background-color: #f0ad11; color: #114294; padding: 1px 6px; border-radius: 8px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin-top: 4px;">{row['Rubro']}</span>
                    </div>
                    <div style="text-align: right; color: #555555; font-weight: bold; font-size: 0.85rem;">{dist_txt}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botonera de interacción abajo de la tarjeta
        col_web, col_wpp, col_ig, col_map = st.columns([2, 1, 1, 1])
        
        with col_web:
            st.link_button("🌐 Visitar Sitio", row['Subdominio'], use_container_width=True)
        
        with col_wpp:
            if row['WhatsApp']:
                clean_wpp = str(row['WhatsApp']).replace(" ", "").replace("+", "")
                if clean_wpp.startswith("09"):
                    clean_wpp = "598" + clean_wpp[1:]
                st.link_button("🟢 Wpp", f"https://wa.me/{clean_wpp}", use_container_width=True)
            else:
                st.button("🟢", disabled=True, use_container_width=True, help="No tiene WhatsApp")
                
        with col_ig:
            if row['Instagram']:
                clean_ig = str(row['Instagram']).replace("@", "").strip()
                st.link_button("📸 IG", f"https://instagram.com/{clean_ig}", use_container_width=True)
            else:
                st.button("📸", disabled=True, use_container_width=True, help="No tiene Instagram")
                
        with col_map:
            if row['GoogleMapsRaw']:
                url_final_mapa = row['GoogleMapsRaw'] if "http" in str(row['GoogleMapsRaw']) else f"https://www.google.com/maps/search/?api=1&query={row['GoogleMapsRaw']}"
                st.link_button("📍 Mapa", url_final_mapa, use_container_width=True)
            else:
                st.button("📍", disabled=True, use_container_width=True, help="No tiene mapa")