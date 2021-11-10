import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import folium



# Function definitions

# Cached function for downloading/prepping data
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
  return (country_geo, df_map)
  

@st.cache(hash_funcs={tuple: lambda x: 1})
def heatmap(country_geo, df_map):
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
  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
  Tortor dignissim convallis aenean et tortor at risus viverra. Risus nullam eget felis eget nunc lobortis mattis. 
  Integer malesuada nunc vel risus commodo. Lacus viverra vitae congue eu consequat ac felis donec et. 
  Sagittis nisl rhoncus mattis rhoncus urna neque viverra justo nec. Urna et pharetra pharetra massa. 
  Tellus in metus vulputate eu scelerisque. Aenean euismod elementum nisi quis eleifend quam. 
  Tristique senectus et netus et malesuada fames ac. Quis eleifend quam adipiscing vitae proin sagittis nisl rhoncus mattis. 
  Dictum fusce ut placerat orci nulla pellentesque. Vulputate enim nulla aliquet porttitor lacus luctus. Eu volutpat odio facilisis mauris sit amet. 
  Cursus sit amet dictum sit amet justo donec. 
  Tempus iaculis urna id volutpat lacus. Ornare massa eget egestas purus viverra accumsan in nisl. Donec et odio pellentesque diam volutpat.
  """)

  st.markdown("""
  - [The temperature is rising](http://localhost:8501/#the-temperature-is-rising)
  - [Here's why it matters](http://localhost:8501/#heres-why-it-matters)
  - [Emissions worldwide have been growing](http://localhost:8501/#emissions-worldwide-have-been-growing)
  - [But, which sectors actually contribute to this?](http://localhost:8501/#but-which-sectors-actually-contribute-to-this)
  - [What can we do about this?](http://localhost:8501/#what-can-we-do-about-this)
  """)

  st.subheader("The temperature is rising")
  # Add template_image.png to the page
  st.image("template_image.png", width=500)
  st.write("""
  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
  Tortor dignissim convallis aenean et tortor at risus viverra. Risus nullam eget felis eget nunc lobortis mattis.
  Integer malesuada nunc vel risus commodo. Lacus viverra vitae congue eu consequat ac felis donec et.
  Sagittis nisl rhoncus mattis rhoncus urna neque viverra justo nec. Urna et pharetra pharetra massa.
  """)

  st.subheader("Here's why it matters")
  # Add template_image.png to the page
  st.image("template_image.png", width=500)
  st.write("""
  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
  Tortor dignissim convallis aenean et tortor at risus viverra. Risus nullam eget felis eget nunc lobortis mattis. 
  Integer malesuada nunc vel risus commodo. Lacus viverra vitae congue eu consequat ac felis donec et. 
  Sagittis nisl rhoncus mattis rhoncus urna neque viverra justo nec. Urna et pharetra pharetra massa. 
  Tellus in metus vulputate eu scelerisque. Aenean euismod elementum nisi quis eleifend quam. 
  Tristique senectus et netus et malesuada fames ac. Quis eleifend quam adipiscing vitae proin sagittis nisl rhoncus mattis. 
  Dictum fusce ut placerat orci nulla pellentesque. Vulputate enim nulla aliquet porttitor lacus luctus. Eu volutpat odio facilisis mauris sit amet. 
  Cursus sit amet dictum sit amet justo donec. 
  Tempus iaculis urna id volutpat lacus. Ornare massa eget egestas purus viverra accumsan in nisl. Donec et odio pellentesque diam volutpat.
  """)

  # Cumulative Emissions: Time Series
  st.subheader("Emissions Worldwide have been growing")
  # Write a paragraph with template text
  st.write("""
  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
  Tortor dignissim convallis aenean et tortor at risus viverra. Risus nullam eget felis eget nunc lobortis mattis.
  Integer malesuada nunc vel risus commodo. Lacus viverra vitae congue eu consequat ac felis donec et.
  Sagittis nisl rhoncus mattis rhoncus urna neque viverra justo nec. Urna et pharetra pharetra massa.
  """)




  # CONSTANTS
  # years for the slider
  start_year = 1950
  end_year = 2019
  
  country_geo, df_map = load_data(start_year, end_year)
  co2_per_capita_choropleth, co2_choropleth, co2_growth_choropleth = heatmap(country_geo, df_map)


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
  st.text("""
  Ullamcorper velit sed ullamcorper morbi. Elementum facilisis leo vel fringilla est ullamcorper. 
  Libero id faucibus nisl tincidunt eget nullam non. Suspendisse interdum consectetur libero id faucibus nisl. 
  Nulla aliquet porttitor lacus luctus accumsan tortor posuere ac. 
  Vitae purus faucibus ornare suspendisse sed nisi lacus. Dui ut ornare lectus sit amet est placerat in egestas. 
  Interdum velit laoreet id donec ultrices tincidunt arcu non sodales.
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
  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
  """)