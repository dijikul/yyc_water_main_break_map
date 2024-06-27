import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import pydeck as pdk

# Define the path to the local XML file
LOCAL_XML_PATH = "data/water_main_breaks.xml"

@st.cache_data
def fetch_data(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error reading data: {e}")
        return None

def parse_xml(content):
    root = ET.fromstring(content)
    data = []
    columns = []
    
    # Find entries in the XML
    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
    for entry in entries:
        entry_data = {}
        properties = entry.findall('.//{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties/*')
        for prop in properties:
            tag = prop.tag.split('}')[-1]
            if tag not in columns:
                columns.append(tag)
            entry_data[tag] = prop.text
        data.append(entry_data)
    
    df = pd.DataFrame(data, columns=columns)
    # Split 'point' column into 'lat' and 'lon'
    if 'point' in df.columns:
        df[['lon', 'lat']] = df['point'].str.extract(r'POINT \(([^ ]+) ([^ ]+)\)')
        df['lat'] = df['lat'].astype(float)
        df['lon'] = df['lon'].astype(float)
    return df

data_content = fetch_data(LOCAL_XML_PATH)

if data_content:
    df = parse_xml(data_content)

    # Streamlit App
    st.title('Calgary Water Main Breaks Visualization')

    st.write("Available columns:", df.columns.tolist())

    # Display the raw data
    if st.checkbox('Show raw data'):
        st.write(df)

    # Filter options
    st.sidebar.header('Filter options')
    if 'year' in df.columns:
        year_filter = st.sidebar.multiselect('Select Year', options=df['year'].unique())
        if year_filter:
            df = df[df['year'].isin(year_filter)]
    if 'status' in df.columns:
        status_filter = st.sidebar.multiselect('Select Status', options=df['status'].unique())
        if status_filter:
            df = df[df['status'].isin(status_filter)]

    # Display filtered data
    st.write('Filtered Data', df)

    # Map Visualization
    st.header('Map Visualization')
    if not df.empty and 'lat' in df.columns and 'lon' in df.columns:
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[lon, lat]',
            get_radius=100,
            get_fill_color='[180, 0, 200, 140]',
            pickable=True,
            tooltip=True,
        )
        tooltip = {
            "html": "<b>Date:</b> {break_date} <br/> <b>Type:</b> {break_type} <br/> <b>Status:</b> {status}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        }
        view_state = pdk.ViewState(
            latitude=df['lat'].mean(),
            longitude=df['lon'].mean(),
            zoom=10,
            pitch=50,
        )
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
        st.pydeck_chart(r)
    else:
        st.write("No geographic data available for visualization.")

else:
    st.error("Failed to load data. Please check the file path or the file content.")
