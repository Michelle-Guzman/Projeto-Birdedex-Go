# ============================================================
#  Análise Ecológica e Espacial dos Clusters de Observadores
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ========================
# 1️ Carregar os arquivos
# ========================

print("🔹 Carregando dados...")

# Diretórios
data_obs = "data_filtered/observations_sao_paulo.csv"
data_users = "processed/user_features_normalized.csv"
data_clusters = "processed/cluster_summary.csv"

# Carregar observações
obs = pd.read_csv(data_obs)
users = pd.read_csv(data_users)
clusters = pd.read_csv(data_clusters)

print(f" Observações: {len(obs)} registros")
print(f" Usuários: {len(users)} registros")
print(f" Clusters: {len(clusters)} registros")

# ==================================================
# 2️ Verificar colunas e normalizar nomes (consistência)
# ==================================================
for df in [obs, users, clusters]:
    df.columns = df.columns.str.lower().str.strip()

# Verificar colunas essenciais
if "user_login" not in obs.columns:
    raise ValueError("❌ Coluna 'user_login' ausente em observations_sao_paulo.csv")

if "cluster" not in users.columns and "cluster" not in clusters.columns:
    raise ValueError("❌ Nenhuma tabela contém coluna 'cluster'.")

# Priorizar cluster no arquivo de usuários
if "cluster" in users.columns:
    cluster_df = users[["user_login", "cluster"]]
else:
    raise ValueError("⚠️ Não encontrei 'cluster' associado aos usuários.")

# Merge observações + cluster
merged = obs.merge(cluster_df, on="user_login", how="inner")

print(f" Dados combinados: {len(merged)} observações com cluster atribuído")

# ==================================================
# 3️ Estatísticas por cluster
# ==================================================

print("\n Calculando estatísticas ecológicas por cluster...")

# Número de observações e espécies por cluster
cluster_stats = (
    merged.groupby("cluster")
    .agg(
        n_observations=("id", "count"),
        n_species=("scientific_name", "nunique"),
        n_users=("user_login", "nunique"),
        lat_mean=("latitude", "mean"),
        lon_mean=("longitude", "mean"),
        lat_std=("latitude", "std"),
        lon_std=("longitude", "std"),
    )
    .reset_index()
)

print(cluster_stats)

# ==================================================
# 4️ Espécies dominantes por cluster
# ==================================================

print("\n🦜 Identificando espécies dominantes...")

species_cluster = (
    merged.groupby(["cluster", "scientific_name"])
    .size()
    .reset_index(name="count")
)

# Calcular proporção dentro do cluster
species_cluster["prop_cluster"] = species_cluster.groupby("cluster")["count"].apply(
    lambda x: x / x.sum()
)

# Top 10 espécies por cluster
top_species = species_cluster.groupby("cluster").apply(
    lambda x: x.sort_values("prop_cluster", ascending=False).head(10)
).reset_index(drop=True)

os.makedirs("processed", exist_ok=True)
top_species.to_csv("processed/cluster_species_summary.csv", index=False)
print(" Arquivo salvo: processed/cluster_species_summary.csv")

# ==================================================
# 5️⃣ Visualização: Heatmap de espécies por cluster
# ==================================================

print("\n🎨 Gerando heatmap de espécies...")

# Pivotar tabela: clusters x espécies (top 15 mais comuns no total)
top15_species = (
    species_cluster.groupby("scientific_name")["count"].sum().nlargest(15).index
)
heatmap_data = species_cluster[species_cluster["scientific_name"].isin(top15_species)]
heatmap_pivot = heatmap_data.pivot_table(
    values="prop_cluster", index="scientific_name", columns="cluster", fill_value=0
)

plt.figure(figsize=(8, 6))
sns.heatmap(heatmap_pivot, cmap="viridis", annot=True, fmt=".2f")
plt.title("🔥 Proporção das principais espécies por cluster")
plt.xlabel("Cluster")
plt.ylabel("Espécie (cientific_name)")
os.makedirs("figs/cluster_analysis", exist_ok=True)
plt.tight_layout()
plt.savefig("figs/cluster_analysis/species_cluster_heatmap.png", dpi=300)
plt.close()

print(" Heatmap salvo em figs/cluster_analysis/species_cluster_heatmap.png")

# ==================================================
# 6️ Mapa de dispersão dos clusters (lat/lon)
# ==================================================

print("\n🗺️ Gerando mapa de dispersão...")

plt.figure(figsize=(8, 8))
sns.scatterplot(
    data=merged,
    x="longitude",
    y="latitude",
    hue="cluster",
    palette="tab10",
    alpha=0.5,
)
plt.title("🌎 Distribuição geográfica dos clusters de observadores")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(title="Cluster")
plt.tight_layout()
plt.savefig("figs/cluster_analysis/spatial_clusters_map.png", dpi=300)
plt.close()

print(" Mapa salvo em figs/cluster_analysis/spatial_clusters_map.png")

# ==================================================
# 7️ Conclusão
# ==================================================

print("\n🎯 Análise concluída com sucesso!")
print("👉 Arquivos gerados:")
print(" - processed/cluster_species_summary.csv")
print(" - figs/cluster_analysis/species_cluster_heatmap.png")
print(" - figs/cluster_analysis/spatial_clusters_map.png")

