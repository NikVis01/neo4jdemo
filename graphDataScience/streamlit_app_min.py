import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load JSON
plot_df = pd.read_json("/home/lethal365/Twiga_Proj/graphDataScience/plot_df_umap.json", orient="records")

# Prepare lines from (0,0,0) to each embedding vector
lines = []
for _, row in plot_df.iterrows():
    lines.append(
        go.Scatter3d(
            x=[0, row['x']],
            y=[0, row['y']],
            z=[0, row['z']],
            mode='lines',
            line=dict(width=2, color='royalblue'),
            showlegend=False
        )
    )

layout = go.Layout(
    title='3D UMAP Embedding Vectors from Origin',
    scene=dict(
        xaxis=dict(title='X'),
        yaxis=dict(title='Y'),
        zaxis=dict(title='Z'),
    ),
    height=800,
    margin=dict(l=0, r=0, t=30, b=0),
    
)

fig = go.Figure(data=lines, layout=layout)
st.plotly_chart(fig, use_container_width=True)
