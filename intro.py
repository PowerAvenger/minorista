import streamlit as st
import base64

st.set_page_config(
    page_title="Index",
    page_icon=":bulb:",
    layout='wide',
    #layout='centered',
    #initial_sidebar_state='collapsed'
    initial_sidebar_state='expanded'
)

c1, c2, c3 = st.columns(3)

with c2:
    st.title('Indexados :orange[e]PowerAPP©')
    st.caption("Copyright by Jose Vidal :ok_hand:")
    url_apps = "https://powerappspy-josevidal.streamlit.app/"
    st.write("Visita mi página de [PowerAPPs](%s) con un montón de utilidades." % url_apps)
    url_linkedin = "https://www.linkedin.com/posts/josefvidalsierra_epowerapps-spo2425-telemindex-activity-7281942697399967744-IpFK?utm_source=share&utm_medium=member_deskto"
    url_bluesky = "https://bsky.app/profile/poweravenger.bsky.social"
    st.markdown(f"Deja tus comentarios y propuestas en mi perfil de [Linkedin]({url_linkedin}) - ¡Sígueme en [Bluesky]({url_bluesky})!")
    #with st.container(border=True):
    #    st.image('images/banner.png', use_column_width=True)

    with open("images/banner.png", "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()

    # Mostrar la imagen con estilo
    st.markdown(f"""
        <style>
            .img-redonda {{
                border-radius: 10px;
                width: 100%;
                height: auto;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
            }}
        </style>
        <img src="data:image/png;base64,{encoded}" class="img-redonda"/>
    """, unsafe_allow_html=True)


    st.text('')
    st.text('')
    st.info('¡Bienvenido a la :orange[e]PowerAPP** del mercado minorista de la electricidad**! \n\n'
            'Presente, pasado y futuro de los precios de indexados minoristas.\n'
            'No dudes en contactar para comentar errores detectados o proponer mejoras en la :orange[e]PowerAPP'
            ,icon="ℹ️")
    
    acceso_telemindex = st.button('🚀 Acceder a indexados', type='primary', use_container_width=True)
    #acceso_simulindex = st.button('🔮 Acceder a **Simulindex**', type='primary', use_container_width=True)
    if acceso_telemindex:
        st.switch_page('pages/telemindex.py')
    #if acceso_simulindex:
    #    st.switch_page('pages/simulindex.py')
    


    