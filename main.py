
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from streamlit_calendar import calendar
from st_files_connection import FilesConnection
import boto3
from datetime import datetime

st.title('Band Studio Booking')

conn = st.experimental_connection('s3', type=FilesConnection)

session = boto3.Session(
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["AWS_DEFAULT_REGION"]
)

s3 = session.resource('s3')

def update_booking_times(booking_data):
    booking_data.to_csv("booking_times.csv", index=False)
    s3.Bucket('studio-booker').upload_file("booking_times.csv", "booking_times.csv")

def update_available_times(date):
    formatted_date = convert_date_format(date)
    st.session_state['available_times'] = get_available_times(formatted_date)

def get_booking_status(booking_data):
    dates = pd.date_range(start=pd.Timestamp.today(), periods=14)
    booking_status = pd.DataFrame(index=dates, columns=['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']).fillna('🟢')
    booking_status['Date'] = booking_status.index.strftime('%d.%m.%Y')
    for index, row in st.session_state['booking_data'].iterrows():
        booking_date_str = row['Booking Date'].strftime('%d.%m.%Y')
        booking_status.loc[booking_status['Date'] == booking_date_str, row['Booking Time']] = '🔴 - ' + row['Band Name']

    return booking_status

def get_available_times(date):
    times = ['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']
    bookings_on_date = st.session_state['booking_data'][st.session_state['booking_data']['Booking Date'] == date]
    for index, booking in bookings_on_date.iterrows():
        if booking['Booking Time'] in times:
            times.remove(booking['Booking Time'])
    return times

def convert_date_format(input_date):
    output_date = str(input_date) + " 00:00:00"
    
    return output_date

if 'booking_data' not in st.session_state:
    try:
        st.session_state['booking_data'] = pd.read_csv("booking_times.csv")
        st.session_state['booking_data']['Booking Date'] = pd.to_datetime(st.session_state['booking_data']['Booking Date'])
    except FileNotFoundError:
        st.session_state['booking_data'] = pd.DataFrame(columns=['Band Name', 'Booking Date', 'Booking Time'])
        st.session_state['booking_data'].to_csv("booking_times.csv", index=False)
        s3.Bucket('studio-booker').upload_file("booking_times.csv", "booking_times.csv")
st.session_state['booking_data']



def form():
    with st.form('Booking Form'):
        submit_button = st.form_submit_button('Book Now')

        if submit_button:
            new_booking = {'Band Name': band_name, 'Booking Date': st.session_state['booking_date'], 'Booking Time': booking_time}
            st.session_state['booking_data'] = st.session_state['booking_data'].append(new_booking, ignore_index=True)
            update_booking_times(st.session_state['booking_data'])

column1, column2 = st.columns(2)
with column1:
    band_name = st.text_input('Band Name')
    min_date = pd.Timestamp.today()
    max_date = min_date + pd.DateOffset(days=14)
    if 'booking_date' not in st.session_state:
        st.session_state['booking_date'] = min_date
    if 'booking_date_input' not in st.session_state:
        st.session_state['booking_date_input'] = st.session_state['booking_date']
    st.session_state['booking_date_input'] = st.date_input('Booking Date', value=st.session_state['booking_date_input'], min_value=min_date, max_value=max_date, format="DD.MM.YYYY", on_change=update_available_times, args=[st.session_state['booking_date_input']])
    available_times = st.session_state['available_times']
    if available_times:
        booking_time = st.selectbox('Booking Time', available_times)
    else:
        st.info('No available times for this date.')
    form()

dates = pd.date_range(start=pd.Timestamp.today(), periods=14)
booking_status = pd.DataFrame(index=dates, columns=['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']).fillna('🟢')
booking_status['Date'] = booking_status.index.strftime('%d.%m.%Y')

for index, row in st.session_state['booking_data'].iterrows():
    booking_date_str = row['Booking Date'].strftime('%d.%m.%Y')
    booking_status.loc[booking_status['Date'] == booking_date_str, row['Booking Time']] = '🔴 - ' + row['Band Name']

with column2:
    with st.form('Remove Booking Form'):
        bookings = st.session_state['booking_data'].apply(lambda row: f"{row['Band Name']} - {row['Booking Date'].strftime('%d.%m.%Y')} - {row['Booking Time']}", axis=1).values.tolist()
        selected_booking = st.selectbox('Select a booking to remove', bookings)
        remove_button = st.form_submit_button('Remove Booking')

        if remove_button:
            if selected_booking is not None:
                band_name, booking_date_str, booking_time = selected_booking.split(' - ')
                booking_date = pd.to_datetime(booking_date_str, format='%d.%m.%Y')
                booking_to_remove = st.session_state['booking_data'][(st.session_state['booking_data']['Band Name'] == band_name) & (st.session_state['booking_data']['Booking Date'] == booking_date) & (st.session_state['booking_data']['Booking Time'] == booking_time)]
                st.session_state['booking_data'] = st.session_state['booking_data'].drop(booking_to_remove.index)
                update_booking_times(st.session_state['booking_data'])
                booking_status = get_booking_status(st.session_state['booking_data'])
            else:
                st.warning('No booking selected.')

AgGrid(booking_status.reset_index(drop=True))
def update_available_times(date):
    formatted_date = convert_date_format(date)
    st.session_state['available_times'] = get_available_times(formatted_date)
