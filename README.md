# Projeto BirdedexGO
Projeto de sistema de recomendação de visualização de aves a partir de dados do iNaturalist, com base em múltiplas camadas de informação (ecológica, geográfica e sazonal). Ao final, as análises apresentadas são integradas a um aplicativo disponível para os usuários.

# Projeto: Análise de Clusters de Usuários e Perfil Ecológico em São Paulo

Este projeto analisa observações de aves na cidade de São Paulo, agrupa usuários em clusters com base em padrões de observação, gera mapas interativos e perfis ecológicos para cada cluster, e fornece ferramentas para análise ecológica e visualização espacial.

---

## Estrutura do Repositório

```
📂 Projeto-Birdedex-Go/
├── 📂 Notebooks/
│   ├── 📄 projeto_disciplina.ipynb # Descrição das análises realizadas
│   ├── 📂 data_filtered/
│   │   └── 📄 observations_sao_paulo.csv       # Observações de aves com coordenadas
│   ├── 📂 processed/
│   │   └── 📄 user_clusters_kmeans_final.csv   # Arquivo final da clusterização de usuários│
├── 📂 app/
│   ├── 📄 app.py                                  # Script do aplicativo
│   └── 📂 artifacts/                              
│
└── 📄 README.md 
    
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

## Executando o Aplicativo BirdedexGO

Existem duas maneiras de interagir com o nosso projeto: acessando o site público ou rodando o aplicativo localmente no seu computador.

### Opção 1: Acessar o Site
A forma mais fácil e rápida de usar o BirdedexGO é através do link do nosso site público, hospedado no Streamlit Community Cloud.

➡️ **Acesse o aplicativo aqui:** [https://seu-link-para-o-app.streamlit.app/](https://seu-link-para-o-app.streamlit.app/) *

---

### Opção 2: Rodar Localmente no seu computador
Se você deseja executar o código na sua própria máquina para explorar ou modificar, siga os passos abaixo.

#### Pré-requisitos
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads/)

#### Passo 1: Clone o Repositório
Abra seu terminal e execute o comando abaixo para baixar todos os arquivos do projeto:
```bash
git clone https://github.com/Michelle-Guzman/Projeto-Birdedex-Go.git
cd Projeto-Birdedex-Go
```
#### Passo 2: Instale as Dependências
Navegue até a pasta Notebooks e instale todas as bibliotecas necessárias para a análise e para o aplicativo com um único comando:

```bash
cd Notebooks
pip install -r requirements_app.txt
```

#### Passo 3: Prepare os Dados (Executar uma única vez)
Este passo crucial processa os dados brutos e gera os arquivos otimizados (artefatos) que o aplicativo usará. Certifique-se de que você ainda está na pasta Notebooks antes de executar o comando.

```bash
python prepare_data_app.py
```

Aguarde a conclusão. Ao final, você verá uma mensagem de sucesso indicando que os artefatos foram salvos na pasta app/artifacts/.
Passo 4: Rode o Aplicativo
Agora que os dados estão prontos, navegue até a pasta do aplicativo e inicie o servidor.

```bash
# Se você está na pasta 'Notebooks', volte para a raiz do projeto e entre em 'app'
# cd ../app
streamlit run app.py
```

Seu navegador abrirá automaticamente o aplicativo BirdedexGO!
---

Autores: Aleksej Kozlakowski Junior, Gabriele da Silva Campos, Michelle Guzman de Fernandes, Tiago Belintani, Victor Matsuno.  
Data: 2025



