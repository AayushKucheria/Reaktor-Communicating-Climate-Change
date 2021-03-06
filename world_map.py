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
from plots import heatmap, changes_plot, emissions_history_plot, world_temperature, sector_breakdown




#######################################
#     PAGE STRUCTURE AND CONTENT      #
#######################################


# Setting page config
st.set_page_config(page_title="Climate Change: A Nordic Perspective", page_icon="🌍", layout="wide")

df = get_OWID_data()
# Create a header aligning the text to the center in streamlit
# Create a sidebar with 3 pages
st.sidebar.header("Menu")
page = st.sidebar.radio("Pages", ("Home", "About"))


# Write some text
if page == "Home":
  st.header("The Climate Crisis")
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

  # Copy the above markdown without the links
  st.markdown("""
  - The temperature is rising
  - Here's why it matters
  - Emissions worldwide have been growing
  - But, which sectors actually contribute to this?
  - What can we do about this?
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
  To give a sense of the rate at which CO2 and methane have been emitted, the plot below shows the historical yearly emissions for a chosen region.
  It also shows a 5-year prediction of the futue emissions.
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


  st.write("""It's clear that CO2 emissions have been increasing for many years, 
  however, in some regions such as Finland and Europe the emissions have started decreasing in the 21st century. 

  Next we will focus on the CO2 emissions as they contribute more to the global warming effect and carbon dioxide stays in the atmosphere much longer than methane.
  To get a closer look at which countries contribute most to CO2 emissions take a look at the map below.
  Select the year and metric you are interested in. You can easily distinguish the biggest poluters and see how your country compares.
  """)



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



  st.write("""The next plot is great for checking how namy countries have managed to decrease their emissions in some year.
  Each spot represents a country and you can easily spot the outliers. 
  Keep in mind that the y-axis scale is logarithmic so the top 3-5 countries produce orders of magnitude more emissions than
  most other countries. They have a large impact on the overall trend.
  The color of the points shows how wealthy a country is using GDP per capita.
  Perhaps the wealthier countries have more money to invest into clean energy sources?""")

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
    As you can see the situation can be quite different from country to country. 
    But a question might arise: What are the main sources of these emissions? 
    The following section will show you how much different sectors of the economy contribute to the problem.
     """)

  template_image = "./res/template_image.png"

  # Solutions, not just sources
  st.subheader("But, which sectors actually contribute to this?")
  st.write(sector_breakdown())
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

  st.subheader("What can we do about this?")
  
  st.write("""
  There are various ways to reduce global warming - we can replace high-emitting fuels such as coal, oil and gas with more climate-friendly 
  alternatives like solar power, wind power, or nuclear power. We can also work on making our buildings, technology and infrastructure more 
  energy-efficient, both in production and in usage. 

  Another approach is to try to remove CO2 that is already in the atmosphere, for example by reforesting the earth – tropical forests once 
  covered 12% of the earth’s landmass, now they only cover 5% -, by changing farming practices to store more carbon in the soil or through 
  direct air capture technology. However, it is unlikely that these methods will be able to remove carbon dioxide faster than it is currently 
  being produced. 
  """)

  st.markdown("**As Individuals**")
  st.write("""
  There are various ways to reduce global warming - we can replace high-emitting fuels such as coal, oil and gas with more climate-friendly 
  alternatives like solar power, wind power, or nuclear power. We can also work on making our buildings, technology and infrastructure more 
  energy-efficient, both in production and in usage. 

  Another approach is to try to remove CO2 that is already in the atmosphere, for example by reforesting the earth – tropical forests once 
  covered 12% of the earth’s landmass, now they only cover 5% -, by changing farming practices to store more carbon in the soil or through 
  direct air capture technology. However, it is unlikely that these methods will be able to remove carbon dioxide faster than it is currently 
  being produced. 
  """)
  st.markdown("**As Companies**")
  st.write("""
  Similarly, companies can impact climate change by reducing the emissions produced by their operations through various measures, such as 
  minimizing transport distances and using carbon-neutral energy sources. 
  """)
  st.markdown("**As Societies**")
  st.write("""
  A promising method to curb climate change on a societal level involves encouraging individuals and companies to reduce their own 
  emissions by introducing carbon taxes – by placing a tax or fee on the use of fossil fuels, production and consumption choices leading to 
  higher emissions become more expensive, raising the incentive to switch to more climate-friendly alternatives. 
  """)

  

elif page == "About":
  st.title("About")
  st.write("""
  This website was created as part of the Data Science Project course at Aalto University. The goal of the project was to find ways to communicate climate change in a clear and impactful way with an interactive web page.
  The focus was especially on capturing the emission reduction momentum by visualizing greenhouse emissions, in particular CO2, and the 
  explanatory phenomena by first exploring the past and then into the future. 

  Contributors: Verna, Hanne, Mikolaj, Aayush, Khue, My.
  """)

  st.subheader("Credits")

  st.markdown("""

    This data has been collected, aggregated, and documented by Our World in Data into a co2-dataset publicly available on [github](https://github.com/owid/co2-data).

    More specifically, Our World in Data has collected the data from the following sources:
  - CO2 emissions: this data is sourced from the Global Carbon Project. The Global Carbon Project typically releases a new update of CO2 emissions annually.
  - Greenhouse gas emissions (including methane, and nitrous oxide): this data is sourced from the CAIT Climate Data Explorer, and downloaded from the Climate Watch Portal.
  - Energy (primary energy, energy mix and energy intensity): this data is sourced from a combination of two sources. The BP Statistical Review of World Energy is published annually, but it does not provide data on primary energy consumption for all countries. For countries absent from this dataset, we calculate primary energy by multiplying the World Bank, World Development Indicators metric Energy use per capita by total population figures. The World Bank sources this metric from the IEA.
  - Other variables: this data is collected from a variety of sources (United Nations, World Bank, Gapminder, Maddison Project Database, etc.).
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