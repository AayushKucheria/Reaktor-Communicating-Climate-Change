import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import folium


# Setting page config
st.set_page_config(page_title="World Map", page_icon="🌍", layout="wide")

# CONSTANTS
# years for the slider
start_year = 1950
end_year = 2019


# Cached function for downloading and prepairing the data to plot.
@st.cache(hash_funcs={tuple: lambda x: 1})   # This hashing function is just so that the program doesn't stop. I don't know how it should be.
def load_data(start_year, end_year):
  url = 'http://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv'
  df = pd.read_csv(url)

  country_geo = 'world-countries.json'


  df_map = df[["year", "country", "co2", "co2_per_capita", "co2_growth_prct", "methane"]]
  # df_map = df_map[df_map.year == 2019]


  # Change country names so that folium understands them
  proper_name = {
    "United States": "United States of America", "Czechia": "Czech Republic", "Serbia": "Republic of Serbia",
    "North Macedonia": "Macedonia", "Congo": "Republic of the Congo", "Democratic Republic of Congo": "Democratic Republic of the Congo",
    "Tanzania": "United Republic of Tanzania", "Cote d'Ivoire": "Ivory Coast", "Guinea-Bissau": "Guinea Bissau", "Eswatini": "Swaziland",
    "Bahamas": "The Bahamas",
    "Timor": "East Timor" # Timor is an island, East Timor is a country 
    }

  for i in range(len(df_map)):
    name = df_map.iloc[i].country
    if name in proper_name:
      df_map.at[i, "country"] = proper_name[name]

  # For the countries below we might have to do something more fancy. Folium recognises them, but OWID not
  # I guess Somaliland is considered as Somalia
  # Northern Cyprus is considered as cyprus
  # Western Sahara is probably under Morocco
  # Falkland Islands. I guess they belong to UK?
  # French Southern and Antarctic Lands probably should be considered as France

  # Remove some non-countries from the data
  not_countries = ["Africa", "Asia (excl. China & India)", "Asia", "EU-27", "EU-28", "Europe", "Europe (excl. EU-27)", "Europe (excl. EU-28)", "International transport",
                  "North America (excl. USA)", "North America", "Oceania", "South America", "World"] # Antarctica is also not a country, but is shown on the map

  df_map = df_map[~df_map.country.isin(not_countries)]


  co2_per_capita_choropleth = {}
  co2_choropleth = {}
  co2_growth_choropleth = {}

  # Creating all the choropleth maps for all the years
  # total CO2 emissions and growth percentage are not shown by default, CO2 per capita is
  for i in range(start_year, end_year+1):
    print(i)
    df_map_year = df_map[df_map.year == i]
    co2_per_capita_choropleth[i] = folium.Choropleth(geo_data=country_geo, data=df_map_year,
              columns=['country', 'co2_per_capita'],
              key_on='feature.properties.name',
              fill_color='Reds', fill_opacity=0.7, line_opacity=0.2,
              legend_name='CO2 emissions per capita'
              )
    co2_per_capita_choropleth[i].geojson.add_child(folium.features.GeoJsonTooltip(fields=['name'], labels=True))
    co2_per_capita_choropleth[i].layer_name = 'CO2 emissions per capita'

    co2_bins = list(df_map_year["co2"].quantile([0, 0.2, 0.3, 0.5, 0.6, 0.8, 0.97, 1]))
    co2_choropleth[i] = folium.Choropleth(geo_data=country_geo, data=df_map_year,
              columns=['country', 'co2'],
              key_on='feature.properties.name',
              fill_color='RdPu', fill_opacity=0.7, line_opacity=0.2,
              legend_name='CO2 emissions',
              bins = co2_bins
              )
    co2_choropleth[i].geojson.add_child(folium.features.GeoJsonTooltip(fields=['name'], labels=True))
    co2_choropleth[i].layer_name = 'total CO2 emissions'

    co2_growth_choropleth[i] = folium.Choropleth(geo_data=country_geo, data=df_map_year,
              columns=['country', 'co2_growth_prct'],
              key_on='feature.properties.name',
              fill_color='PuBu', fill_opacity=0.7, line_opacity=0.2,
              legend_name='CO2 Growth Percentage'
              )
    co2_growth_choropleth[i].geojson.add_child(folium.features.GeoJsonTooltip(fields=['name'], labels=True))
    co2_growth_choropleth[i].layer_name = 'CO2 growth percentage'

  return((co2_per_capita_choropleth, co2_choropleth, co2_growth_choropleth))


co2_per_capita_choropleth, co2_choropleth, co2_growth_choropleth = load_data(start_year, end_year)


# Setup a folium map at a high-level zoom
map = folium.Map(zoom_start=1, tiles='cartodbpositron')
# slider for selecting the year
year_slider = st.slider("Year", start_year, end_year, end_year)
# radio buttons for selecting what to show
layer_radio = st.radio("Quantity", ('CO2 per capita', 'total CO2 emissions', 'CO2 growth percentage'))
if layer_radio == 'CO2 per capita':
  co2_per_capita_choropleth[year_slider].add_to(map)
elif layer_radio == 'total CO2 emissions':
  co2_choropleth[year_slider].add_to(map)
else:
  co2_growth_choropleth[year_slider].add_to(map)

folium.LayerControl().add_to(map)

folium_static(map)