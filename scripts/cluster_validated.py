import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import umap.umap_ as umap

# ============================================================
# CONFIGURAÇÕES
# ============================================================
DATA_FILE = "data_filtered/observations_sao_paulo.csv"
PROCESSED_DIR = "processed"
FIG_DIR = "figs/cluster_analysis"
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# ============================================================
# 1️ CARREGAR DADOS
# ============================================================
print(" Carregando dados...")
df = pd.read_csv(DATA_FILE)
df = df[df["iconic_taxon_name"] == "Aves"]
df = df.dropna(subset=["user_login", "scientific_name", "latitude", "longitude"])

print(f" Observações: {len(df):,}")
print(f" Usuários: {df['user_login'].nunique():,}")
print(f" Espécies: {df['scientific_name'].nunique():,}")

# ============================================================
# 2️ CRIAR MATRIZ USUÁRIO × ESPÉCIE + FEATURES
# ============================================================
print("\n Criando matriz usuário × espécie...")
user_species = (
    df.groupby(["user_login", "scientific_name"])
      .size()
      .unstack(fill_value=0)
)

features_extra = df.groupby("user_login").agg({
    "latitude": "mean",
    "longitude": "mean",
    "id": "count",
    "scientific_name": pd.Series.nunique
}).rename(columns={"id": "num_observations", "scientific_name": "num_species"})

user_features = user_species.join(features_extra, how="left").fillna(0)

# ============================================================
# 3️ UMAP + KMEANS (melhor setup anterior: n_neighbors=50, k=2)
# ============================================================
print("\n Aplicando UMAP + KMeans...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(user_features)

reducer = umap.UMAP(
    n_neighbors=50,
    n_components=2,
    random_state=42,
    min_dist=0.1,
    metric="euclidean"
)
X_umap = reducer.fit_transform(X_scaled)

kmeans = KMeans(n_clusters=2, random_state=42)
labels = kmeans.fit_predict(X_umap)
user_features["cluster"] = labels

# ============================================================
# 4️ RESUMO DOS CLUSTERS
# ============================================================
print("\n Gerando resumo dos clusters...")
summary = user_features.groupby("cluster").agg({
    "num_observations": ["mean", "median"],
    "num_species": ["mean", "median"],
    "latitude": "mean",
    "longitude": "mean",
    "cluster": "count"
}).rename(columns={"cluster": "n_users"})
summary.columns = ["_".join(col).strip() for col in summary.columns.values]
summary.to_csv(f"{PROCESSED_DIR}/cluster_summary.csv")
print(summary)

# ============================================================
# 5️ ESPÉCIES MAIS ASSOCIADAS A CADA CLUSTER
# ============================================================
print("\n Identificando top espécies por cluster...")
species_cols = user_species.columns
top_species = []
for c in sorted(user_features["cluster"].unique()):
    subset = user_features[user_features["cluster"] == c][species_cols]
    mean_freq = subset.mean().sort_values(ascending=False).head(10)
    for sp, val in mean_freq.items():
        top_species.append({"cluster": c, "species": sp, "mean_freq": val})

top_species_df = pd.DataFrame(top_species)
top_species_df.to_csv(f"{PROCESSED_DIR}/top_species_per_cluster.csv", index=False)

# ============================================================
# 6️ PLOTS
# ============================================================
print("\n Gerando gráficos...")

# A. UMAP
plt.figure(figsize=(8, 6))
plt.scatter(X_umap[:, 0], X_umap[:, 1], c=labels, cmap="tab10", s=15)
plt.title("Distribuição UMAP colorida por cluster")
plt.xlabel("UMAP-1")
plt.ylabel("UMAP-2")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/umap_clusters.png", dpi=300)
plt.close()

# B. Boxplots
for metric in ["num_observations", "num_species"]:
    plt.figure(figsize=(6, 5))
    user_features.boxplot(column=metric, by="cluster", grid=False)
    plt.title(f"Distribuição de {metric} por cluster")
    plt.suptitle("")
    plt.xlabel("Cluster")
    plt.ylabel(metric)
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/boxplot_{metric}.png", dpi=300)
    plt.close()

# C. Top espécies (barras)
for c in sorted(top_species_df["cluster"].unique()):
    subset = top_species_df[top_species_df["cluster"] == c]
    plt.figure(figsize=(8, 5))
    plt.barh(subset["species"], subset["mean_freq"])
    plt.gca().invert_yaxis()
    plt.title(f"Top espécies - Cluster {c}")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/top_species_cluster_{c}.png", dpi=300)
    plt.close()

print("\n Análise concluída!")
print(f" Resultados em '{PROCESSED_DIR}' e figuras em '{FIG_DIR}'")

