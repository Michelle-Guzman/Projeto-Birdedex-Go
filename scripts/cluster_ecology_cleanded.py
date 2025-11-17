import pandas as pd
from pathlib import Path

print(" Carregando dados...")

# ======================
# 1️ Carregar datasets
# ======================
obs = pd.read_csv("data_filtered/observations_sao_paulo.csv")
users = pd.read_csv("processed/user_clusters_hdbscan.csv")

print(f" Observações: {len(obs)} registros")
print(f" Usuários: {len(users)} registros")

# =====================
# 2️ Identificar colunas de coordenadas
# ======================
lat_col = "latitude" if "latitude" in obs.columns else "private_latitude"
lon_col = "longitude" if "longitude" in obs.columns else "private_longitude"
print(f"📍 Usando colunas: {lat_col} e {lon_col}")

# ======================
# 3️ Remover outliers
# ======================
users = users[users["cluster"] != -1]
print(f"🧹 Clusters válidos: {users['cluster'].nunique()}")

# ======================
# 4️ Garantir chave de merge
# ======================
if "user_login" not in users.columns:
    alt_user_col = [c for c in users.columns if "user" in c.lower()][0]
    users = users.rename(columns={alt_user_col: "user_login"})

# Evita sobrescrever colunas do dataset de observações
user_cols = [c for c in users.columns if c not in ["user_login"]]
users_renamed = users.rename(columns={c: f"user_{c}" for c in user_cols})

# ======================
# 5️ Merge seguro
# ======================
merged = obs.merge(users_renamed, on="user_login", how="inner")
print(f" Merge concluído: {len(merged)} observações associadas a clusters")

# Verificação de colunas após o merge
print("🔍 Colunas após merge:", [c for c in merged.columns if "lat" in c or "lon" in c][:6])

# ======================
# 6️ Converter coordenadas
# ======================
merged[lat_col] = pd.to_numeric(merged[lat_col], errors="coerce")
merged[lon_col] = pd.to_numeric(merged[lon_col], errors="coerce")

# ======================
# 7️ Estatísticas por cluster
# ======================
print("📊 Calculando estatísticas por cluster...")

def top_species(series, n=10):
    return ", ".join(series.value_counts().head(n).index)

cluster_summary = (
    merged.groupby("user_cluster")
    .agg(
        n_users=("user_login", "nunique"),
        n_obs=("id", "count"),
        top_species=("scientific_name", lambda x: top_species(x)),
        mean_lat=(lat_col, "mean"),
        mean_lon=(lon_col, "mean"),
    )
    .reset_index()
)

# ======================
# 8️ Salvar
# ======================
out_path = Path("processed/cluster_ecology_summary.csv")
cluster_summary.to_csv(out_path, index=False)

print(f"✅ Resumo ecológico salvo em: {out_path}")
print(cluster_summary.head())

