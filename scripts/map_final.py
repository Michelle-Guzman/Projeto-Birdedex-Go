import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# Use clusters validados
observations_file = "processed/cluster_validated_summary.csv"  # ou cluster_validated_summary.csv

obs = pd.read_csv(observations_file)

# Verifique nomes das colunas de latitude/longitude
print(obs.columns)

# Converter para numérico
obs['mean_lat'] = pd.to_numeric(obs['mean_lat'], errors='coerce')
obs['mean_lon'] = pd.to_numeric(obs['mean_lon'], errors='coerce')

# Criar GeoDataFrame
gdf = gpd.GeoDataFrame(
    obs,
    geometry=gpd.points_from_xy(obs['mean_lon'], obs['mean_lat']),
    crs="EPSG:4326"
)

gdf = gdf.to_crs(epsg=3857)  # para basemap

# Plot
fig, ax = plt.subplots(figsize=(12, 12))
gdf.plot(ax=ax, column='user_cluster', cmap='tab20', markersize=50, alpha=0.7, legend=True)

ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

ax.set_title("Clusters de Observações de Aves em São Paulo")
ax.set_axis_off()

plt.savefig("processed/map_clusters_sao_paulo_2.png", dpi=300, bbox_inches='tight')
plt.show()

