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

from util import load_data, get_OWID_data, max_year
from plots import heatmap, changes_plot, model_future_CO2_emissions, model_future_methane_emissions, emissions_history_plot, world_temperature




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
  # Figure of worldwide mean temperature over time
  st.plotly_chart(world_temperature())
  st.write("""
  Human-induced global warming reached about 1°C (likely between 0.8 and 1.2°C) above pre-indstrial levels in 2017, with a 0.2°C increase per decade.
  Most land regions are warming up faster than the global average - depending on the considered temperature dataset, 20-40% of the world population 
  live in regions that had already experienced warming of more than 1.5°C in at least one season by the decade 2006-2015.

  The straight lines in the figure above represent a 1°C and 1.5°C increase from pre-industrial levels, respectively. 
  Global warming is defined in the IPCC report as an increase
  in combined surface air and sea surface temperatures averaged over the globe and a 30-year period, usually relative to the period 1850-1900.
  By that measure, warming from pre-industrial levels to the decade 2006-2015 is assessed to be approximately 0.87°C.
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

  co2_per_capita_choropleth, co2_choropleth, co2_growth_choropleth = heatmap(country_geo, df.copy(), start_year, end_year)


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

  template_image = "./res/template_image.png"
  # Bold text
  st.markdown("**Expand on Sub-saharan africa, latin america, etc**")
  st.text("VIZ TODO")
  # Add template_image
  st.image(template_image, width=500)
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

  st.subheader("What can we do about this?")

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
