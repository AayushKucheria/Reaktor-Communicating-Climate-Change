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



# Function definitions

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
  

@st.cache(hash_funcs={tuple: lambda x: 1})
def heatmap(country_geo, df_map):

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

@st.cache()
def model_future_CO2_emissions(country, predict_time, train_from):
  df = get_OWID_data()
  fi = df[df.country == country]
  fi = fi[["country", "year", "co2", "co2_growth_prct", "population", "energy_per_capita"]]
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
  X_train = training[["year", "co2", "co2_growth_prct", "population", "energy_per_capita"]]
  X_test = test[["year", "co2", "co2_growth_prct", "population", "energy_per_capita"]]

  model = smapi.OLS(y_train,X_train)
  results = model.fit()

  # https://tedboy.github.io/statsmodels_doc/generated/statsmodels.sandbox.regression.predstd.wls_prediction_std.html
  a, lower_confidence ,upper_confidence = sm.sandbox.regression.predstd.wls_prediction_std(results, X_test)
  result = pd.DataFrame({"year": test.year + shift_by, "prediction": results.predict(X_test), "lci": lower_confidence, "uci": upper_confidence})
  return(result)

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
  X_train = training[["year", "co2", "methane", "population"]]
  X_test = test[["year", "co2", "methane", "population"]]

  model = smapi.OLS(y_train,X_train)
  results = model.fit()

  a, lower_confidence ,upper_confidence = sm.sandbox.regression.predstd.wls_prediction_std(results, X_test)
  result = pd.DataFrame({"year": test.year + shift_by, "methane prediction": results.predict(X_test), "mlci": lower_confidence, "muci": upper_confidence})
  return(result)


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
  )
  # fig.add_hline(y = preindustrialTemp + 1, line_color = "orange")
  # fig.add_hline(y = preindustrialTemp + 1.5, line_color = "red")
  return(fig)





#######################################
#     PAGE STRUCTURE AND CONTENT      #
#######################################


# Setting page config
st.set_page_config(page_title="Climate Change: A Nordic Perspective", page_icon="🌍", layout="wide")

# Create a header aligning the text to the center in streamlit
# Create a sidebar with 3 pages
st.sidebar.header("Menu")
page = st.sidebar.radio("Pages", ("Home", "About"))


# Write some text
if page == "Home":
  st.header("The Climate Crisis. Tick Tock.")
  st.write("""
Climate change, mainly due to carbon dioxide (CO2) and methane emissions, is one of the largest challenges that humanity is currently facing. 
As population and consumption will continue to increase in the future, so will emissions. Meaning the challenge is far from over and will 
likely get worse before getting better. 

If not addressed and limited, climate change will cause widespread social, economic and ecosystem damage. 
As greenhouse gas emissions are distributed globally and over a wide range of societal activities, it needs to be addressed from a 
global point of view. 

The political goal of limiting global warming caused by emissions to 1,5 degrees has risen. It has been assessed that this would require a 
general global carbon neutrality by 2050 and negative emission soon after that. 
 
While that goal is still far from achieved there is an increasing momentum of decreasing emissions. Europe as an example has been able to 
cut its total emissions almost yearly since the 1990s. In addition, several countries both within and outside of Europe have pledged 
carbon neutrality with varying target years. 
 
In the Glasgow climate conference in November of 2021 a new global agreement, the Glasgow Climate Pact, was reached. In the agreement the 
countries pledged to cut the emission of CO2 to limit temperature rise to 1.5 degrees. On a better note, for the first time, there was an 
explicit plan to reduce the use of coal by phasing it down. The pact pledged to increase financial aid to developing countries to help them 
cope with both the effects of climate change and the switch to clean energy. 
  """)

  st.markdown("""
  - [The temperature is rising](http://localhost:8501/#the-temperature-is-rising)
  - [Here's why it matters](http://localhost:8501/#heres-why-it-matters)
  - [Emissions worldwide have been growing](http://localhost:8501/#emissions-worldwide-have-been-growing)
  - [But, which sectors actually contribute to this?](http://localhost:8501/#but-which-sectors-actually-contribute-to-this)
  - [What can we do about this?](http://localhost:8501/#what-can-we-do-about-this)
  """)

  st.subheader("The temperature is rising")
  # Figure of worldwide mean temperature over time
  st.plotly_chart(world_temperature())
  st.write("""
  Human-induced global warming reached about 1°C (likely between 0.8 and 1.2°C) above pre-industrial levels in 2017, with a 0.2°C increase per decade. 
  Most land regions are warming up faster than the global average - depending on the considered temperature dataset, 20-40% of the world population 
  live in regions that had already experienced warming of more than 1.5°C in at least one season by the decade 2006-2015. 

  Global warming is defined in the IPCC (Intergovernmental Panel on Climate Change) report as an increase in combined surface air and 
  sea surface temperatures averaged over the globe and a 30-year period, usually relative to the period 1850-1900. By that measure, warming 
  from pre-industrial levels to the decade 2006-2015 is assessed to be approximately 0.87°C.  
  
  The red line in the figure above shows the global temperature over the previous 30 years while the straight lines represent a 1 °C and 1.5 °C 
  increase from pre-industrial levels. Note that the figure is merely an approximation for the sake of visualization: in practice, there is no 
  exact pre-industrial temperature to work with - even the methods of calculating it differ greatly - and therefore also no exact temperature we 
  could label as 1.5 °C increase.
  """)

  st.subheader("Here's why it matters")
  # Add template_image.png to the page
  st.write("""
  Currently, climate change has most significantly impacted natural systems. 
  This includes situations such as melting ice, changing precipitation, which affect water resource quality and quantity.
  It has also caused terrestrial, freshwater, and marine species to alter their habits.
  """)
  st.write("""
  The consequences of emission rise follow a snowball effect. That is, it exhibits a positive feedback loop that severely magnifies the consequences over time. 
  Some of these include negative effects on human health (especially so for marginalized communities), economic inequality, 
  impact from extreme events such as heat waves, droughts, cyclones, etc. 
  """)

  st.write("""
  Some second-order consequences of these events are disruption of food production and water supply, 
  alteration of ecosystems, violent conflict, etc. 
  These are further intensified due to our lack of preparedness regarding them.
  """)
  st.image("https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2Faayush%2Fr8XOhzwE_m.png?alt=media&token=3a757954-5455-42ee-a18e-73fdd6d53afb", caption="AR5 Climate Change 2014: Impacts, Adaptation, and Vulnerability — IPCC", width=500)


  # Cumulative Emissions: Time Series
  st.subheader("Emissions Worldwide have been growing")
  # Write a paragraph with template text
  st.write("""
  Ever since the industrial revolution the greenhouse gas output has been quickly rising.
  The most problmatic of the greenhouse gases is carbon dioxide (CO2) which is emmited in enormous quantities mainly when burning fossil fuels.
  The other main contributor to global warming is methane (CH4) which is emitted in far smaller amounts, but is much more potent and therefore 
  accounts for roughly 1/3 of the temperature increase due to the greenhouse effect.
  To give a sense of the rate at which CO2 and methane have been emitted, the plot below shows the historical yearly emissions for the whole world.
  """)

  # Plot of the CO2 and methane emissions for the entire world
  lineplot_space = st.columns((2, 1))
  with lineplot_space[1]:
    st.write("")
    st.write("")
    st.write("")  # Just some padding
    st.write("")
    st.write("")
    select_country = st.selectbox("Select region", ["World", "Europe", "Finland", "Sweden", "Norway", "China", "United States"])

  fig = emissions_history_plot(country = select_country, from_year = 1850)
  with lineplot_space[0]:
    st.plotly_chart(fig)


  st.write("""It's clear that CO2 emissions have been increasing for many years. 
  To get a closer look at which countries contribute most to CO2 emissions take a look at the map below.""")



  # Load data
  # years in data set and in the slider
  start_year = 1950
  end_year = int(max_year())
  country_geo, df = load_data(start_year, end_year)

  co2_per_capita_choropleth, co2_choropleth, co2_growth_choropleth = heatmap(country_geo, df.copy())


  # Setup a folium map at a high-level zoom
  map = folium.Map(zoom_start=1, tiles='cartodbpositron')
  # Set aside some space for the map
  map_space = st.columns((2, 1))

  with map_space[1]:
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

  Fullscreen().add_to(map)

  with map_space[0]:
    folium_static(map, width = 900)



  st.write("""Below is another way to visualize how the emissions have been changing in each country. 
  This plot is particularly useful for finding the outliers.""")

  # Scatter plot of changes in CO2 emissions

  # Element placeholders

  changes_plot_space = st.columns((2, 1))
  with changes_plot_space[0]:
    plot_ph = st.empty()
  
  with changes_plot_space[1]:
    st.write("")
    st.write("")
    st.write("")  # Just some padding
    st.write("")
    st.write("")
    slider_ph = st.empty()
    animate = st.button('animate')

  year_scatter = slider_ph.slider("Year", start_year, end_year, end_year - 2, 1, key = 1)
  fig = changes_plot(df, year_scatter, rangeX = None)
  plot_ph.plotly_chart(fig)
  
  if animate:
      for x in range(year_scatter, end_year, 1):
          time.sleep(.5)

          year_scatter = slider_ph.slider("Year", start_year, end_year, year_scatter + 1, 1, key = str(year_scatter) + "animation")
          fig = changes_plot(df, year_scatter, rangeX = [-100, 100])
          plot_ph.plotly_chart(fig)





  st.write("""
  Dictumst quisque sagittis purus sit amet volutpat. Consequat interdum varius sit amet mattis vulputate enim nulla. 
  Nulla posuere sollicitudin aliquam ultrices sagittis orci a scelerisque. Sit amet purus gravida quis blandit. 
  Sit amet consectetur adipiscing elit pellentesque. Dictumst vestibulum rhoncus est pellentesque elit ullamcorper dignissim. 
  Dolor sit amet consectetur adipiscing. Nec feugiat in fermentum posuere. Eu ultrices vitae auctor eu augue ut lectus arcu. 
  Aenean euismod elementum nisi quis eleifend. In mollis nunc sed id semper risus in hendrerit gravida. 
  Massa tincidunt dui ut ornare lectus sit amet est placerat. Cursus mattis molestie a iaculis at erat pellentesque. Eget nullam non nisi est.
  """)

  # Bold text
  st.markdown("**Expand on Sub-saharan africa, latin america, etc**")
  st.text("VIZ TODO")
  st.text("""
  Ullamcorper velit sed ullamcorper morbi. Elementum facilisis leo vel fringilla est ullamcorper. 
  Libero id faucibus nisl tincidunt eget nullam non. Suspendisse interdum consectetur libero id faucibus nisl. 
  Nulla aliquet porttitor lacus luctus accumsan tortor posuere ac. 
  Vitae purus faucibus ornare suspendisse sed nisi lacus. Dui ut ornare lectus sit amet est placerat in egestas. 
  Interdum velit laoreet id donec ultrices tincidunt arcu non sodales.
  """)

  # Solutions, not just sources
  st.subheader("But, which sectors actually contribute to this?")
  st.markdown("**TODO:** Verna's visualizations will go here.")
  st.write("""
  Global emissions can be grouped according to their source sectors. One way to do this is the following where 4 different sources are 
  identified and those then broken into further sub-sectors and sub-sub-sectors. These four sectors are from the largest to the smallest: 
  Energy related emission, agriculture, forestry, and land use related emissions, industrial process related emissions and waste related emissions.  

  As mentioned of these sectors, energy is with 73,2% the largest source of emissions. 54% of energy related emissions come from energy in industry, 
  22,1% from transportation, and 23,9% from energy usage in buildings both commercial and residential. Transportation related emissions are mainly 
  from roads. This is visible in the figure above as the circles are relative to the proportion of total emissions. 

  The remaining 26,8% of the emissions are as following: 18,4% of emissions come from agriculture, forestry & land use which mainly consists 
  of livestock, manure, rice cultivation, agricultural soils, and crop related emissions. Industrial processes, cement and chemical & petrochemical, 
  account for 5,2% of the emissions and waste, wastewater, and landfills, for 3,2%. 
  """)
  st.image("template_image.png", width=500)

  st.subheader("What can we do about this?")
  st.image("template_image.png", width=500)

  st.markdown("**As Individuals**")
  st.text("""
  Ullamcorper velit sed ullamcorper morbi. Elementum facilisis leo vel fringilla est ullamcorper. 
  Libero id faucibus nisl tincidunt eget nullam non. Suspendisse interdum consectetur libero id faucibus nisl. 
  Nulla aliquet porttitor lacus luctus accumsan tortor posuere ac. 
  Vitae purus faucibus ornare suspendisse sed nisi lacus. Dui ut ornare lectus sit amet est placerat in egestas. 
  Interdum velit laoreet id donec ultrices tincidunt arcu non sodales.
  """)
  st.markdown("**As Companies**")
  st.text("""
  Ullamcorper velit sed ullamcorper morbi. Elementum facilisis leo vel fringilla est ullamcorper. 
  Libero id faucibus nisl tincidunt eget nullam non. Suspendisse interdum consectetur libero id faucibus nisl. 
  Nulla aliquet porttitor lacus luctus accumsan tortor posuere ac. 
  Vitae purus faucibus ornare suspendisse sed nisi lacus. Dui ut ornare lectus sit amet est placerat in egestas. 
  Interdum velit laoreet id donec ultrices tincidunt arcu non sodales.
  """)
  st.markdown("**As Societies**")
  st.text("""
  Ullamcorper velit sed ullamcorper morbi. Elementum facilisis leo vel fringilla est ullamcorper. 
  Libero id faucibus nisl tincidunt eget nullam non. Suspendisse interdum consectetur libero id faucibus nisl. 
  Nulla aliquet porttitor lacus luctus accumsan tortor posuere ac. 
  Vitae purus faucibus ornare suspendisse sed nisi lacus. Dui ut ornare lectus sit amet est placerat in egestas. 
  Interdum velit laoreet id donec ultrices tincidunt arcu non sodales.
  """)

  

elif page == "About":
  st.title("About")
  st.write("""
  This website was created as part of the Data Science Project course at Aalto University.

  The goal of the project was to find ways to communicate climate change in a clear and impactful way with an interactive web page.  

  The focus was especially on capturing the emission reduction momentum by visualizing greenhouse emissions, in particular CO2, and the 
  explanatory phenomena by first exploring the past and then into the future. 
  """)





















#################################################
#  CODE EXAMPLES
################

# How to store some information in Streamlit if Streamplit changes it back to default when you don't want.
# For example if a button has been pressed.

# # Keep the state of the button press between actions
# @st.cache(allow_output_mutation=True)
# def button_states():
#     return {"pressed": None}

# press_button = st.button("Press it Now!")
# is_pressed = button_states()  # gets our cached dictionary

# if press_button:
#     # any changes need to be performed in place
#     is_pressed.update({"pressed": True})

# if is_pressed["pressed"]:  # saved between sessions
#     th = st.number_input("Please enter the values from 0 - 10")
