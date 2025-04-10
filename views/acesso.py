import streamlit as st
from forms.contact import contact_form
from views.cliente_criar import showcliente

st.set_page_config(page_title='ORACULO MED', page_icon="🔍", layout="wide")


def showhome():

    # --- HERO SECTION ---
    col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
    with col1:
        st.image("./src/img/oraculo-logo.png", width=230)

    with col2:
        st.title("SOLICITAR MEU ACESSO!", anchor=False)
        st.write("Sistema super avançado de coleta de dados com inteligência artificial.")
        if st.button("✉SOLICITAR ACESSO"):
            showcliente()


    # --- EXPERIENCE & QUALIFICATIONS ---
    st.write("\n")
    st.subheader("Experience & Qualifications", anchor=False)
    st.write(
        """
        - 7 Years experience extracting actionable insights from data
        - Strong hands-on experience and knowledge in Python and Excel
        - Good understanding of statistical principles and their respective applications
        - Excellent team-player and displaying a strong sense of initiative on tasks
        """
    )

    # --- SKILLS ---
    st.write("\n")
    st.subheader("Hard Skills", anchor=False)
    st.write(
        """
        - Programming: Python (Scikit-learn, Pandas), SQL, VBA
        - Data Visualization: PowerBi, MS Excel, Plotly
        - Modeling: Logistic regression, linear regression, decision trees
        - Databases: Postgres, MongoDB, MySQL
        """
    )
