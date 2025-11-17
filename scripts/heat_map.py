import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("processed/cluster_summary.csv")

plt.figure(figsize=(8, 8))
plt.scatter(df["longitude_mean"], df["latitude_mean"],
            s=df["n_users_count"]*0.5,  # tamanho relativo ao número de usuários
            c=df["cluster"], cmap="tab10", alpha=0.7)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Centros médios dos clusters (usuários em São Paulo)")
plt.grid(True)
plt.savefig("figs/cluster_centroids_map.png", dpi=300)
plt.show()

