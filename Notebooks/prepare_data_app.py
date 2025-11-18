import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import shutil # Usaremos para limpar a pasta de artefatos antigos

print("--- Iniciando a preparação de dados para o App Birdédex GO ---")

# --- 1. CARREGAMENTO DOS DADOS LOCAIS ---
print("1. Carregando dados de entrada locais...")
path_clusters = os.path.join('processed', 'user_clusters_kmeans_final.csv')
path_obs = os.path.join('data_filtered', 'observations_sao_paulo.csv')
try:
    df_clusters_raw = pd.read_csv(path_clusters)
    df_obs_raw = pd.read_csv(path_obs)
    print("   ... Dados carregados com sucesso.")
except FileNotFoundError as e:
    print(f"   ERRO: Arquivo não encontrado: {e}.")
    print("   Certifique-se de que este script está na pasta 'Notebooks' e que os arquivos de dados existem nas subpastas corretas.")
    exit()

# --- 2. JUNÇÃO, LIMPEZA E FORMATAÇÃO DOS DADOS ---
print("2. Juntando clusters com observações, limpando e formatando...")
df_merged = df_obs_raw.merge(df_clusters_raw[['user_login', 'cluster']], on='user_login', how='left')
df_merged['cluster'].fillna(-1, inplace=True)
df_merged['cluster'] = df_merged['cluster'].astype(int)
df_merged['observed_on'] = pd.to_datetime(df_merged['observed_on'], errors='coerce')
df_merged.dropna(subset=['observed_on', 'user_login', 'scientific_name', 'common_name', 'image_url'], inplace=True)
df_merged['common_name'] = df_merged['common_name'].str.split(';').str[0].str.strip()
df_merged['month'] = df_merged['observed_on'].dt.month
print("   ... Junção e limpeza concluídas.")

# --- 3. CÁLCULO DO PERFIL DOS CLUSTERS ---
print("3. Calculando o perfil de espécies de cada cluster...")
total_registros_cluster = df_merged.groupby('cluster').size().reset_index(name='total_registros')
species_counts = df_merged.groupby(['cluster', 'scientific_name']).size().reset_index(name='n_registros')
species_counts = species_counts.merge(total_registros_cluster, on='cluster', how='left')
species_counts['freq_relativa'] = species_counts['n_registros'] / species_counts['total_registros'] # Coluna é 'freq_relativa'
top_species_per_cluster = species_counts.sort_values(['cluster', 'freq_relativa'], ascending=[True, False]).groupby('cluster').head(15)
perfil_especies_cluster = top_species_per_cluster.groupby('cluster')['scientific_name'].apply(list).reset_index(name='especies_mais_comuns')
print("   ... Perfis de cluster definidos.")

# --- 4. CÁLCULO DA SAZONALIDADE ---
print("4. Calculando a sazonalidade das espécies...")
def estacao(mes):
    if mes in [12, 1, 2]: return 'Verão'
    elif mes in [3, 4, 5]: return 'Outono'
    elif mes in [6, 7, 8]: return 'Inverno'
    else: return 'Primavera'
df_merged['estacao'] = df_merged['month'].apply(estacao)
sazonalidade = df_merged.groupby(['scientific_name', 'estacao']).size().reset_index(name='n_observacoes')
total_por_especie = sazonalidade.groupby('scientific_name')['n_observacoes'].sum().reset_index(name='total_especie')
sazonalidade = sazonalidade.merge(total_por_especie, on='scientific_name')
sazonalidade['freq_relativa'] = sazonalidade['n_observacoes'] / sazonalidade['total_especie']
max_freq = sazonalidade.groupby('scientific_name')['freq_relativa'].max().reset_index().rename(columns={'freq_relativa': 'freq_relativa_max'})
sazonalidade_merge = sazonalidade.merge(max_freq, on='scientific_name')
sazonalidade_merge['diff_relativa'] = sazonalidade_merge['freq_relativa_max'] - sazonalidade_merge['freq_relativa']
dominantes = sazonalidade_merge[sazonalidade_merge['diff_relativa'] <= 0.10]
estacao_dominante = dominantes.groupby('scientific_name')['estacao'].apply(list).reset_index()
print("   ... Sazonalidade calculada.")

# --- 5. CÁLCULO DAS MATRIZES DE SIMILARIDADE ---
print("5. Calculando matrizes de similaridade para o sistema de fallback...")

# <<-- CORREÇÃO APLICADA AQUI -->>
# O valor da coluna 'values' foi corrigido de 'freq_rel' para 'freq_relativa'
mat_cluster_especie = species_counts.pivot_table(index='cluster', columns='scientific_name', values='freq_relativa', fill_value=0)

sim_clusters = pd.DataFrame(cosine_similarity(mat_cluster_especie), index=mat_cluster_especie.index, columns=mat_cluster_especie.index)
print("   ... Matrizes de similaridade criadas.")

# --- 6. SALVAR OS ARTEFATOS FINAIS ---
print("6. Limpando artefatos antigos e salvando os novos...")
output_dir = os.path.join('..', 'app', 'artifacts')
# Limpa a pasta de artefatos antes de salvar, para garantir que não haja arquivos antigos
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

df_merged.to_parquet(os.path.join(output_dir, 'observations_processed.parquet'))
perfil_especies_cluster.to_parquet(os.path.join(output_dir, 'perfil_especies_cluster.parquet'))
estacao_dominante.to_parquet(os.path.join(output_dir, 'sazonalidade_especies.parquet'))
mat_cluster_especie.to_csv(os.path.join(output_dir, 'mat_cluster_especie.csv'))
sim_clusters.to_csv(os.path.join(output_dir, 'sim_clusters.csv'))

print("\n--- Preparação concluída com sucesso! ---")
print(f"Os artefatos foram salvos em: {os.path.abspath(output_dir)}")