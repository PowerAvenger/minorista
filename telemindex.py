import streamlit as st
from backend import (filtrar_mes, aplicar_margen, graf_principal, pt5_trans, pt1, pt7_trans, costes_indexado, 
    autenticar_google_sheets, carga_rapida_sheets, carga_total_sheets, actualizar_sheets
)
import pandas as pd
import datetime


st.set_page_config(
    page_title="Telemindex",
    page_icon=":bulb:",
    layout='wide',
    menu_items={
        'Get help':'https://www.linkedin.com/in/jfvidalsierra/',
        'About':'https://www.linkedin.com/in/jfvidalsierra/'
        }
    )

#if "cache_cleared" not in st.session_state:
#    st.cache_data.clear()  # Limpiar caché al iniciar
#    st.session_state.cache_cleared = True  # Evita que se borre en cada interacción


# CONSTANTES
SPREADSHEET_ID = st.secrets['SPREADSHEET_ID']

# INICIALIZAMOS VARIABLES
if 'client' not in st.session_state:
    st.session_state.client = autenticar_google_sheets()
if 'rango_temporal' not in st.session_state:
    st.session_state.rango_temporal = 'Selecciona un día'
if 'año_seleccionado' not in st.session_state:
    st.session_state.año_seleccionado = 2025
if 'mes_seleccionado' not in st.session_state: 
    st.session_state.mes_seleccionado = 'enero'
if 'ultima_fecha_sheets' not in st.session_state:
    carga_rapida_sheets(SPREADSHEET_ID)
if 'dia_seleccionado' not in st.session_state:
    st.session_state.dia_seleccionado = st.session_state.ultima_fecha_sheets
if 'texto_precios' not in st.session_state:
    st.session_state.texto_precios = f'Día seleccionado: {st.session_state.ultima_fecha_sheets}'
if 'margen' not in st.session_state: 
    st.session_state.margen = 0
    
columnas_numericas = st.session_state.df_sheets.columns.difference(['fecha', 'mes_nombre', 'dh_3p', 'dh_6p'])  # Excluir columnas de texto si las hay
# 🔹 Convertir todas las columnas a numérico (int o float según corresponda)
st.session_state.df_sheets[columnas_numericas] = st.session_state.df_sheets[columnas_numericas].apply(pd.to_numeric, errors='coerce')


df_filtrado, lista_meses = filtrar_mes()

#ejecutamos la función para obtener la tabla resumen y precios medios
tabla_precios, media_20, media_30, media_61, media_spot, media_ssaa = pt5_trans(df_filtrado)
media_20 = round(media_20 / 10, 1)
media_30 = round(media_30 / 10, 1)
media_61 = round(media_61 / 10, 1)
media_spot = round(media_spot, 2)
media_ssaa = round(media_ssaa, 2)
media_combo = media_spot + media_ssaa
sobrecoste_ssaa = ((media_combo / media_spot) - 1) * 100

#tabla resumen de costes ATR
tabla_atr = pt7_trans(df_filtrado)
tabla_costes = costes_indexado(df_filtrado)



#ELEMENTOS DE LA BARRA LATERAL ---------------------------------------------------------------------------------------

st.sidebar.subheader('Opciones')
with st.sidebar.container(border=True):
    st.sidebar.radio("Seleccionar rango temporal", ['Por años', 'Por meses', 'Selecciona un día'], key = "rango_temporal")

    if st.session_state.rango_temporal == 'Por años':
        st.sidebar.selectbox('Seleccione el año', options = [2025, 2024, 2023], key = 'año_seleccionado') 
        st.session_state.texto_precios = f'Año {st.session_state.año_seleccionado}, hasta el día {st.session_state.ultima_fecha_sheets}'
    elif st.session_state.rango_temporal =='Por meses' : 
        col_sb1, col_sb2 = st.sidebar.container().columns(2)      
        with col_sb1:
            st.sidebar.selectbox('Seleccione el año', options = [2025, 2024, 2023], key = 'año_seleccionado') 
        with col_sb2:
            st.sidebar.selectbox('Seleccionar mes', lista_meses, key = 'mes_seleccionado')
            st.session_state.texto_precios = f'Seleccionado: {st.session_state.mes_seleccionado} de {st.session_state.año_seleccionado}'
    else:
        st.sidebar.date_input('Selecciona un día', min_value = datetime.date(2023, 1, 1), max_value = st.session_state.ultima_fecha_sheets, key = 'dia_seleccionado')  
        st.session_state.texto_precios = f'Día seleccionado {st.session_state.dia_seleccionado}'
with st.sidebar.container():
#if st.sidebar.toggle('Marca si quieres añadir margen'):
    st.sidebar.slider("Añadir margen al gusto (en €/MWh)", min_value = 0, max_value = 50, value = 0, key = 'margen', on_change = aplicar_margen, args=(df_filtrado,))
    st.sidebar.caption(f'Se ha añadido {st.session_state.margen} €/MWh')
#else:
#    st.session_state.margen = 0
    
#no usado
actualizar = False
with st.sidebar.container():
    zona_mensajes = st.sidebar.empty()
    zona_fechas = st.sidebar.empty()
    zona_fechas.write(f'Última fecha disponible: {st.session_state.ultima_fecha_sheets}')

    if st.sidebar.button('Actualizar registros', disabled=True):
        mensaje = actualizar_sheets()
        zona_mensajes.warning(mensaje)
        zona_fechas.write(f'Última fecha disponible: {st.session_state.ultima_fecha_sheets}')



#ELEMENTOS DE LA BARRA LATERAL ---------------------------------------------------------------------------------------


## LAYOUT DE LA PÁGINA PRINCIPAL+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
st.title("Telemindex 2023-2025 :orange[e]PowerAPP©")
st.caption("Tu aplicación para saber los precios minoristas de indexado. Copyright by Jose Vidal :ok_hand:")
#st.caption("Copyright by Jose Vidal :ok_hand:")
url_apps = "https://powerappspy-josevidal.streamlit.app/"
url_linkedin = "https://www.linkedin.com/posts/josefvidalsierra_epowerapps-spo2425-telemindex-activity-7281942697399967744-IpFK?utm_source=share&utm_medium=member_deskto"
url_bluesky = "https://bsky.app/profile/poweravenger.bsky.social"
#st.write("Visita mi página de [ePowerAPPs](%s) con un montón de utilidades" % url_apps)
st.markdown(f"Visita mi página de [ePowerAPPs]({url_apps}). Deja tus comentarios y propuestas en mi perfil de [Linkedin]({url_linkedin}) - ¡Sígueme en [Bluesky]({url_bluesky})!")

# Cargamos datos

zona_grafica = st.empty()


with zona_grafica.container():

    col1, col2 = st.columns([.7,.3])

    #COLUMNA PRINCIPAL
    with col1:
        st.subheader(f'Resumen de precios medios minoristas por peaje de acceso. **:orange[{st.session_state.texto_precios}]**', divider = 'rainbow')
        
        with st.container():
            col5, col6, col7, col8, col9 = st.columns(5)
            with col5:
                st.metric(':orange[Precio medio 2.0 c€/kWh]',value = media_20)
            with col6:
                st.metric(':red[Precio medio 3.0 c€/kWh]',value = media_30)
            with col7:
                st.metric(':blue[Precio medio 6.1 c€/kWh]',value = media_61)
            with col8:
                st.metric(':green[Precio medio Spot €/MWh]',value = media_spot)
            with col9:
                st.metric('Precio medio SSAA €/MWh', value = media_ssaa, delta = f'{sobrecoste_ssaa:,.1f}%', delta_color = 'inverse', help= 'Se indica su valor medio y en qué % aumenta el precio medio Spot')
        st.empty()
        # gráfico principal de barras y lineas precios medios y omie+ssaa
        st.plotly_chart(graf_principal(df_filtrado))
        st.empty()
        st.subheader("Peso de los componentes por peaje de acceso", divider='rainbow')
        _, graf20, graf30, graf61 = pt1(df_filtrado)
        col10,col11,col12=st.columns(3)
        with col10:
            st.write(graf20)    
        with col11:
            st.write(graf30)
        with col12:
            st.write(graf61)    


    with col2:
        st.subheader("Tabla resumen de precios por peaje de acceso", divider='rainbow')
        with st.expander("Nota sobre los precios de indexado:"):
            st.caption("Basados en las fórmulas tipo con todos los componentes de mercado y costes regulados. Se incluye FNEE, SRAD y 2€ en desvíos. Por supuesto peajes y cargos según tarifa de acceso. Añadir margen al gusto en 'Opciones' de la barra lateral")
            
        with st.container():

            tabla_margen = pd.DataFrame(columns = tabla_precios.columns, index = ['margen_2.0', 'margen_3.0', 'margen_6.1'])
            tabla_margen = tabla_margen.fillna(st.session_state.margen / 10)
                
            texto_precios=f'{st.session_state.texto_precios}. Precios en c€/kWh'
            st.caption(st.session_state.texto_precios)

            st.text ('Precios medios de indexado', help='PRECIO MEDIO (FINAL) DE LA ENERGÍA.Suma de costes (energía y ATR)')
            st.dataframe(tabla_precios, use_container_width=True)
            
            st.text ('Costes medios de indexado', help = 'COSTE MEDIO DE LA ENERGÍA, sin incluir ATR.')
            st.dataframe(tabla_costes, use_container_width=True)
            
            st.text ('Costes de ATR')
            #tabla_atr['Media'] = (tabla_precios['Media'] - tabla_costes['Media']).fillna(0)
            st.dataframe(tabla_atr, use_container_width=True )
            
            st.text ('Margen')
            st.dataframe(tabla_margen, use_container_width=True )


            print(tabla_precios)
            print(tabla_costes)
            print(tabla_atr)
        


if 'df_sheets_full' not in st.session_state:
    zona_mensajes.warning('Cargados datos iniciales. Espera a que estén disponibles todos los datos', icon = '⚠️')
    #st.session_state.df_sheets_full = actualizar_sheets(SPREADSHEET_ID, actualizar)
    st.session_state.df_sheets_full = carga_total_sheets(SPREADSHEET_ID)
    st.session_state.df_sheets = st.session_state.df_sheets_full
    zona_mensajes.success('Cargados todos los datos. Ya puedes consultar los históricos', icon = '👍')