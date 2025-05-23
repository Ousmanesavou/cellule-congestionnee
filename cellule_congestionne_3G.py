# -*- coding: utf-8 -*-
"""
Analyse de la Congestion RRC (3G)
Auteur : BXYH8369
Date : Mai 2025
"""

import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO

# === Configuration de la page ===
st.set_page_config(page_title="Analyse de la Congestion RRC (3G)", layout="wide")

st.title("📡 Analyse de la Congestion RRC (3G)")
st.markdown("Charge un fichier Excel, choisis les seuils et télécharge le rapport généré.")

# === 1. Import du fichier Excel ===
uploaded_file = st.file_uploader("📂 Charger le fichier Excel (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Nettoyage
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date  # Format date uniquement
    kpi_col = 'RRC Congestion (%)_CS'
    df[kpi_col] = df[kpi_col].replace(['/0', '/', ' ', ''], np.nan)
    df[kpi_col] = pd.to_numeric(df[kpi_col], errors='coerce')

    # === 2. Liste déroulante paramètres utilisateur ===
    st.sidebar.header("🔧 Paramètres")
    seuil_kpi = st.sidebar.slider("Seuil de Congestion RRC (%)", 0.0, 100.0, 80.0, 0.1)
    seuil_jours = st.sidebar.slider("Nombre minimum de jours de congestion", 1, 31, 10)

    # === 3. Traitement des données ===
    df_congested = df[df[kpi_col] >= seuil_kpi]
    jours_congestion = df_congested.groupby('Cell Name')['Date'].nunique()
    cellules_congestionnees = jours_congestion[jours_congestion >= seuil_jours].index

    df_congested_detailed = df_congested[df_congested['Cell Name'].isin(cellules_congestionnees)]
    df_resultat = df_congested_detailed[['Date', 'Cell Name', 'NodeB Name', kpi_col]]
    df_resultat = df_resultat.sort_values(by=['Cell Name', 'Date'])

    nb_jours_total = df['Date'].nunique()

    # === 4. Affichage résultats ===
    st.subheader("📈 Résultat : Cellules 3G Congestionnées")
    st.write(f"Nombre total de jours distincts dans le fichier : **{nb_jours_total}**")
    st.dataframe(df_resultat)

    # === 5. Génération fichier Excel ===
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_resultat.to_excel(writer, index=False, sheet_name='Détails')
        pd.DataFrame({
            'Paramètre': ['Seuil Congestion (%)', 'Seuil Jours', 'Jours Distincts'],
            'Valeur': [seuil_kpi, seuil_jours, nb_jours_total]
        }).to_excel(writer, index=False, sheet_name='Paramètres')
    
    st.download_button(
        label="📥 Télécharger le rapport de congestion",
        data=output.getvalue(),
        file_name="rapport_congestion_rrc_3g.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
