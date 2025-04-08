import streamlit as st
from backend_comun import autenticar_google_sheets
from backend_simulindex import obtener_historicos, obtener_meff_trimestral, obtener_grafico_meff, hist_mensual, graf_hist
from backend_comun import carga_rapida_sheets, carga_total_sheets, colores_precios

from utilidades import generar_menu

# CONSTANTES
#SPREADSHEET_ID = st.secrets['SPREADSHEET_ID']

generar_menu()


if 'client' not in st.session_state:
    st.session_state.client = autenticar_google_sheets()
#if 'ultima_fecha_sheets' not in st.session_state:
#    carga_rapida_sheets()

df_historicos_FTB, ultimo_registro = obtener_historicos()
df_FTB_trimestral_filtrado, fecha_ultimo_omip, media_omip_calc = obtener_meff_trimestral(df_historicos_FTB)
graf_omip_trim = obtener_grafico_meff(df_FTB_trimestral_filtrado)

if 'omip_slider' not in st.session_state:
    st.session_state.omip_slider = round(media_omip_calc)
def reset_slider():
    st.session_state.omip_slider = round(media_omip_calc)

#df_hist = leer_excel()
df_hist = hist_mensual()
grafico, simul20, simul30, simul61 = graf_hist(df_hist, st.session_state.omip_slider, colores_precios)
# a los precios simulados resultantes le incrementamos el coste medio de los pyc 2025
simul20 = round(simul20 + 0.38, 2)
simul30 = round(simul30 + 0.18, 2)
simul61 = round(simul61 + 0.1, 2)


# Inicializamos margen a cero
if 'margen' not in st.session_state:
    st.session_state.margen = 0


#BARRA LATERAL+++++++++++++++++++++++++++++++++++++++++++++++++++++++
st.sidebar.header('', divider='rainbow')
st.sidebar.header('Simulación de indexados')
st.sidebar.subheader('¡Personaliza la simulación!')
st.sidebar.info('Usa el deslizador para modificar el valor de :green[OMIP]. No te preocupes, siempre puedes resetear al valor por defecto.', icon = "ℹ️")
with st.sidebar.container(border = True):
    st.slider(':green[OMIP] en €/MWh', min_value = 30, max_value = 150, step = 1, key = 'omip_slider')
    reset_omip = st.sidebar.button('Resetear OMIP', on_click = reset_slider)
  


with st.sidebar.container(border=True):
    st.sidebar.subheader('¡Más interacción!')
    st.sidebar.info('¿Quieres afinar un poco más. Añade :violet[margen] al gusto y obtén un precio medio de indexado más ajustado con tus necesidades.', icon="ℹ️")
    añadir_margen = st.sidebar.toggle('Quieres añadir :violet[margen]?')
    if añadir_margen:
        st.sidebar.slider('Añade margen al precio base de indexado en €/MWh', min_value = 1, max_value = 50, step = 1, key = 'margen')

zona_mensajes = st.sidebar.empty()


simul20_margen = simul20 + st.session_state.margen / 10
simul30_margen = simul30 + st.session_state.margen / 10
simul61_margen = simul61 + st.session_state.margen / 10

##LAYOUT DE LA PÁGINA PRINCIPAL-----------------------------------------------------------------------------------------------------------------------------
#st.title("Simulindex :orange[e]PowerAPP©")
#st.subheader("Tu aplicación para simular los futuros precios minoristas de indexado")
#st.caption("Copyright by Jose Vidal :ok_hand:")
#url_apps = "https://powerappspy-josevidal.streamlit.app/"
#st.write("Visita mi página de [ePowerAPPs](%s) con un montón de utilidades" % url_apps)
#url_linkedin = "https://www.linkedin.com/posts/josefvidalsierra_epowerapps-spo2425-telemindex-activity-7281942697399967744-IpFK?utm_source=share&utm_medium=member_deskto"
#url_bluesky = "https://bsky.app/profile/poweravenger.bsky.social"
#st.markdown(f"Deja tus comentarios y propuestas en mi perfil de [Linkedin]({url_linkedin}) - ¡Sígueme en [Bluesky]({url_bluesky})!")



#PRIMERA TANDA DE GRÁFICOS. SIMULACION DE PRECIOS DE INDEXADO------------------------------------------------------------------------------------------------------------------


col1, col2 = st.columns([0.2, 0.8])
with col1:
    st.info('A partir de :green[OMIP] y opcionalmente :violet[margen] añadido, obtendrás unos precios medios de indexado.', icon = "ℹ️")
    with st.container(border = True):
        st.subheader(':blue-background[Datos de entrada]', divider = 'rainbow')
        col11, col12 = st.columns(2)
        with col11:
            st.metric(':green[OMIP] (€/MWh)', value = st.session_state.omip_slider, help = 'Este es el valor OMIP de referencia que has utilizado como entrada')
        with col12:
            st.metric(':violet[Margen] (€/MWh)', value = st.session_state.margen, help = 'Margen que añades para obtener un precio medio final más ajustado a tus necesidades')
    with st.container(border = True):
        st.subheader(':green-background[Datos de salida]', divider = 'rainbow')
        col13, col14 = st.columns(2)
        with col13:
            st.text('Precios base')
            st.metric(':orange[Precio 2.0] c€/kWh', value = simul20, help = 'Este el precio 2.0 medio simulado a un año vista')
            st.metric(':red[Precio 3.0] c€/kWh', value = simul30, help = 'Este el precio 3.0 medio simulado a un año vista')
            st.metric(':blue[Precio 6.1] c€/kWh', value = simul61, help='Este el precio 6.1 medio simulado a un año vista')
        with col14:
            st.text('Precios con margen')
            st.metric(':orange[Precio 2.0] c€/kWh', value = round(simul20_margen, 2), help = 'Este el precio 2.0 con el margen añadido')
            st.metric(':red[Precio 3.0] c€/kWh', value = round(simul30_margen, 2), help = 'Este el precio 3.0 con el margen añadido')
            st.metric(':blue[Precio 6.1] c€/kWh', value = round(simul61_margen, 2), help = 'Este el precio 6.1 con el margen añadido')
    
with col2:
    st.info('**¿Cómo funciona?** Los :orange[puntos] son valores de indexado de los 12 últimos meses. Las :orange[líneas] reflejan una tendencia. Los :orange[círculos] simulan los precios medios de indexado a un año vista en base al valor de OMIP usado por defecto o seleccionado por ti.',icon="ℹ️")
    st.plotly_chart(grafico)            

#SEGUNDA TANDA DE GRÁFICOS. OMIP TRIMESTRAL------------------------------------------------------------------------------------------------------------------
col3, col4 = st.columns([0.2, 0.8])
with col3:
    with st.container(border = True):
        st.info('Aquí tienes el valor medio de :green[OMIP] en €/MWh a partir de los siguientes trimestres, así como la fecha del último registro.', icon = "ℹ️")
        st.subheader('Datos de OMIP', divider = 'rainbow')
        col31, col32 = st.columns(2)
        with col31:
            st.metric('Fecha', value = fecha_ultimo_omip)
        with col32:
            st.metric(':green[OMIP] medio', value = media_omip_calc)
with col4:
    st.info('Aquí tienes la evolución de :green[OMIP] por trimestres', icon = "ℹ️")            
    st.write(graf_omip_trim)



