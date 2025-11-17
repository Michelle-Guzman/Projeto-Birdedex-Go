# Projeto Birdedex Go
Projeto de sistema de recomendação de visualização de aves a partir de dados do iNaturalist, com base em múltiplas camadas de informação (ecológica, geográfica e sazonal).

# Projeto: Análise de Clusters de Usuários e Perfil Ecológico em São Paulo

Este projeto analisa observações de aves na cidade de São Paulo, agrupa usuários em clusters com base em padrões de observação, gera mapas interativos e perfis ecológicos para cada cluster, e fornece ferramentas para análise ecológica e visualização espacial.

---

## Estrutura do Repositório

```
/data_filtered
    observations_sao_paulo.csv       # Observações de aves com coordenadas
    /processed
    /scripts
    /figs
    cleaned_analysis/
 
```

---

## Passo a Passo: Criação do Ambiente Conda

No terminal (Anaconda Prompt ou Terminal do Mac/Linux):

```bash
# Cria um ambiente novo chamado birdrec
conda create -n birdrec python=3.10 -y

# Ativa o ambiente
conda activate birdrec
```

---

## Instalação de Pacotes Essenciais

### Manipulação de dados, Machine Learning, clusterização, redes, visualização

```bash
conda install -c conda-forge pandas numpy scikit-learn matplotlib seaborn tqdm jupyterlab -y
```

### Redução de dimensionalidade e clusterização avançada

```bash
conda install -c conda-forge umap-learn hdbscan -y
```

### Redes e comunidades

```bash
conda install -c conda-forge networkx python-igraph leidenalg -y
```

### Dados geográficos e visualização espacial

```bash
conda install -c conda-forge geopandas folium pyproj shapely -y
```

### Aprendizado profundo (opcional, para recomendação)

```bash
pip install tensorflow==2.12  # versão estável CPU
```

ou via Conda

```bash
conda install -c conda-forge tensorflow
```

### Embeddings / Node2Vec (opcional)

```bash
pip install torch torchvision
```

---

## Verificação das Versões

```bash
python -m pip list | grep -E "pandas|numpy|scikit|umap|hdbscan|networkx|tensorflow|torch"
```

---

## Uso do Projeto

1. Coloque os arquivos CSV em `/data_filtered` e `/processed`.
2. Execute o script principal:

```bash
python scripts/generate_maps_and_profiles.py
```

3. O script gera:

   * Mapas interativos em HTML:

     * `processed/cluster_centroids_gradient_map.html`
     * `processed/cluster_ecoprofile_map.html`
   * CSV com top espécies por cluster:

     * `processed/cluster_top_species.csv`
   * CSV resumo por perfil ecológico:

     * `processed/cluster_ecoprofile_summary.csv`

---

## Descrição dos Mapas

* `cluster_centroids_gradient_map.html`: centroids de cada cluster com gradiente de cor e tamanho indicativos do número de usuários.
* `cluster_ecoprofile_map.html`: centroids coloridos por perfil ecológico (urbano, mata, aquático, campos).

---

## Perfis Ecológicos dos Clusters

| Ecotipo                      | Clusters        | Características                                      |
| ---------------------------- | --------------- | ---------------------------------------------------- |
| Urbano duro / sinantrópicos  | 0, 7            | Aves domesticadas e exóticas em áreas urbanas densas |
| Urbano arborizado / quintais | 4, 9, 10        | Bairros com árvores e parques menores                |
| Ambientes aquáticos          | 1, 3, 7         | Lagos, represas, canais                              |
| Mata / fragmentos florestais | 2, 5, 6, 11, 13 | Parques grandes e fragmentos florestais              |
| Campos abertos               | 6, 12           | Gramados e bordas de áreas abertas                   |

---

## Possíveis Análises

* Comparação de espécies entre clusters
* Mapas temáticos interativos por perfil ecológico
* Gráficos de diversidade e abundância de espécies
* Perfis ecológicos para publicações e relatórios

---

Autores: Aleksej Kozlakowski Junior, Gabriele ???, Michelle Fernandez ??, Tiago Belintani, Victor ???, 
Data: 2025
