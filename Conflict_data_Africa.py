import streamlit as st
import plotly.express as px
import klib
import pydeck as pdk
import pandas as pd
import numpy as np


def getIndexes(dfObj, value):
    ''' Get index positions of value in dataframe i.e. dfObj.'''
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append(row)
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos


st.title('Conflict data in Africa: 1997 to 2016')

rows = 140748
DATE_COLUMN = 'event_date'

@st.cache
def load_data(nrows):
    df = pd.read_csv(r"C:\Users\ainet\PycharmProjects\streamlit\conflict data.csv", nrows=nrows)
    data = klib.data_cleaning(df)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(rows)
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...Done')


if st.checkbox('Show Data'):
    st.subheader('Raw Data')
    st.write(data)


st.subheader('Map of all Conflicts')
year_filter = st.slider('Year', 1997, 2016, 2016)
location_df = data[['year', 'latitude', 'longitude']]
filtered_data = location_df[location_df['year'] == year_filter]
st.subheader(f'Map of all conflicts in {year_filter}')
st.map(filtered_data)


st.subheader(f'Fatalities per country in {year_filter}')
year_df = data[data['year'] == year_filter]
fatal = []
for country in data['country'].unique():
    fatal.append(round(year_df.loc[year_df['country'] == country, 'fatalities'].sum()))
d = {'country': list(data['country'].unique()), 'fatalities': fatal}
df1 = pd.DataFrame(d)
print(df1)
fig = px.bar(df1, x="country", y="fatalities")
st.plotly_chart(fig, use_container_width=True)


option = st.selectbox(
    'Select a country',
    data['country'].unique())

country_df = data[data['country'] == option]
col1, col2 = st.columns(2)
with col1:
    fatal = []
    for year in range(1996, 2017):
        fatal.append(round(country_df.loc[country_df['year'] == year, 'fatalities'].sum()))
    d = {'year': list(np.arange(1996, 2017)), 'fatalities': fatal}
    df1 = pd.DataFrame(d)
    print(df1)
    st.subheader(f'Fatalities in {option}')
    fig = px.bar(df1, x="year", y="fatalities")
    st.plotly_chart(fig, use_container_width=True)


with col2:
    year = st.slider('year', 1997, 2016, 2016)
    st.text(f'Conflicts in {option} in {year}')
    st.metric('Average fatalities per conflict', round(country_df.loc[country_df['year'] == year, 'fatalities'].mean(),1))
    st.metric('Count of conflicts', (country_df.loc[country_df['year'] == year, 'year'].sum())/year)

    table = pd.pivot_table(country_df, values='fatalities', index=['actor1'], columns=['year'], aggfunc=np.sum)
    print(table)
    st.metric('Actors with most fatalities', table[year].max(), getIndexes(table, table[year].max())[0])


