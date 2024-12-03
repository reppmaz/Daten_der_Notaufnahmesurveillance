# imports
import streamlit as st
import pandas as pd
import plotly.express as px

# load data
zeitreihen = pd.read_csv("Notaufnahmesurveillance_Zeitreihen_Syndrome.tsv", sep="\t")
standorte = pd.read_csv("Notaufnahmesurveillance_Standorte.tsv", sep="\t")

# datetime schenanigangs
zeitreihen['date'] = pd.to_datetime(zeitreihen['date'])
min_date = zeitreihen['date'].min().date()
max_date = zeitreihen['date'].max().date()

# renaming col
zeitreihen['age_group'] = zeitreihen['age_group'].replace("00+", "Alle")

# title and description
st.title("Notaufnahmesurveillance Dashboard")
st.markdown("""
Dieses Dashboard zeigt die Ergebnisse der Notaufnahmesurveillance am Robert Koch-Institut (RKI) wie Trends und geografische Verteilungen zu verschiedenen Syndromen in Notaufnahmen Deutschlands.
Die Daten basieren auf dem 
[AKTIN-Notaufnahmeregister](https://public.data.rki.de/t/public/views/Notaufnahmesurveillance/DashboardSyndrome).
- [Original Tableau Dashboard](https://public.data.rki.de/t/public/views/Notaufnahmesurveillance/DashboardSyndrome)
- [GitHub-Repository des RKI](https://github.com/robert-koch-institut/Daten_der_Notaufnahmesurveillance)
""")

# sidebar
st.sidebar.header("Filter")
selected_syndrome = st.sidebar.selectbox("Wähle Syndrom", zeitreihen["syndrome"].unique())
selected_ed_type = st.sidebar.selectbox("Wähle Notaufnahmetyp", zeitreihen["ed_type"].unique())
selected_date_range = st.sidebar.slider(
    "Zeitraum wählen",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="DD.MM.YYYY")

# averaging options
st.sidebar.header("Anzeigeoptionen")
average_option = st.sidebar.selectbox(
    "Wähle Aggregation für Zeitverlauf",
    ["Täglich", "Wöchentlich", "Monatlich"])

# filtering
filtered_data = zeitreihen[
    (zeitreihen["syndrome"] == selected_syndrome) &
    (zeitreihen["ed_type"] == selected_ed_type) &
    (zeitreihen["date"] >= pd.Timestamp(selected_date_range[0])) &
    (zeitreihen["date"] <= pd.Timestamp(selected_date_range[1]))]

# avergages for plotting
if average_option == "Wöchentlich":
    filtered_data = (
        filtered_data
        .groupby([pd.Grouper(key="date", freq="W"), "age_group"])
        .mean(numeric_only=True)  # Aggregate only numeric columns
        .reset_index())
elif average_option == "Monatlich":
    filtered_data = (
        filtered_data
        .groupby([pd.Grouper(key="date", freq="M"), "age_group"])
        .mean(numeric_only=True)  # Aggregate only numeric columns
        .reset_index())

# time series viz
st.header(f"Relative Fallzahlen im Zeitverlauf ({average_option})")
fig = px.line(
    filtered_data,
    x="date",
    y="relative_cases",
    color="age_group",  # Use age_group as the legend
    title="",
    labels={
        "date": "Datum",
        "relative_cases": "Relative Fallzahlen",
        "age_group": "Altersgruppe"})
st.plotly_chart(fig)

# integrate map of emergency rooms
st.header("Geografische Verteilung der teilnehmenden Notaufnahmen")
fig_map = px.scatter_mapbox(
    standorte,
    lat="latitude",
    lon="longitude",
    color_discrete_sequence=["red"],
    size=[7] * len(standorte),
    hover_name="ed_name",
    title="",
    mapbox_style="open-street-map",
    labels={"ed_type": "Notaufnahmetyp"})
st.plotly_chart(fig_map)