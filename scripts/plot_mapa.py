import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# Carregar observações com clusters validados
obs = pd.read_csv("processed/cluster_validated_summary.csv")

# Remover outliers, se houver
obs = obs[obs['n_obs'] > 0]

# Criar GeoDataFrame
gdf = gpd.GeoDataFrame(
    obs,
    geometry=gpd.points_from_xy(obs['mean_lon'], obs['mean_lat']),
    crs="EPSG:4326"
)

# Transformar para Web Mercator para usar basemap
gdf = gdf.to_crs(epsg=3857)

# Plotar
fig, ax = plt.subplots(figsize=(12, 12))
gdf.plot(
    ax=ax,
    column='n_obs',           # cor baseada no número de observações
    cmap='viridis',
    markersize=50,
    legend=True,
    legend_kwds={'label': "Número de observações por cluster"}
)

# Adicionar mapa base
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

ax.set_axis_off()
plt.title("Distribuição espacial dos clusters de observações em SP", fontsize=15)
plt.tight_layout()

# Salvar arquivo
plt.savefig("processed/map_clusters_final.png", dpi=300)
plt.close()
print(" Mapa salvo em: processed/map_clusters_final.png")

