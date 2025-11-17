import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import umap.umap_ as umap

# ============================================================
# CONFIGURAÇÕES
# ============================================================
DATA_FILE = "processed/user_features_normalized.csv"
HDBSCAN_FILE = "processed/user_clusters_hdbscan.csv"

OUTPUT_DIR = "processed"
FIG_DIR = "figs/cleaned_analysis"
os.makedirs(FIG_DIR, exist_ok=True)

# ============================================================
# 1️ CARREGAR DADOS
# ============================================================
print(" Carregando dados e clusters...")
df = pd.read_csv(DATA_FILE)
clusters = pd.read_csv(HDBSCAN_FILE)

if "user_login" not in clusters.columns:
    raise ValueError("❌ Arquivo HDBSCAN precisa conter a coluna 'user_login'.")

# Combinar dados com clusters
merged = df.merge(clusters, on="user_login", how="inner")
print(f" Dados combinados: {merged.shape[0]} linhas")

# ============================================================
# 2️ REMOVER OUTLIERS
# ============================================================
cleaned = merged[merged["cluster"] != -1].copy()
print(f" Usuários após remoção de outliers: {cleaned.shape[0]}")

# ============================================================
# 3️ NORMALIZAR FEATURES NUMÉRICAS
# ============================================================
print("⚖️ Reaplicando normalização nas features...")
exclude_cols = ["user_login", "cluster"]
X = cleaned.drop(columns=exclude_cols)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ============================================================
# 4️ TESTAR DIFERENTES N_NEIGHBORS + K
# ============================================================
neighbors_list = [5, 10, 15, 20, 30, 50, 100]
silhouette_results = []

for n_neighbors in neighbors_list:
    print(f"\n Testando n_neighbors={n_neighbors}...")

    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=2,
        random_state=42,
        min_dist=0.1,
        metric="euclidean"
    )
    X_umap = reducer.fit_transform(X_scaled)

    # Testar vários K
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
    print(f" Melhor K={best_k} | Silhouette={best_score:.3f}")

    # Plot dos clusters
    plt.figure(figsize=(8, 6))
    plt.scatter(X_umap[:, 0], X_umap[:, 1], c=best_labels, cmap="Spectral", s=10)
    plt.title(f"UMAP + KMeans (n_neighbors={n_neighbors}, k={best_k}) - Sem Outliers", fontsize=12)
    plt.xlabel("UMAP-1")
    plt.ylabel("UMAP-2")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/umap_kmeans_cleaned_neighbors_{n_neighbors}.png", dpi=300)
    plt.close()

# ============================================================
# 5️⃣ SALVAR RESULTADOS
# ============================================================
silhouette_df = pd.DataFrame(silhouette_results, columns=["n_neighbors", "best_k", "silhouette_score"])
silhouette_df.to_csv(f"{OUTPUT_DIR}/umap_kmeans_silhouette_cleaned.csv", index=False)

# Gráfico comparativo
original = pd.read_csv(f"{OUTPUT_DIR}/umap_kmeans_silhouette_summary.csv")
plt.figure(figsize=(7, 5))
plt.plot(original["n_neighbors"], original["silhouette_score"], marker="o", label="Com Outliers")
plt.plot(silhouette_df["n_neighbors"], silhouette_df["silhouette_score"], marker="o", label="Sem Outliers")
plt.title("Comparação: Silhouette Score (Antes vs Depois da Limpeza)")
plt.xlabel("n_neighbors (UMAP)")
plt.ylabel("Silhouette Score")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/silhouette_comparison_cleaned.png", dpi=300)
plt.close()

print("\n Análise finalizada!")
print(f" Resultados salvos em: {OUTPUT_DIR}")
print(f" Figuras em: {FIG_DIR}")

