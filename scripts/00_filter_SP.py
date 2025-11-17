#!/usr/bin/env python3
# ============================================================
# 01_filter_sao_paulo.py
# Filtra observações do iNaturalist para apenas a cidade de São Paulo
# ============================================================

import os
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Caminhos
# ------------------------------------------------------------
base_dir = "/home/tiagobelintani/Projeto_disciplina/teste_sp"
data_raw = os.path.join(base_dir, "observations-634104.csv")

data_dir = os.path.join(base_dir, "data_filtered")
figs_dir = os.path.join(base_dir, "figs")

os.makedirs(data_dir, exist_ok=True)
os.makedirs(figs_dir, exist_ok=True)

# ------------------------------------------------------------
# Carregar dados
# ------------------------------------------------------------
print(" Carregando dados...")
df = pd.read_csv(data_raw)
print(f" Dados carregados: {df.shape[0]} observações, {df.shape[1]} colunas")

# ------------------------------------------------------------
# Filtrar apenas linhas com coordenadas válidas
# ------------------------------------------------------------
df = df.dropna(subset=["latitude", "longitude"])
print(f"Após remover coordenadas nulas: {df.shape[0]} observações")

# ------------------------------------------------------------
# Filtro geográfico para a cidade de São Paulo
# Aproximadamente entre:
#   Latitude: -24.00 a -23.30
#   Longitude: -46.80 a -46.30
# ------------------------------------------------------------
mask_sp = (
    (df["latitude"] <= -23.30) & (df["latitude"] >= -24.00) &
    (df["longitude"] <= -46.30) & (df["longitude"] >= -46.80)
)

df_sp = df[mask_sp].copy()
print(f" Observações dentro da cidade de São Paulo: {df_sp.shape[0]}")

# ------------------------------------------------------------
# Estatísticas rápidas
# ------------------------------------------------------------
n_users = df_sp["user_id"].nunique() if "user_id" in df_sp.columns else "?"
n_species = df_sp["scientific_name"].nunique() if "scientific_name" in df_sp.columns else "?"
print(f" Usuários únicos: {n_users}")
print(f" Espécies únicas: {n_species}")

# ------------------------------------------------------------
# Plotar mapa de pontos
# ------------------------------------------------------------
plt.figure(figsize=(6, 6))
plt.scatter(df["longitude"], df["latitude"], s=1, alpha=0.1, color="gray", label="Todas as observações")
plt.scatter(df_sp["longitude"], df_sp["latitude"], s=3, color="red", label="São Paulo (filtro aplicado)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(markerscale=3)
plt.title("Distribuição das observações - São Paulo")
plt.tight_layout()

fig_path = os.path.join(figs_dir, "sao_paulo_filter_map.png")
plt.savefig(fig_path, dpi=300)
plt.close()
print(f" Figura salva: {fig_path}")

# ------------------------------------------------------------
# Salvar dataset filtrado
# ------------------------------------------------------------
out_path = os.path.join(data_dir, "observations_sao_paulo.csv")
df_sp.to_csv(out_path, index=False)
print(f" Dados filtrados salvos: {out_path}")

print("\n Filtro concluído com sucesso!")

