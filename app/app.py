# estando dentro da sua pasta, execute o app com streamlit run app.py

import pandas as pd
import streamlit as st
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import folium
from streamlit_folium import st_folium
import pyqrcode
from io import BytesIO
from urllib.parse import quote

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="BirdedexGO", page_icon="🐦", layout="wide")

# --- CARREGAMENTO SEM CACHE ---
def carregar_artefatos():
    """Carrega todos os dados da pasta artifacts local."""
    try:
        base_path = "artifacts/"
        df_obs = pd.read_parquet(base_path + "observations_processed.parquet")
        perfil_cluster = pd.read_parquet(base_path + "perfil_especies_cluster.parquet")
        sazonalidade = pd.read_parquet(base_path + "sazonalidade_especies.parquet")
        mat_cluster_especie = pd.read_csv(base_path + "mat_cluster_especie.csv", index_col=0)
        sim_clusters = pd.read_csv(base_path + "sim_clusters.csv", index_col=0)
        sim_clusters.columns = sim_clusters.columns.astype(int)

        if -1 in mat_cluster_especie.index:
            mat_cluster_especie = mat_cluster_especie.drop(-1)

        return df_obs, perfil_cluster, sazonalidade, mat_cluster_especie, sim_clusters
    except FileNotFoundError:
        return None, None, None, None, None


# --- FUNÇÕES AUXILIARES ---
def estacao_atual():
    mes = datetime.now().month
    if mes in [12, 1, 2]: return 'Verão'
    elif mes in [3, 4, 5]: return 'Outono'
    elif mes in [6, 7, 8]: return 'Inverno'
    else: return 'Primavera'


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2*np.arcsin(np.sqrt(a))
    return R*c


# --- LÓGICA DE RECOMENDAÇÃO ---
def recomendar_aves(usuario_login, df_obs, perfil_cluster, sazonalidade, mat_cluster_especie, sim_clusters, top_n=5, min_recomendacoes=3):

    dados_usuario = df_obs[df_obs['user_login'] == usuario_login]
    vistas = set(dados_usuario['scientific_name'].unique())

    # --- Filtro sazonal ---
    est_atual = estacao_atual()
    sazonalidade['em_alta'] = sazonalidade['estacao'].apply(lambda estacoes: est_atual in estacoes)
    especies_em_alta = set(sazonalidade[sazonalidade['em_alta']]['scientific_name'])

    # --- Novo usuário ---
    if dados_usuario.empty:
        mensagem = "Bem-vindo(a)! Parece que você é um novo Mestre. Aqui estão as aves mais populares de São Paulo:"
        populares = df_obs['scientific_name'].value_counts()
        recomendacoes_finais = [esp for esp in populares.index if esp in especies_em_alta]
        return mensagem, recomendacoes_finais[:top_n]

    # --- Usuário com cluster definido ---
    cluster_usuario = int(dados_usuario['cluster'].iloc[0])

    # --- Caso cluster -1 ---
    if cluster_usuario == -1:
        if not vistas:
            mensagem = "Bem-vindo(a)! Aqui estão as aves mais populares de São Paulo:"
            populares = df_obs['scientific_name'].value_counts()
            recomendacoes_finais = [esp for esp in populares.index if esp in especies_em_alta]
            return mensagem, recomendacoes_finais[:top_n]

        # Usuário com poucas observações, faz recomendação baseada em similaridade
        mensagem = "Seu perfil é único! Buscamos aves de clusters semelhantes ao seu."
        todas_especies_cols = mat_cluster_especie.columns

        perfil_usuario_df = pd.DataFrame(
            [[1 if esp in vistas else 0 for esp in todas_especies_cols]],
            columns=todas_especies_cols
        )

        sim_usuario_clusters = cosine_similarity(perfil_usuario_df.values, mat_cluster_especie.values)
        scores = pd.Series(sim_usuario_clusters[0], index=mat_cluster_especie.index)

        top_clusters_similares = scores.sort_values(ascending=False).head(3)

        especie_scores = {}
        for cluster, score_cluster in top_clusters_similares.items():
            lista = perfil_cluster[perfil_cluster['cluster'] == cluster]['especies_mais_comuns']
            if not lista.empty:
                for esp in lista.iloc[0]:
                    especie_scores[esp] = especie_scores.get(esp, 0) + score_cluster

        especie_scores = {
            esp: sc for esp, sc in especie_scores.items()
            if esp not in vistas and esp in especies_em_alta
        }

        recomendadas = sorted(especie_scores.items(), key=lambda x: x[1], reverse=True)
        recomendacoes_finais = [esp for esp, _ in recomendadas]

        return mensagem, recomendacoes_finais[:top_n]

    # --- Caso cluster válido ---
    mensagem = f"Radar (Cluster {cluster_usuario}): Detectamos estas aves para o seu perfil!"
    lista_cluster = perfil_cluster[perfil_cluster['cluster'] == cluster_usuario]['especies_mais_comuns']
    especies_cluster = [] if lista_cluster.empty else lista_cluster.iloc[0]

    sugestoes = [esp for esp in especies_cluster if esp not in vistas and esp in especies_em_alta]

    recomendacoes_finais = list(sugestoes)

    # --- Fallback ---
    if len(recomendacoes_finais) < min_recomendacoes:
        similares = sim_clusters.loc[cluster_usuario].sort_values(ascending=False)
        similares = similares[similares.index != cluster_usuario]
        top_vizinhos = similares.head(3).index.tolist()

        especie_scores_fallback = {}

        for cluster_v in top_vizinhos:
            score_cluster = float(sim_clusters.loc[cluster_usuario, cluster_v])
            lista_v = perfil_cluster[perfil_cluster['cluster'] == cluster_v]['especies_mais_comuns']

            if not lista_v.empty:
                for esp in lista_v.iloc[0]:
                    especie_scores_fallback[esp] = especie_scores_fallback.get(esp, 0) + score_cluster

        sugestoes_fallback = sorted(especie_scores_fallback.items(), key=lambda x: x[1], reverse=True)

        for esp, _ in sugestoes_fallback:
            if len(recomendacoes_finais) >= top_n:
                break
            if esp not in recomendacoes_finais and esp not in vistas and esp in especies_em_alta:
                recomendacoes_finais.append(esp)

    return mensagem, recomendacoes_finais[:top_n]


# ============================================================
# ------------------- INTERFACE STREAMLIT ---------------------
# ============================================================

st.title("🐦 BirdedexGO")
st.markdown("Seja o maior Mestre Observador! Complete sua Birdedex e encontre novas espécies de Aves.")

df_obs, perfil_cluster, sazonalidade, mat_cluster_especie, sim_clusters = carregar_artefatos()

if df_obs is None:
    st.error("❌ ERRO: Artefatos não encontrados na pasta 'artifacts/'.")
    st.stop()

if 'selected_map' not in st.session_state:
    st.session_state.selected_map = None

login_selecionado = st.text_input("Digite seu `user_login` do iNaturalist para começar:", placeholder="Ex: a42147")

if login_selecionado:
    user_data = df_obs[df_obs['user_login'] == login_selecionado]
    
    st.header(f"Análise para Mestre {login_selecionado}!", divider='rainbow')

    # ===========================
    #      BIRDEDÉX DO USUÁRIO
    # ===========================
    if user_data.empty:
        st.info("Novo Mestre! Nenhuma observação encontrada.")
    else:
        user_lat, user_lon = user_data['latitude'].mean(), user_data['longitude'].mean()

        st.subheader("📖 Sua Birdedex")
        aves_capturadas = user_data.drop_duplicates(subset='scientific_name').sort_values('common_name')
        st.success(f"Você já registrou **{len(aves_capturadas)}** espécies únicas!")

        with st.expander("Ver todas as espécies registradas"):
            cols = st.columns(5)
            for i, row in aves_capturadas.iterrows():
                with cols[i % 5]:
                    st.image(row['image_url'], use_container_width=True)
                    st.markdown(f"**{row['common_name']}**")

    # ===========================
    #       RECOMENDAÇÕES
    # ===========================
    st.header("📡 Aves no seu Radar", divider='rainbow')
    with st.spinner("Escaneando a área..."):
        mensagem, recomendacoes_nomes = recomendar_aves(
            login_selecionado, df_obs, perfil_cluster, sazonalidade, mat_cluster_especie, sim_clusters
        )

    st.info(mensagem)

    if recomendacoes_nomes:
        recomendacoes_df = df_obs[df_obs['scientific_name'].isin(recomendacoes_nomes)].drop_duplicates(subset='scientific_name')

        if not recomendacoes_df.empty:
            recomendacoes_df = recomendacoes_df.set_index('scientific_name').loc[recomendacoes_nomes].reset_index()

            for i, row in recomendacoes_df.iterrows():
                species_id = row['scientific_name']

                col1, col2 = st.columns([1, 3])

                # ----------- Coluna 1 (Imagem + Nome + Botão) -----------
                with col1:
                    st.image(row['image_url'], use_container_width=True)
                    st.markdown(f"#### {row['common_name']}")
                    st.caption(f"_{species_id}_")

                    button_label = "🗺️ Fechar Mapa" if st.session_state.selected_map == species_id else "🗺️ Onde encontrar?"
                    if st.button(button_label, key=f"map_btn_{species_id}"):
                        st.session_state.selected_map = None if st.session_state.selected_map == species_id else species_id
                        st.rerun()

                # ----------- Coluna 2 (Mapa) -----------
                with col2:
                    if st.session_state.selected_map == species_id:

                        if not user_data.empty:
                            user_lat_map, user_lon_map = user_lat, user_lon
                        else:
                            user_lat_map, user_lon_map = -23.5505, -46.6333

                        locais_proximos = df_obs[df_obs['scientific_name'] == species_id].copy()
                        locais_proximos['distance'] = haversine(
                            user_lat_map, user_lon_map,
                            locais_proximos['latitude'],
                            locais_proximos['longitude']
                        )
                        locais_proximos = locais_proximos[locais_proximos['distance'] <= 50]

                        if locais_proximos.empty:
                            st.warning("Nenhum avistamento recente a menos de 50 km.")
                        else:
                            mapa = folium.Map(location=[user_lat_map, user_lon_map], zoom_start=10)
                            folium.Marker(
                                [user_lat_map, user_lon_map],
                                popup="Sua posição média",
                                icon=folium.Icon(color='blue', icon='user', prefix='fa')
                            ).add_to(mapa)

                            for _, ponto in locais_proximos.iterrows():
                                folium.Marker([ponto['latitude'], ponto['longitude']]).add_to(mapa)

                            st_folium(mapa, width=700, height=400)

                            st.subheader("📲 Leve o mapa com você!")
                            termo_busca = quote(f"avistamentos de {row['common_name']} perto de mim")
                            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={termo_busca}"

                            qr_code = pyqrcode.create(google_maps_url)
                            buffer = BytesIO()
                            qr_code.png(buffer, scale=5)
                            st.image(buffer.getvalue())


    else:
        st.success("Radar limpo por enquanto!")
