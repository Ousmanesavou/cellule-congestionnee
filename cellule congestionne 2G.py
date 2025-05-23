# -*- coding: utf-8 -*-
"""
Created on Fri May 23 14:49:15 2025

@author: BXYH8369
"""

import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Analyse de la Congestion SDCCH", layout="wide")

st.title("📊 Analyse de la Congestion SDCCH (2G)")
st.markdown("Charge un fichier Excel, choisis les seuils et télécharge le rapport généré.")

# === 1. Charger le fichier Excel ===
uploaded_file = st.file_uploader("📂 Charger le fichier Excel (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Nettoyage
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['OG_SDCCH_Congestion_Rate(%)'] = df['OG_SDCCH_Congestion_Rate(%)'].replace(['/0', '/', ' ', ''], np.nan)
    df['OG_SDCCH_Congestion_Rate(%)'] = pd.to_numeric(df['OG_SDCCH_Congestion_Rate(%)'], errors='coerce')

    # === 2. Liste déroulante pour paramètres ===
    st.sidebar.header("🔧 Paramètres")
    seuil_kpi = st.sidebar.slider("Seuil de Congestion (%)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    seuil_jours = st.sidebar.slider("Nombre minimum de jours de congestion", min_value=1, max_value=31, value=22)

    # === 3. Traitement ===
    df_congested = df[df['OG_SDCCH_Congestion_Rate(%)'] > seuil_kpi]
    jours_congestion = df_congested.groupby('Cell Name')['Date'].nunique()
    cellules_congestionnees = jours_congestion[jours_congestion >= seuil_jours].index

    df_congested_detailed = df_congested[df_congested['Cell Name'].isin(cellules_congestionnees)]
    df_resultat = df_congested_detailed[['Date', 'Cell Name', 'Site Name', 'OG_SDCCH_Congestion_Rate(%)']]
    df_resultat = df_resultat.sort_values(by=['Cell Name', 'Date'])

    nb_jours_total = df['Date'].nunique()

    # === 4. Affichage Résultats ===
    st.subheader("📈 Résultat : Cellules Congestionnées")
    st.write(f"Nombre total de jours distincts : **{nb_jours_total}**")
    st.dataframe(df_resultat)

    # Fichier Excel
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_resultat.to_excel(writer, index=False, sheet_name='Détails')
        pd.DataFrame({
            'Paramètre': ['Seuil Congestion (%)', 'Seuil Jours', 'Jours Distincts'],
            'Valeur': [seuil_kpi, seuil_jours, nb_jours_total]
        }).to_excel(writer, index=False, sheet_name='Paramètres')
    st.download_button(
        label="📥 Télécharger le fichier généré",
        data=output.getvalue(),
        file_name="rapport_congestion_sdcch.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
