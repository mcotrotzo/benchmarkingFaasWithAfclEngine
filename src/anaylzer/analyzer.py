from plotly_integration.sheet import SheetManager
import streamlit as st
def main():
    st.set_page_config(
        page_title="Anaylzer",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="expanded"
        )
    st.markdown(
        r"""
        <style>
        .stAppDeployButton {
                visibility: hidden;
            }
        </style>
        """, unsafe_allow_html=True
    )
    
    st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)
    st.title("Analyzer")
    sheet_maanger = SheetManager()
    sheet_maanger.load()

if __name__ == "__main__":
    main()
