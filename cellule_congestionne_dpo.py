# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Analyse de la Congestion Réseau", layout="wide")
st.title("📡 Analyse de la Congestion Réseau (2G / 3G / 4G)")
st.markdown("Charge un fichier Excel, sélectionne la technologie, ajuste les seuils, et télécharge le rapport généré.")

techno = st.selectbox("Sélectionner la technologie :", ["2G", "3G", "4G"])
uploaded_file = st.file_uploader("📂 Charger le fichier Excel (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    st.sidebar.header("🔧 Paramètres")

    # Initialiser les variables
    kpi_col = ""
    nom_site_col = ""

    try:
        if techno == "2G":
            st.subheader("📊 Analyse de la TCH Congestion Rate (2G)")
            kpi_col = 'TCH Congestion Rate(%)'
            nom_site_col = 'Site Name'
            seuil_kpi = st.sidebar.slider("Seuil de TCH Congestion Rate(%)", 0.0, 100.0, 1.0, 0.1)
            seuil_jours = st.sidebar.slider("Nombre minimum de jours de congestion", 1, 31, 22)

        elif techno == "3G":
            st.subheader("📡 Analyse de la Congestion RRC (3G)")
            kpi_col = 'RRC Congestion (%)_CS'
            nom_site_col = 'NodeB Name'
            seuil_kpi = st.sidebar.slider("Seuil de Congestion RRC (%)", 0.0, 100.0, 80.0, 0.1)
            seuil_jours = st.sidebar.slider("Nombre minimum de jours de congestion", 1, 31, 22)

        elif techno == "4G":
            st.subheader("📶 Analyse de la Congestion PRB (4G)")
            kpi_col = 'OG_DL_PRB_Utilization(%)'
            nom_site_col = 'eNodeB Name'
            seuil_kpi = st.sidebar.slider("Seuil d'utilisation PRB DL (%)", 0.0, 100.0, 80.0, 0.5)
            seuil_jours = st.sidebar.slider("Nombre minimum de jours de congestion", 1, 31, 22)

            if 'NodeB Name' in df.columns:
                df = df.rename(columns={'NodeB Name': 'eNodeB Name'})

        # Vérification des colonnes nécessaires
        colonnes_requises = ['Cell Name', 'Date', kpi_col, nom_site_col]
        colonnes_absentes = [col for col in colonnes_requises if col not in df.columns]

        if colonnes_absentes:
            st.error(f"❌ Le fichier ne contient pas les colonnes nécessaires pour l’analyse {techno} : {', '.join(colonnes_absentes)}")
        else:
            # Nettoyage et conversion
            df[kpi_col] = df[kpi_col].replace(['/0', '/', ' ', ''], np.nan)
            df[kpi_col] = pd.to_numeric(df[kpi_col], errors='coerce')

            df_congested = df[df[kpi_col] > seuil_kpi]
            jours_congestion = df_congested.groupby('Cell Name')['Date'].nunique()
            cellules_congestionnees = jours_congestion[jours_congestion >= seuil_jours].index
            df_resultat = df_congested[df_congested['Cell Name'].isin(cellules_congestionnees)]

            nb_jours_total = df['Date'].nunique()

            df_resultat = df_resultat[['Date', 'Cell Name', nom_site_col, kpi_col]].sort_values(by=['Cell Name', 'Date'])

            st.subheader(f"📈 Résultat : Cellules {techno} Congestionnées")
            st.write(f"Nombre total de jours distincts : **{nb_jours_total}**")
            st.dataframe(df_resultat)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_resultat.to_excel(writer, index=False, sheet_name='Détails')
                pd.DataFrame({
                    'Paramètre': ['Seuil Congestion (%)', 'Seuil Jours', 'Jours Distincts'],
                    'Valeur': [seuil_kpi, seuil_jours, nb_jours_total]
                }).to_excel(writer, index=False, sheet_name='Paramètres')

            st.download_button(
                label="📥 Télécharger le rapport",
                data=output.getvalue(),
                file_name=f"rapport_congestion_{techno.lower()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Une erreur est survenue : {str(e)}")
