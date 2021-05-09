import datetime
import json
import numpy as np
import requests
import pandas as pd
import streamlit as st
from copy import deepcopy
import math

# faking chrome browser
browser_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_mapping():
    df = pd.read_csv("district_mapping.csv")
    return df

def write_chennai_coordinates():
    df = pd.read_csv("pincodes.csv")

    for index, row in df.iterrows():
        pin = str(math.trunc(row['pincode']))
        while len(pin) != 6:
            pin = "0" + pin
        coordinates = find_coordinates(pin)
        df1.at[index,'latitude'] = coordinates['latitude']
        df1.at[index,'longitude'] = coordinates['longitude']
    columns = ['latitude', 'longitude']
    df['coordinates'] = df[columns].to_dict(orient='records')
    df = df.drop(columns=columns)
    df.to_csv("pincodes.csv", index = False, header = True)
    return df

def load_chennai_coordinates():
    df = pd.read_csv("pincodes.csv")
    return df

def filter_column(df, col, value):
    df_temp = deepcopy(df.loc[df[col] == value, :])
    return df_temp

def filter_capacity(df, col, value):
    df_temp = deepcopy(df.loc[df[col] > value, :])
    return df_temp

def find_coordinates(pincode):
    homeUrl = "http://dev.virtualearth.net/REST/v1/Locations/IN/{}?key=AuyegZZi5R2_xFXcfOWydEmo3XtAcRX_Of1YrfsQWfht93egm1XheF4mpCKhfuVU".format(pincode)          
    response = requests.get(homeUrl, headers=browser_header)
    if response.ok:
        response_json = json.loads(response.text)
        if response_json is not None:
            return {'latitude': response_json['resourceSets'][0]['resources'][0]['geocodePoints'][0]['coordinates'][0], 'longitude': response_json['resourceSets'][0]['resources'][0]['geocodePoints'][0]['coordinates'][1] }
    return {'latitude': 0, 'longitude': 0}

def find_distance(origin, destination):
    homeUrl = "https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins={},{}&destinations={}&travelMode=driving&key=AuyegZZi5R2_xFXcfOWydEmo3XtAcRX_Of1YrfsQWfht93egm1XheF4mpCKhfuVU".format(origin['latitude'], origin['longitude'], destination)         
    response = requests.get(homeUrl, headers=browser_header)
    if response.ok:
        response_json = json.loads(response.text)
        if response_json is not None:
            return response_json['resourceSets'][0]['resources'][0]['results']
    return -1

def get_chennai_coordinate(dict, pincode):
    strcoord = dict[pincode]
    strcoord = strcoord.replace("\'", "\"")
    coordinate = json.loads(strcoord)
    return coordinate

mapping_df = load_mapping()
chennai_coordinates_df = load_chennai_coordinates()

mapping_dict = pd.Series(mapping_df["district id"].values,
                         index = mapping_df["district name"].values).to_dict()
chennai_coordinates_dict = pd.Series(chennai_coordinates_df["coordinates"].values,
                         index = chennai_coordinates_df["pincode"].values).to_dict()

rename_mapping = {
    'date': 'Date',
    'min_age_limit': 'Minimum Age Limit',
    'available_capacity': 'Available Capacity',
    'vaccine': 'Vaccine',
    'pincode': 'Pincode',
    'name': 'Hospital Name',
    'state_name' : 'State',
    'district_name' : 'District',
    'block_name': 'Block Name',
    'fee_type' : 'Fees'
    }

st.title('CoWIN Vaccination Slot Availability')
st.info('The CoWIN APIs are geo-fenced so sometimes you may not see an output! Please try after sometime ')

# numdays = st.sidebar.slider('Select Date Range', 0, 100, 10)
unique_districts = list(mapping_df["district name"].unique())
unique_districts.sort()

left_column_1, right_column_1 = st.beta_columns(2)
with left_column_1:
    numdays = st.slider('Select Date Range', 0, 100, 5)

with right_column_1:
    dist_inp = st.selectbox('Select District', unique_districts)

DIST_ID = mapping_dict[dist_inp]

base = datetime.datetime.today()
date_list = [base + datetime.timedelta(days=x) for x in range(numdays)]
date_str = [x.strftime("%d-%m-%Y") for x in date_list]

final_df = None
for INP_DATE in date_str:
    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(DIST_ID, INP_DATE)
    response = requests.get(URL, headers=browser_header)
    if (response.ok) and ('centers' in json.loads(response.text)):
        resp_json = json.loads(response.text)['centers']
        if resp_json is not None:
            df = pd.DataFrame(resp_json)
            if len(df):
                df = df.explode("sessions")
                df['min_age_limit'] = df.sessions.apply(lambda x: x['min_age_limit'])
                df['vaccine'] = df.sessions.apply(lambda x: x['vaccine'])
                df['available_capacity'] = df.sessions.apply(lambda x: x['available_capacity'])
                df['date'] = df.sessions.apply(lambda x: x['date'])
                df['distance'] = 0

                df = df[["date", "available_capacity", "vaccine", "min_age_limit", "pincode", "name", "state_name", "district_name", "block_name", "fee_type", "distance"]]
                if final_df is not None:
                    final_df = pd.concat([final_df, df])
                else:
                    final_df = deepcopy(df)
            else:
                st.error("No rows in the data Extracted from the API")
#     else:
#         st.error("Invalid response")

if (final_df is not None) and (len(final_df)):
    final_df.drop_duplicates(inplace=True)
    final_df.rename(columns=rename_mapping, inplace=True)
    dest = ""

    left_column_2, left_column_2a, center_column_2, right_column_2, right_column_2a = st.beta_columns(5)
    with left_column_2:
        valid_pincodes = list(np.unique(final_df["Pincode"].values))
        pincode_inp = st.selectbox('Select Pincode', [""] + valid_pincodes)
        if pincode_inp != "":
            final_df = filter_column(final_df, "Pincode", pincode_inp)

    with left_column_2a:
        pincode_inp = st.text_input('Source Pincode', '600097')
        pincode_inp = int(pincode_inp)

    with center_column_2:
        valid_age = [18, 45]
        age_inp = st.selectbox('Select Minimum Age', [""] + valid_age)
        if age_inp != "":
            final_df = filter_column(final_df, "Minimum Age Limit", age_inp)

    with right_column_2:
        valid_payments = ["Free", "Paid"]
        pay_inp = st.selectbox('Select Free or Paid', [""] + valid_payments)
        if pay_inp != "":
            final_df = filter_column(final_df, "Fees", pay_inp)

    with right_column_2a:
        valid_capacity = ["available"]
        cap_inp = st.selectbox('Select Availablilty', [""] + valid_capacity)
        if cap_inp != "":
            final_df = filter_capacity(final_df, "Available Capacity", 0)

    final_df.reset_index(inplace=True, drop=True)

    distances = []
    if pincode_inp > 600000 and pincode_inp < 600113:
        home_coordinates = get_chennai_coordinate(chennai_coordinates_dict, pincode_inp)
    else:
        home_coordinates = find_coordinates(pincode_inp)

    for index, row in final_df.iterrows():
        if DIST_ID == 571:
            destinationLoc = get_chennai_coordinate(chennai_coordinates_dict, row['Pincode'])
        else:
            destinationLoc = find_coordinates(row['Pincode'])
        
        dest = dest + str(destinationLoc['latitude']) + "," + str(destinationLoc['longitude']) + ";"
        if index % 50 == 49:
            dest = dest[:-1]
            distancegroup = find_distance(home_coordinates, dest)
            if distancegroup != -1:
                distances = distances + distancegroup
            dest = ""

    if dest != "":
        dest = dest[:-1]
        distancegroup = find_distance(home_coordinates, dest)
        if distancegroup != -1:
            distances = distances + distancegroup
    
    if len(distances):
        for index, row in final_df.iterrows():
            final_df.at[index,'distance'] = distances[index]['travelDistance']

    table = deepcopy(final_df)
    
    st.dataframe(table)
else:
    st.error("Unable to fetch data currently, please try after sometime")
