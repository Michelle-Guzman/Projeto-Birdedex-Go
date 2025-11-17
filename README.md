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

## Possíveis Análises

* Comparação de espécies entre clusters
* Mapas temáticos interativos por perfil ecológico
* Gráficos de diversidade e abundância de espécies
* Perfis ecológicos para publicações e relatórios

---

Autores: Aleksej Kozlakowski Junior, Gabriele da Silva Campos, Gabriele da Silva Campos, Tiago Belintani, Victor Matsuno,  
Data: 2025



