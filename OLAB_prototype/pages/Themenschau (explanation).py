import streamlit as st

st.set_page_config(page_title="Network Analysis Explained", layout="wide")

st.title("Understanding the Bundestag Topic Network")

st.markdown("---")

# SECTION 1: NETWORK CONSTRUCTION
st.header("1️⃣ Network Construction")

st.write("""
We start from the **topic–TOP matrix** (rows = Tagesordnungspunkte, 
columns = topics).  

From this, we construct a **topic–topic similarity network**:

- Each **node** = one topic
- Each **edge** = cosine similarity between two topics
- Edge **sign** = positive (blue) if topics co-occur, negative (red) if they are in opposition
- Edge **weight** = strength of similarity
- A **threshold** is applied to keep only relevant connections
""")

st.info("This transforms our high-dimensional theme data into a network of semantic relations.")

st.markdown("---")

# SECTION 2: PCA LAYOUT
st.header("2️⃣ PCA Layout")

st.write("""
The network layout is determined by **Principal Component Analysis (PCA)**:

- We compute the **similarity matrix** between topics
- Then extract the first 2–3 **principal components**
- These components provide **coordinates** for each topic in 2D space
- The result: topics that behave similarly across TOPs are plotted close together

✨ This gives a **geometry of ideas**, where clusters naturally appear.
""")

st.success("Users can switch between PC1–PC2, PC1–PC3, and PC2–PC3 mappings interactively.")

st.markdown("---")

# SECTION 3: NODE COLORING (CLUSTERING)
st.header("3️⃣ Node Coloring (Clustering)")

st.write("""
To reveal **communities of topics**, we use a **signed best-response dynamics** algorithm:

- Each node starts with its own color
- Iteratively, each node updates its color:
  - **Positive edges** → favor adopting neighbor’s color
  - **Negative edges** → discourage adopting neighbor’s color
  - **Self-vote** → stabilizes decisions
- The process continues until **no further changes occur**

🎨 The final colors show **coherent topic groups**:
topics that support each other are grouped, while opposing topics are separated.
""")

st.warning("This method respects the *signed* nature of the network — unlike standard modularity clustering.")

st.markdown("---")

# SECTION 4: THE BIG PICTURE
st.header("4️⃣ The Big Picture")

st.write("""
Putting it all together:

1. **Build** the topic similarity network  
2. **Lay out** the nodes using PCA for interpretable geometry  
3. **Cluster** the nodes with best-response dynamics for signed graphs  

➡️ The result is a **map of themes** in Bundestag debates:  
which topics align, which oppose, and how they structure the agenda.
""")

#st.balloons()
