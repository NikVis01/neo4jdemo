from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# Original (1500D) embedding matrix
import streamlit as st
import plotly.graph_objects as go

embedding_df = pd.read_json("/home/lethal365/Twiga_Proj/graphDataScience/plot_df_unscaled.json")
matrix = embedding_df
print(matrix)

sim_matrix = cosine_similarity(matrix)

# Optionally convert to DataFrame
sim_df = pd.DataFrame(sim_matrix, index=embedding_df['node_id'], columns=embedding_df['node_id'])

# Plot
plt.figure(figsize=(10, 8))
sns.heatmap(sim_df, cmap='coolwarm')
plt.title('Cosine Similarity Between Node Embeddings')
st.pyplot(plt.gcf())
