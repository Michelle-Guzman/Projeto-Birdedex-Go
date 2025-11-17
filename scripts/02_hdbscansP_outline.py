import os
import pandas as pd
import numpy as np
import umap.umap_ as umap
import hdbscan
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# ============================================================
# CONFIGURAÇÕES
# ============================================================
INPUT_FILE = "processed/user_features_normalized.csv"
OUTPUT_DIR = "processed"
FIG_DIR = "figs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

print(" Carregando dados normalizados...")
user_features = pd.read_csv(INPUT_FILE, index_col=0)

# Mantém apenas colunas numéricas
X = user_features.select_dtypes(include=[np.number])

# ============================================================
# 1️ NORMALIZAÇÃO E REDUÇÃO DE DIMENSIONALIDADE (UMAP)
# ============================================================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(" Reduzindo dimensionalidade com UMAP...")
reducer = umap.UMAP(n_neighbors=15, n_components=2, random_state=42, min_dist=0.1)
X_umap = reducer.fit_transform(X_scaled)

# ============================================================
# 2️ CLUSTERIZAÇÃO COM HDBSCAN
# ============================================================
print(" Aplicando HDBSCAN para detectar clusters e outliers...")
clusterer = hdbscan.HDBSCAN(min_cluster_size=15, min_samples=10, metric='euclidean')
labels = clusterer.fit_predict(X_umap)

user_features["cluster"] = labels
user_features["is_outlier"] = (labels == -1)

# ============================================================
# 3️ SALVAR RESULTADOS
# ============================================================
output_path = os.path.join(OUTPUT_DIR, "user_clusters_hdbscan.csv")
user_features.to_csv(output_path)
print(f" Clusters e outliers salvos em: {output_path}")

# ============================================================
# 4️ PLOTS
# ============================================================
plt.figure(figsize=(8, 6))
plt.scatter(X_umap[:, 0], X_umap[:, 1], c=labels, cmap="Spectral", s=10)
plt.title("Clusters HDBSCAN (UMAP 2D)", fontsize=12)
plt.xlabel("UMAP-1")
plt.ylabel("UMAP-2")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/hdbscan_umap_clusters.png", dpi=300)
plt.close()

# Plot de outliers
plt.figure(figsize=(8, 6))
plt.scatter(X_umap[:, 0], X_umap[:, 1], c=user_features["is_outlier"], cmap="coolwarm", s=10)
plt.title("Detecção de Outliers (HDBSCAN)", fontsize=12)
plt.xlabel("UMAP-1")
plt.ylabel("UMAP-2")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/hdbscan_outliers.png", dpi=300)
plt.close()

# ============================================================
# 5️ RESUMO DE RESULTADOS
# ============================================================
n_outliers = user_features["is_outlier"].sum()
n_total = len(user_features)
perc = n_outliers / n_total * 100

print(f"\n Total de usuários analisados: {n_total}")
print(f" Outliers detectados: {n_outliers} ({perc:.2f}%)")
print(f" Clusters formados (excluindo -1): {len(set(labels)) - (1 if -1 in labels else 0)}")

