from pandas.core.frame import DataFrame
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import folium
import plotly.express as px
import time
from sklearn.linear_model import LinearRegression
from folium.plugins import Fullscreen
import statsmodels.api as smapi
import statsmodels as sm
import plotly.graph_objs as go


@st.cache()
def get_OWID_data():
  #url = 'http://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv'
  #df = pd.read_csv(url)
  df = pd.read_csv("owid-co2-data_25_11_2021.csv")
  return(df)

@st.cache()
def max_year():
  df = get_OWID_data()
  max_y = df.year.max()
  return(max_y)


# Cached function for downloading/prepping data
@st.cache(hash_funcs={tuple: lambda x: 1})   # This hashing function is just so that the program doesn't stop. I don't know how it should be.
def load_data(start_year, end_year):
	df = get_OWID_data()

	country_geo = 'world-countries.json'

	df_map = df[["year", "country", "co2", "co2_per_capita", "co2_growth_prct", "methane", "gdp", "population"]]
	df_map["gdp_per_capita"] = df_map["gdp"] / df_map["population"]
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
	return (country_geo, df_map)