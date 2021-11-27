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
from plotly.subplots import make_subplots

from util import get_OWID_data

# Heatmap
@st.cache(hash_funcs={tuple: lambda x: 1})
def heatmap(country_geo, df_map, start_year, end_year):

  co2_per_capita_choropleth = {}
  co2_choropleth = {}
  co2_growth_choropleth = {}

  # Creating all the choropleth maps for all the years
  # total CO2 emissions and growth percentage are not shown by default, CO2 per capita is
  for i in range(start_year, end_year+1):
    df_map_year = df_map[df_map.year == i]
    co2_pc_bins = list(df_map_year["co2_per_capita"].quantile([0, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 0.97, 1]))
    co2_per_capita_choropleth[i] = folium.Choropleth(geo_data=country_geo, data=df_map_year,
              columns=['country', 'co2_per_capita'],
              key_on='feature.properties.name',
              fill_color='Reds', fill_opacity=0.7, line_opacity=0.2,
              legend_name='CO2 emissions per capita in tonnes (t)',
              nan_fill_color="white",
              bins = co2_pc_bins
              )
    co2_per_capita_choropleth[i].geojson.add_child(folium.features.GeoJsonTooltip(fields=['name'], labels=True))
    co2_per_capita_choropleth[i].layer_name = 'CO2 emissions per capita'

    co2_bins = list(df_map_year["co2"].quantile([0, 0.2, 0.3, 0.5, 0.6, 0.8, 0.97, 1]))
    co2_choropleth[i] = folium.Choropleth(geo_data=country_geo, data=df_map_year,
              columns=['country', 'co2'],
              key_on='feature.properties.name',
              fill_color='RdPu', fill_opacity=0.7, line_opacity=0.2,
              legend_name='CO2 emissions in million tonnes (Mt)',
              nan_fill_color="white",
              bins = co2_bins
              )
    co2_choropleth[i].geojson.add_child(folium.features.GeoJsonTooltip(fields=['name'], labels=True))
    co2_choropleth[i].layer_name = 'total CO2 emissions'

    co2_growth_choropleth[i] = folium.Choropleth(geo_data=country_geo, data=df_map_year,
              columns=['country', 'co2_growth_prct'],
              key_on='feature.properties.name',
              fill_color='PuBu', fill_opacity=0.7, line_opacity=0.2,
              legend_name='CO2 Growth Percentage',
              nan_fill_color="white"
              )
    co2_growth_choropleth[i].geojson.add_child(folium.features.GeoJsonTooltip(fields=['name'], labels=True))
    co2_growth_choropleth[i].layer_name = 'CO2 growth percentage'

  return((co2_per_capita_choropleth, co2_choropleth, co2_growth_choropleth))

### CHANGES PLOT
# This caching does not seem to be changing much
@st.cache()
def changes_plot(df, year, rangeX):
  df = df[df.year == year].copy()
  if rangeX is not None:
    df["co2_growth_prct"] = df.co2_growth_prct.clip(rangeX[0] + 1, rangeX[1] - 1)    
  
  fig = px.scatter(
    df, 
    x = "co2_growth_prct", 
    y = "co2", color = "gdp_per_capita",  
    hover_name = "country", 
    log_y = True,
    range_x=rangeX,
    hover_data = {"co2_growth_prct":False, "co2":False, "gdp_per_capita": False},
    labels = {"co2": "CO2 output (t)", "co2_growth_prct": "CO2 percentage change", "gdp_per_capita": "GDP per capita"},
    title = "Annual CO2 output and percentage change in " + str(year), 
    width = 900,
    height=600
  )

  fig.add_vline(x = 0, line_color = "lime") #line_dash = "dash"
  return(fig)


# FUTURE CO@ EMISSIONS PREDICTION
@st.cache()
def model_future_CO2_emissions(country, predict_time, train_from):
  df = get_OWID_data()
  fi = df[df.country == country]
  fi = fi[["country", "year", "co2", "population", "energy_per_capita"]]
  fi = fi[df.year > train_from]
  available_data_year = fi[~ fi.isnull().any(axis = 1)].year.max()
  years_cut_off = fi.year.max() - available_data_year
  shift_by = predict_time + years_cut_off
  fi["co2_now"] = fi["co2"].shift(-shift_by) # All other variables are from the past
  fi = fi[df.year < available_data_year]
  predict_from = available_data_year + 1

  training = fi[fi.year < predict_from - shift_by].copy()
  test = fi[fi.year >= predict_from - shift_by].copy()

  y_train = training.co2_now
  X_train = training[["year", "population", "energy_per_capita"]]
  X_test = test[["year", "population", "energy_per_capita"]]

  model = smapi.OLS(y_train,X_train)
  results = model.fit()

  # https://tedboy.github.io/statsmodels_doc/generated/statsmodels.sandbox.regression.predstd.wls_prediction_std.html
  a, lower_confidence ,upper_confidence = sm.sandbox.regression.predstd.wls_prediction_std(results, X_test)
  result = pd.DataFrame({"year": test.year + shift_by, "prediction": results.predict(X_test), "lci": lower_confidence, "uci": upper_confidence})
  return(result)


# FUTURE METHANE EMISSIONS PREDICTION
@st.cache()
def model_future_methane_emissions(country, predict_time, train_from):
  df = get_OWID_data()
  fi = df[df.country == country]
  fi = fi[["country", "year", "co2", "population", "methane"]]
  fi = fi[df.year > train_from]
  available_data_year = fi[~ fi.isnull().any(axis = 1)].year.max()
  if(pd.isnull(available_data_year)):
    return(pd.DataFrame({"year":[], "methane prediction": [], "muci": [], "mlci":[]}))
  years_cut_off = fi.year.max() - available_data_year
  shift_by = predict_time + years_cut_off
  fi["methane_now"] = fi["methane"].shift(-shift_by) # All other variables are from the past
  fi = fi[df.year < available_data_year]
  predict_from = available_data_year + 1

  training = fi[fi.year < predict_from - shift_by].copy()
  test = fi[fi.year >= predict_from - shift_by].copy()

  y_train = training.methane_now
  X_train = training[["year", "methane", "population"]]
  X_test = test[["year", "methane", "population"]]

  model = smapi.OLS(y_train,X_train)
  results = model.fit()

  a, lower_confidence ,upper_confidence = sm.sandbox.regression.predstd.wls_prediction_std(results, X_test)
  result = pd.DataFrame({"year": test.year + shift_by, "methane prediction": results.predict(X_test), "mlci": lower_confidence, "muci": upper_confidence})
  return(result)

  ### EMISSIONS HISTORY PLOT
@st.cache()
def emissions_history_plot(country, from_year):
  co2_prediction = model_future_CO2_emissions(country, 5, 1980)
  methane_prediction = model_future_methane_emissions(country, 5, 2000)
  df = get_OWID_data()
  dfw = df[df["country"] == country]
  df3 = dfw[dfw.year >= from_year].copy()
  df3 = pd.merge(df3, co2_prediction, how = "outer", on=["year"])
  df3 = pd.merge(df3, methane_prediction, how = "outer", on=["year"])
  df3.rename({"co2": "CO2", "prediction": "CO2 prediction"}, axis = 1, inplace = True)

  fig = px.line(
    df3, 
    x = "year", 
    y = ["CO2", "CO2 prediction", "methane", "methane prediction"],
    labels = {"value": "million tonnes (Mt) of CO2 equivalent", "variable": "Greenhouse gas"},
    title = "CO2 and methane emissions history for " + str(country),
    width = 900,
    height = 500
  )
  fig.add_hline(y = 0, line_color = "black", line_dash = "dash")
  fig.add_annotation( # add a text callout with arrow
    text="Paris agreement", x=2016, y=1.05 * int(df3[df3.year == 2016].CO2), arrowhead=1, showarrow=True
  )
  fig.add_annotation( # add a text callout with arrow
    text="Kyoto protocol", x=2005, y=1.05 * int(df3[df3.year == 2005].CO2), arrowhead=1, showarrow=True
  )
  fig.add_annotation( # add a text callout with arrow
    text="WW1", x=1914, y=1.3 * int(df3[df3.year == 1914].CO2), arrowhead=1, showarrow=True
  )
  fig.add_annotation( # add a text callout with arrow
    text="WW2", x=1939, y=1.3 * int(df3[df3.year == 1939].CO2), arrowhead=1,  showarrow=True
  )
  fig.add_annotation( # add a text callout with arrow
    text="Early 1980's recession", x=1980, y=1.05 * int(df3[df3.year == 1980].CO2), arrowhead=1,  showarrow=True, ay = -50
  )
  fig.add_annotation( # add a text callout with arrow
    text="The Great Depession", x=1930, y=1.3 * int(df3[df3.year == 1930].CO2), arrowhead=1,  showarrow=True, ay = -100
  )
  fig.add_annotation( # add a text callout with arrow
    text="COVID pandemic", x=2019, y=0.99 * int(df3[df3.year == 2019].CO2), arrowhead=1,  showarrow=True, ay = 70
  )

  # Confidence intervals
  fig.add_trace(go.Scatter(x=df3.year, y = df3.uci,
    fill=None,
    mode='lines',
    line_color="rgba(255, 0, 0, 0)",
    name = ""
  ))
  fig.add_trace(go.Scatter(
    x=df3.year, y = df3.lci,
    fill='tonexty', # fill area between trace0 and trace1
    mode='lines', line_color="rgba(255, 0, 0, 0)", fillcolor="rgba(255, 0, 0, 0.2)",
    name = "95% confidence inteval for CO2"
  ))
  fig.add_trace(go.Scatter(x=df3.year, y = df3.muci,
    fill=None,
    mode='lines',
    line_color="rgba(0, 255, 0, 0)",
    name = ""
  ))
  fig.add_trace(go.Scatter(
    x=df3.year, y = df3.mlci,
    fill='tonexty', # fill area between trace0 and trace1
    mode='lines', line_color="rgba(0, 255, 0, 0)", fillcolor = "rgba(0, 255, 0, 0.2)",
    name = "95% confidence inteval for methane"
  ))

  return(fig)

### Sector breakdown pie chart
@st.cache()
def sector_breakdown():
  xls = pd.ExcelFile('./res/Global-GHG-Emissions-by-sector-based-on-WRI-2020.xlsx')
  df_all = pd.read_excel(xls, 'All')
  df_all = df_all.rename(columns={'Sub-sector (further breakdown)': 'Sub-sub-sector'})


  energy = df_all[df_all["Sector"] == "Energy"]
  industrial = df_all[df_all["Sector"] == "Industrial processes"]
  waste = df_all[df_all["Sector"] == "Waste"]
  AFOLU = df_all[df_all["Sector"] == "Agriculture, Forestry & Land Use (AFOLU)"]

  # Create subplots: use 'domain' type for Pie subplot
  fig = make_subplots(rows=1, cols=4, specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}]], subplot_titles=['Energy',"Agriculture, Forestry & Land", 'Industrial processes', "Waste" ])

  fig.add_trace(go.Pie(labels=energy["Sub-sector"], values=energy["Share of global greenhouse gas emissions (%)"], scalegroup='one', name="Emissions from Energy"),
                1, 1)
  fig.add_trace(go.Pie(labels=AFOLU["Sub-sub-sector"], values=AFOLU["Share of global greenhouse gas emissions (%)"], scalegroup='one', name="Emissions from AFOLU"),
                1, 2)
  fig.add_trace(go.Pie(labels=industrial["Sub-sub-sector"], values=industrial["Share of global greenhouse gas emissions (%)"],scalegroup='one', name="Emissions from Industrial processes"),
                1, 3)
  fig.add_trace(go.Pie(labels=waste["Sub-sub-sector"], values=waste["Share of global greenhouse gas emissions (%)"], scalegroup='one', name="Emissions from Waste"),
                1, 4)

  fig.update_traces(hoverinfo='label+percent', textinfo='none')
  fig.update_layout(
      title_text="Global Emissions by Sectors",
      showlegend=False,
      width=900, height=500)
      
  return fig
#### WORLD TEMPERATURE
@st.cache()
def world_temperature():
  df_temp = pd.read_csv("globalTemperature.csv", header=1)
  df_temp["30 year average"] = df_temp.rolling(window=30)["Temperature"].mean()
  # preindustrialTemp = (df_temp[df_temp.Year <= 1900][['Temperature']].mean())[0]
  preindustrialTemp = df_temp.loc[df_temp.Year == 2017, '30 year average'].values[0] - 1
  df_temp["1 degree increase"] = preindustrialTemp + 1
  df_temp["1.5 degree increase"] = preindustrialTemp + 1.5
  fig = px.line(
      df_temp,
      x = "Year",
      y = ["Temperature", "30 year average", "1 degree increase", "1.5 degree increase"],
      title = "Global mean temperature history",
      range_y = (-0.8, 1.8),
      width = 900,
      height = 500
  )
  # fig.add_hline(y = preindustrialTemp + 1, line_color = "orange")
  # fig.add_hline(y = preindustrialTemp + 1.5, line_color = "red")
  return(fig)