# ============================================================
#  top_especies_por_cluster.py
# Gera lista de espécies mais observadas por cluster de usuários
# ============================================================

import pandas as pd
from pathlib import Path

# -------------------------------
# 1️ Carregar dados
# -------------------------------
print(" Carregando dados...")

obs_path = Path("data_filtered/observations_sao_paulo.csv")
clusters_path = Path("processed/user_clusters_hdbscan.csv")

obs = pd.read_csv(obs_path)
clusters = pd.read_csv(clusters_path)

print(f" Observações: {len(obs):,}")
print(f" Usuários (clusters): {len(clusters):,}")

# -------------------------------
# 2️ Verificar colunas
# -------------------------------
if "user_login" not in clusters.columns:
    raise ValueError(" Coluna 'user_login' ausente no arquivo de clusters.")

cluster_col = None
for c in ["user_cluster", "cluster"]:
    if c in clusters.columns:
        cluster_col = c
        break

if cluster_col is None:
    raise ValueError(" Nenhuma coluna de cluster ('user_cluster' ou 'cluster') encontrada!")

print(f" Fazendo merge usando: user_login e coluna de cluster '{cluster_col}'")

# -------------------------------
# 3️ Merge observações + clusters
# -------------------------------
merged = obs.merge(clusters[["user_login", cluster_col]], on="user_login", how="inner")

print(f" Merge concluído: {len(merged):,} observações associadas a clusters")

# -------------------------------
# 4️ Filtrar outliers (se existir)
# -------------------------------
if "is_outlier" in clusters.columns:
    merged = merged[~merged[cluster_col].isin(clusters.loc[clusters["is_outlier"], cluster_col])]
    print(f" Após remoção de outliers: {len(merged):,} observações")

# -------------------------------
# 5️ Calcular top espécies por cluster
# -------------------------------
if "common_name" not in merged.columns and "species_guess" in merged.columns:
    merged["common_name"] = merged["species_guess"]

cluster_species = (
    merged.groupby(cluster_col)["common_name"]
    .value_counts()
    .groupby(level=0)
    .head(10)
    .reset_index(name="count")
)

# -------------------------------
# 6️ Gerar resumo final
# -------------------------------
summary_path = Path("processed/top_species_per_cluster.csv")
cluster_species.to_csv(summary_path, index=False)

print(f" Top espécies por cluster salvas em: {summary_path}")
print(cluster_species.head(20))

