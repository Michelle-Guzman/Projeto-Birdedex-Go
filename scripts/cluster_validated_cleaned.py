#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cluster_validated.py
Integra estatísticas ecológicas e espécies dominantes por cluster.
"""

import pandas as pd

print(" Carregando arquivos de entrada...")

# Caminhos
eco_path = "processed/cluster_ecology_summary.csv"
species_path = "processed/top_species_per_cluster.csv"
output_path = "processed/cluster_validated_summary.csv"

# === 1️ Carregar dados
ecology = pd.read_csv(eco_path)
species = pd.read_csv(species_path)

print(f" Clusters ecológicos: {ecology.shape[0]} linhas")
print(f" Top espécies: {species['cluster'].nunique()} clusters")

# === 2️ Preparar top espécies (agrupar as top N espécies por cluster)
top_n = 10  # você pode mudar aqui
top_species_summary = (
    species.groupby("cluster")
    .apply(lambda g: ", ".join(g.sort_values("count", ascending=False)
                               .head(top_n)["common_name"]))
    .reset_index(name="top_species")
)

# === 3️ Unir com dados ecológicos
validated = ecology.merge(top_species_summary, how="left", left_on="user_cluster", right_on="cluster")

# === 4️ Limpeza final
validated = validated.drop(columns=["cluster"], errors="ignore")

# Reordenar colunas
cols = ["user_cluster", "n_users", "n_obs", "mean_lat", "mean_lon", "top_species"]
validated = validated[[c for c in cols if c in validated.columns]]

# === 5️ Salvar resultado
validated.to_csv(output_path, index=False)
print(f" Resumo validado salvo em: {output_path}")

# Mostrar prévia
print("\n Prévia dos clusters validados:")
print(validated.head(10).to_string(index=False))

