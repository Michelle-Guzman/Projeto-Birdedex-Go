import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import umap.umap_ as umap
from sklearn.cluster import KMeans

# ============================================================
# CONFIGURAÇÕES
# ============================================================
DATA_PATH = "processed/user_features_normalized.csv"
FIG_DIR = "figs/cluster_analysis"
os.makedirs(FIG_DIR, exist_ok=True)

# Melhor setup encontrado
N_NEIGHBORS = 100
BEST_K = 2

print(f" Analisando clusters com n_neighbors={N_NEIGHBORS}, K={BEST_K}")

# ============================================================
# 1️ CARREGAR DADOS
# ============================================================
df = pd.read_csv(DATA_PATH, index_col=0)
species_cols = [c for c in df.columns if c not in ['latitude', 'longitude', 'num_observations']]

print(f" Dados carregados: {df.shape[0]} usuários × {len(species_cols)} espécies/features")

# ============================================================
# 2️ NORMALIZAR E RECRIAR EMBEDDING + CLUSTERS
# ============================================================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

reducer = umap.UMAP(
    n_neighbors=N_NEIGHBORS,
    n_components=2,
    random_state=42,
    min_dist=0.1,
    metric="euclidean"
)
X_umap = reducer.fit_transform(X_scaled)

km = KMeans(n_clusters=BEST_K, random_state=42)
df["cluster"] = km.fit_predict(X_umap)

# Salvar coordenadas UMAP
df["umap_x"] = X_umap[:, 0]
df["umap_y"] = X_umap[:, 1]

print(" Clusters e embeddings gerados com sucesso!")

# ============================================================
# 3️ RESUMO GERAL DOS CLUSTERS
# ============================================================
summary = df.groupby("cluster").agg({
    "latitude": "mean",
    "longitude": "mean",
    "num_observations": ["mean", "sum", "count"]
})
summary.columns = ["lat_mean", "lon_mean", "obs_mean", "obs_sum", "n_users"]
summary.to_csv("processed/cluster_summary.csv")
print("\n📊 Resumo geral salvo em processed/cluster_summary.csv")
print(summary)

# ============================================================
# 4️ ESPÉCIES MAIS REPRESENTATIVAS POR CLUSTER
# ============================================================
top_species = {}
for c in df["cluster"].unique():
    sub = df[df["cluster"] == c][species_cols]
    mean_counts = sub.mean().sort_values(ascending=False)
    top_species[c] = mean_counts.head(15).index.tolist()

top_species_df = pd.DataFrame.from_dict(top_species, orient="index").T
top_species_df.to_csv("processed/top_species_per_cluster.csv", index=False)
print("\n🕊️ Top espécies salvas em processed/top_species_per_cluster.csv")

# ============================================================
# 5️ GRÁFICOS
# ============================================================

# --- 5.1 Distribuição UMAP
plt.figure(figsize=(8, 6))
plt.scatter(df["umap_x"], df["umap_y"], c=df["cluster"], cmap="Spectral", s=15)
plt.title(f"Distribuição UMAP + KMeans (K={BEST_K}, n_neighbors={N_NEIGHBORS})")
plt.xlabel("UMAP-1")
plt.ylabel("UMAP-2")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/umap_clusters.png", dpi=300)
plt.close()

# --- 5.2 Distribuição geográfica
plt.figure(figsize=(8, 6))
plt.scatter(df["longitude"], df["latitude"], c=df["cluster"], cmap="Spectral", s=15)
plt.title("Distribuição geográfica dos clusters de usuários")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/geo_clusters.png", dpi=300)
plt.close()

# --- 5.3 Esforço amostral por cluster
plt.figure(figsize=(6, 4))
sns.boxplot(x="cluster", y="num_observations", data=df)
plt.title("Número de observações por cluster")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/effort_per_cluster.png", dpi=300)
plt.close()

print("\n Figuras salvas em:", FIG_DIR)
print(" Análise completa concluída com sucesso!")

