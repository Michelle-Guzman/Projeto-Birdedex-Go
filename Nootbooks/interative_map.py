import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from matplotlib import cm, colors

# ============================================================
# CONFIGURAÇÕES
# ============================================================
BASE_DIR = "/Users/trash/Downloads/Projeto_Disciplina/Cidade_sp"
OBS_FILE = os.path.join(BASE_DIR, "data_filtered/observations_sao_paulo.csv")
CLUSTER_FILE = os.path.join(BASE_DIR, "processed/user_clusters_kmeans_final.csv")

OUTPUT_MAP_DIR = os.path.join(BASE_DIR, "processed", "maps")
os.makedirs(OUTPUT_MAP_DIR, exist_ok=True)

# ============================================================
# 1️⃣ CARREGAR DADOS
# ============================================================
obs = pd.read_csv(OBS_FILE)
clusters = pd.read_csv(CLUSTER_FILE)

# Garantir nomes das colunas
lat_col = "latitude" if "latitude" in obs.columns else "private_latitude"
lon_col = "longitude" if "longitude" in obs.columns else "private_longitude"

if "cluster" not in clusters.columns:
    alt = [c for c in clusters.columns if "cluster" in c.lower()][0]
    clusters = clusters.rename(columns={alt: "cluster"})

if "user_login" not in clusters.columns:
    alt_user = [c for c in clusters.columns if "user" in c.lower()][0]
    clusters = clusters.rename(columns={alt_user: "user_login"})

# Merge observações com clusters
df = obs.merge(clusters, on="user_login", how="inner")

# ============================================================
# 2️⃣ CRIAR MAPA INTERATIVO
# ============================================================
sp_center = [-23.55, -46.63]
m = folium.Map(location=sp_center, zoom_start=11)

# Gerar cores para cada cluster
n_clusters = df["cluster"].nunique()
cmap = cm.get_cmap("tab20", n_clusters)
cluster_colors = {i: colors.rgb2hex(cmap(i)) for i in sorted(df["cluster"].unique())}

# Adicionar pontos com MarkerCluster
marker_cluster = MarkerCluster().add_to(m)
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row[lat_col], row[lon_col]],
        radius=4,
        color=cluster_colors[row["cluster"]],
        fill=True,
        fill_opacity=0.7,
        popup=f"Cluster: {row['cluster']}<br>User: {row['user_login']}<br>Species: {row['scientific_name']}"
    ).add_to(marker_cluster)

# ============================================================
# 3️⃣ SALVAR MAPA
# ============================================================
map_file = os.path.join(OUTPUT_MAP_DIR, "cluster_map_interactive_kmeans.html")
m.save(map_file)
print(f"✅ Mapa interativo salvo em: {map_file}")
