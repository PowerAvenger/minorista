import streamlit as st

def generar_menu():
    with st.sidebar:
        st.header('Indexados :orange[e]PowerAPP©')
        st.image('images/banner.png')
        st.caption("Copyright by Jose Vidal :ok_hand:")
        url_apps = "https://powerappspy-josevidal.streamlit.app/"
        st.write("Visita mi página de [ePowerAPPs](%s) con un montón de utilidades." % url_apps)
        url_linkedin = "https://www.linkedin.com/posts/josefvidalsierra_epowerapps-spo2425-telemindex-activity-7281942697399967744-IpFK?utm_source=share&utm_medium=member_deskto"
        url_bluesky = "https://bsky.app/profile/poweravenger.bsky.social"
        st.markdown(f"Deja tus comentarios y propuestas en mi perfil de [Linkedin]({url_linkedin}) - ¡Sígueme en [Bluesky]({url_bluesky})!")
        st.page_link('intro.py', label = 'Bienvenida', icon = "🙌")
        st.page_link('pages/telemindex.py', label = 'Telemindex', icon = "🗂️")
        st.page_link('pages/simulindex.py', label = 'Simulindex', icon = "🔮")