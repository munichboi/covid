import numpy as np # linear algebra
import streamlit as st
import pandas as pd
from pyecharts.charts import Bar
from streamlit_echarts import st_pyecharts
import pydeck as pdk
import matplotlib.pyplot as plt
st.set_page_config(
    page_title="Pakapol Chuleewan",
    page_icon="👋",
)

st.write("# Covid-19 2022 😷")

COVID_2022_url = ('worldwide covid data with location.csv')

def load_covid_data_2022():
    data = pd.read_csv(COVID_2022_url)
    # data = data[(data['Total Tests'].isna())|(data['Total Recovered'].isna())|(data['Active Cases'].isna())]
    data.fillna(0,inplace=True)
    data.isna().sum()
    data['Total Recovered'] = data['Total Recovered'].astype(int)
    data['Active Cases'] = data['Active Cases'].astype(int)
    data['Total Tests'] = data['Total Tests'].astype(int)
    data['Tests/ 1M pop'] = data['Tests/ 1M pop'].astype(int)

    return data

covid_data_2022 = load_covid_data_2022()


countrys = st.multiselect(
    'Select Country',
    covid_data_2022['Country'],
    ['Thailand', 'Laos']
)

country_index = []

for i in countrys:
    country_index.append(covid_data_2022.index[covid_data_2022['Country']==i].values[0])

columns = st.multiselect(
    "Select Column",
    covid_data_2022.columns.values.tolist()[1:],
    ['Total Cases', 'Population']
)

y_axis = []

if (len(columns) > 0 and len(country_index) > 0):
    for i in country_index:
        y_axis.append(int(covid_data_2022[columns[0]][i]))
    b = (
        Bar()
        .add_xaxis(countrys)
        .add_yaxis(columns[0], y_axis)
    )

# country_index 
if (len(columns) > 1):
    for column_name in columns[1:]:
        new_y_axis_value = []
        for index in country_index:
            new_y_axis_value.append(int(covid_data_2022[column_name][index]))
        b.add_yaxis(column_name, new_y_axis_value)


if (len(countrys) > 0 and len(columns) > 0):
    st_pyecharts(b)

st.markdown(
    """
    ## Research Questions
    - Which Country has the highest and Lowest number of active cases ?
    - Which country must, may and avoid imposing lockdowns ?
"""
)

st.markdown(
    """
    ### Question 1
    - Which Country has the highest and Lowest number of active cases ?
""")

covid_data_2022['lock_down_rate']=[round(covid_data_2022['Active Cases'][i]/covid_data_2022['Population'][i],4) for i in range(len(covid_data_2022))]
active_cases_data=covid_data_2022.set_index('Country')['lock_down_rate'].to_dict()

max_active_case_country=max(active_cases_data, key=active_cases_data.get)
min_active_case_country=min(active_cases_data, key=active_cases_data.get)

st.write('Country with Maximum lock_down_rate : ',max_active_case_country,' ({} cases)'.format(list(covid_data_2022[covid_data_2022['Country']==max_active_case_country]['Active Cases'])[0]))
st.write('Country with Minimum lock_down_rate : ',min_active_case_country,' ({} cases)'.format(list(covid_data_2022[covid_data_2022['Country']==min_active_case_country]['Active Cases'])[0]))

# Considering Lockdown is imposed when Active Cases/Population >0.1

# st.write("Countries that should LOCKDOWN :\n")
# st.write(list(covid_data_2022[covid_data_2022['lock_down_rate']>0.1]['Country']))

# st.write("\nCountries that may LOCKDOWN :\n")
# st.write(list(covid_data_2022[(covid_data_2022['lock_down_rate']>=0.001)&(covid_data_2022['lock_down_rate']<=0.1)]['Country']))

# st.write("\nCountries that can avoid LOCKDOWN :\n")
# st.write(list(covid_data_2022[covid_data_2022['lock_down_rate']<0.001]['Country']))


# Q2
st.markdown(
    """
    ### Question 2
    - Which country must, may and avoid imposing lockdowns ?
""")


# Define a layer to display on a map
covid_data_2022
layer = pdk.Layer(
    "ScatterplotLayer",
    covid_data_2022,
    pickable=True,
    opacity=1,
    stroked=True,
    filled=True,
    radius_scale=10,
    radius_min_pixels=15,
    radius_max_pixels=15,
    line_width_min_pixels=1,
    get_position=["longitude", "latitude"],
    get_radius='Recovery_Rate',
    get_fill_color="[lock_down_rate > 0.1 ? 255 : lock_down_rate >=0.001 ? 255 : 0, lock_down_rate > 0.1 ? 0 : lock_down_rate >=0.001 ? 188 : 255, 0]",
    elevation_scale=4,
    elevation_range=[0, 1000]
)


covid_data_2022
# Render
r = pdk.Deck(layers=[layer], tooltip={"html": "{Country}"})
r.to_html("scatterplot_layer.html")

map = st.pydeck_chart(r)
