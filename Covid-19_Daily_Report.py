import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt
import datetime
import time

#########################################################################################
# Load data

DATA_URL = ('covid.csv')
@st.cache(allow_output_mutation=True)
def load_data():
    data = pd.read_csv(DATA_URL)
    data['date'] = pd.to_datetime(data['date'],format='%d/%m/%Y' ).dt.strftime('%Y-%m-%d')
    return data

# Load rows of data into the dataframe.
df = load_data()

st.title('Covid Daily Report 📝')

########################################################################################
### SELECTBOX widgets

metrics =['total_cases','new_cases','total_deaths','new_deaths','total_cases_per_million','new_cases_per_million','total_deaths_per_million','new_deaths_per_million','total_tests','new_tests','total_tests_per_thousand','new_tests_per_thousand']
cols = st.selectbox('Covid metric to view', metrics)

########################################################################################
## MAP

# let's ask the user which column should be used as Index
if cols in metrics:   
    metric_to_show_in_covid_Layer = cols 

# Set viewport for the deckgl map
view = pdk.ViewState(latitude=0, longitude=0, zoom=0.2)

# Create the scatter plot layer
covidLayer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        pickable=True,
        opacity=0.3,
        stroked=True,
        filled=True,
        radius_scale=10,
        radius_min_pixels=5,
        radius_max_pixels=40,
        line_width_min_pixels=1,
        get_position=["Longitude", "Latitude"],
        get_radius=metric_to_show_in_covid_Layer,
        get_fill_color=[252, 136, 3],
        get_line_color=[255,0,0],
    )

# Create the deck.gl map
r = pdk.Deck(
layers=[covidLayer],
initial_view_state=view,
map_style='light_no_labels',
    tooltip={'html': '<b>{Country}:</b> total_cases: {total_cases}'},
)
r.to_html()
def onButtonClick():
    date = datetime.date(2020,1,1)
    for i in range(0, 120, 1):
        # Increment day by 1
        date += datetime.timedelta(days=1)

        # Update data in map layers
        covidLayer.data = df[df['date'] == date.isoformat()]

        # Update the deck.gl map
        r.update()

        # Render the map
        map.pydeck_chart(r)

        # Update the heading with current date
        subheading.subheader("%s on : %s" % (metric_to_show_in_covid_Layer, date.strftime("%B %d, %Y")))
        
        # wait 0.1 second before go onto next day
        time.sleep(0.05)

st.button("Play", on_click=onButtonClick)

# Create a subheading to display current date
subheading = st.subheader("")

map = st.pydeck_chart(r)


############################################################################################

countrys = df['Country'].unique()

country = st.selectbox(
        "Country",
        countrys
    )

# bar chart 
filter_data = df[(df['date'] >='2020-04-01') & (df['Country']== country)].set_index("date")

st.markdown( country + " daily Death cases from 1st April 2020")

st.bar_chart(filter_data[['total_deaths']])


########################################################################################
    #   WIDGETS
subset_data = df

### MULTISELECT
country_name_input = st.multiselect(
'Country name',
df.groupby('Country').count().reset_index()['Country'].tolist())

# by country name
if len(country_name_input) > 0:
    subset_data = df[df['Country'].isin(country_name_input)]
  
########################################################################################
## linechart

st.subheader('Comparision of infection growth')

total_cases_graph  = alt.Chart(subset_data).transform_filter(
    alt.datum.total_cases > 0  
).mark_line().encode(
    x=alt.X('date', type='nominal', title='Date'),
    y=alt.Y('sum(total_cases):Q',  title='Confirmed cases'),
    color='Country',
    tooltip = 'sum(total_cases)',
).properties(
    width=1500,
    height=600
).configure_axis(
    labelFontSize=17,
    titleFontSize=20
)

st.altair_chart(total_cases_graph)

st.write(df)
