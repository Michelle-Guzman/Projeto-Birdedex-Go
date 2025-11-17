import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import umap.umap_ as umap

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================
DATA_FILE = "data_filtered/observations_sao_paulo.csv"
OUTPUT_DIR = "processed"
FIG_DIR = "figs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# ============================================================
# 1️ CARREGAR DADOS
# ============================================================
print(" Carregando dados...")
df = pd.read_csv(DATA_FILE)
df = df[df["iconic_taxon_name"] == "Aves"]

# Remover registros com dados essenciais ausentes
df = df.dropna(subset=["user_login", "scientific_name", "latitude", "longitude"])

print(f" Total de observações: {len(df):,}")
print(f" Usuários únicos: {df['user_login'].nunique():,}")
print(f" Espécies únicas: {df['scientific_name'].nunique():,}")

# ============================================================
# 2️ GERAR MATRIZ USUÁRIO × ESPÉCIE
# ============================================================
print("\n Criando matriz usuário × espécie...")
user_species = (
    df.groupby(["user_login", "scientific_name"])
      .size()
      .unstack(fill_value=0)
)

print(f" Matriz criada: {user_species.shape[0]} usuários × {user_species.shape[1]} espécies")

# ============================================================
# 3️ FEATURES ADICIONAIS POR USUÁRIO
# ============================================================
print("\n➕ Adicionando features adicionais...")
features_extra = df.groupby("user_login").agg({
    "latitude": "mean",
    "longitude": "mean",
    "id": "count"  # número de observações
}).rename(columns={"id": "num_observations"})

# Combinar com matriz principal
user_features = user_species.join(features_extra, how="left").fillna(0)
print(f" Dimensões após junção: {user_features.shape}")

# ============================================================
# 4️ NORMALIZAÇÃO
# ============================================================
print("\n⚖️ Normalizando dados...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(user_features)

# ============================================================
# 5️ TESTAR DIFERENTES N_NEIGHBORS
# ============================================================
neighbors_list = [5, 10, 15, 20, 30, 50, 100]
silhouette_results = []

for n_neighbors in neighbors_list:
    print(f"\n UMAP + KMeans para n_neighbors = {n_neighbors}...")

    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=2,
        random_state=42,
        min_dist=0.1,
        metric="euclidean"
    )

    X_umap = reducer.fit_transform(X_scaled)

    # Testar vários K via silhouette
    best_score = -1
    best_k = None
    best_labels = None

    for k in range(2, 15):
        km = KMeans(n_clusters=k, random_state=42)
        labels = km.fit_predict(X_umap)
        score = silhouette_score(X_umap, labels)

        if score > best_score:
            best_score = score
            best_k = k
            best_labels = labels

    silhouette_results.append((n_neighbors, best_k, best_score))
    print(f" Melhor K={best_k} com silhouette={best_score:.3f}")

    # Plot UMAP
    plt.figure(figsize=(8, 6))
    plt.scatter(X_umap[:, 0], X_umap[:, 1], c=best_labels, cmap="Spectral", s=10)
    plt.title(f"UMAP + KMeans (n_neighbors={n_neighbors}, k={best_k})", fontsize=12)
    plt.xlabel("UMAP-1")
    plt.ylabel("UMAP-2")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/umap_kmeans_neighbors_{n_neighbors}.png", dpi=300)
    plt.close()

# ============================================================
# 6️ SALVAR RESULTADOS
# ============================================================
print("\n Salvando dados e métricas...")
np.save(f"{OUTPUT_DIR}/user_umap_ready.npy", X_umap)
user_features.to_csv(f"{OUTPUT_DIR}/user_features_normalized.csv")

silhouette_df = pd.DataFrame(silhouette_results, columns=["n_neighbors", "best_k", "silhouette_score"])
silhouette_df.to_csv(f"{OUTPUT_DIR}/umap_kmeans_silhouette_summary.csv", index=False)

# Gráfico de resumo
plt.figure(figsize=(7, 5))
plt.plot(silhouette_df["n_neighbors"], silhouette_df["silhouette_score"], marker="o")
plt.title("Variação do Silhouette Score por n_neighbors")
plt.xlabel("n_neighbors (UMAP)")
plt.ylabel("Silhouette Score")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/silhouette_neighbors.png", dpi=300)
plt.close()

print("\n Pipeline completo! Resultados salvos em:")
print(f"   • Dados processados → {OUTPUT_DIR}")
print(f"   • Figuras → {FIG_DIR}")

