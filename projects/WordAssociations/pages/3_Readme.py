import streamlit as st
from pathlib import Path


markdown_content = Path("pages/dataReadme/readme1.md").read_text()
st.markdown(markdown_content)

absolute_path = Path("dataReadme/network_rechtsextrem.PNG").resolve()
st.image(str(absolute_path))

markdown_content = Path("pages/dataReadme/readme2.md").read_text()
st.markdown(markdown_content)



