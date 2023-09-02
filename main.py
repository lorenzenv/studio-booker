
import streamlit as st
import pandas as pd
from st_files_connection import FilesConnection
import boto3
from io import StringIO

st.set_page_config(page_title="Liebermann Studio Zeit", layout="wide", page_icon=":guitar:", )

st.title(':guitar: Liebermann Studio Zeit')

conn = st.experimental_connection('s3', type=FilesConnection)

session = boto3.Session(
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["AWS_DEFAULT_REGION"]
)

s3 = session.resource('s3')


bucket_name = "studio-booker"  
file_key = "booking_times.csv"

######################
### UTIL FUNCTIONS ###
######################

def get_df():
    obj = s3.Object(bucket_name, file_key)
    response = obj.get()
    read_buffer = StringIO(response['Body'].read().decode())
    df = pd.read_csv(read_buffer)
    return df

def get_available_times(date, df):
    times = ['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']
    date = convert_date_format(date)
    bookings_on_date = df[df['Booking Date'] == date]
    for index, booking in bookings_on_date.iterrows():
        if booking['Booking Time'] in times:
            times.remove(booking['Booking Time'])
    return times

def convert_date_format(input_date):
    return input_date.strftime('%d.%m.%Y')

def update_booking_times(band_name, datum, selected_time):
    booking_data = pd.DataFrame({'Band Name': [band_name], 'Booking Date': [datum], 'Booking Time': [selected_time]})
    df = get_df()
    df = df.append(booking_data)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3.Object(bucket_name, file_key).put(Body=csv_buffer.getvalue())
    st.info("**Buchung erfolgreich!**")

def get_booking_status(df):
    dates = pd.date_range(start=pd.Timestamp.today(), periods=14)
    booking_status = pd.DataFrame(index=dates, columns=['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']).fillna('🟢')
    booking_status['Date'] = booking_status.index.strftime('%d.%m.%Y')
    for index, row in df.iterrows():
        booking_date_str = row['Booking Date']
        booking_status.loc[booking_status['Date'] == booking_date_str, row['Booking Time']] = '🔴 - ' + row['Band Name']

    booking_status = booking_status.reindex(columns=['Date', 'Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)'])  # Replace these with the actual column names
    return booking_status

def get_all_bookings(df):
    df = df.sort_values(by=['Booking Date', 'Booking Time'])
    formatted_list = []
    for index, row in df.iterrows():
        formatted_string = f"{row['Booking Date']} - {row['Band Name']} - {row['Booking Time']}"
        formatted_list.append(formatted_string)
    return formatted_list

def delete_booking(booking_to_delete, df):
    indices_to_remove = []

    for index, row in df.iterrows():
        formatted_string = f"{row['Booking Date']} - {row['Band Name']} - {row['Booking Time']}"
        if formatted_string == booking_to_delete:
            indices_to_remove.append(index)

    df.drop(indices_to_remove, inplace=True)
    df.reset_index(drop=True, inplace=True)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3.Object(bucket_name, file_key).put(Body=csv_buffer.getvalue())

######################
###### MAIN PAGE #####
######################

df = get_df()

min_date = pd.Timestamp.today()
max_date = min_date + pd.DateOffset(days=14)

column1, column2 = st.columns(2)

with column1:
    band_name = st.text_input('Wer?')
    datum = st.date_input(min_value=min_date, max_value=max_date, label='Welcher Tag?', format="DD.MM.YYYY")
    datum_formatted = convert_date_format(datum)
    available_times = get_available_times(datum, df)
    if available_times != []:
        selected_time = st.selectbox('Welche Uhrzeit?', available_times)
        send_button = st.button('Buchen')
    else:
        send_button = st.button("Keine Zeit mehr frei an diesem Tag", disabled=True)

    if send_button:
        st.info(f"**{datum_formatted} - {selected_time}** \n\n für **{band_name}** gebucht")
        update_booking_times(band_name, datum_formatted, selected_time)
        st.experimental_rerun()

    all_bookings = get_all_bookings(df)
    booking_to_delete = st.selectbox("Buchungen", all_bookings)

    delete_button = st.button("Löschen")
    if delete_button:
        delete_booking(booking_to_delete, df)
        st.experimental_rerun()

booking_status = get_booking_status(df)

with column2:
    st.dataframe(booking_status, use_container_width=True, hide_index=True, height=528)

# def update_booking_times(booking_data):
#     booking_data.to_csv("booking_times.csv", index=False)
#     s3.Bucket('studio-booker').upload_file("booking_times.csv", "booking_times.csv")

# def update_available_times(date):
#     if date is not None:
#         formatted_date = convert_date_format(date)
#         st.session_state['available_times'] = get_available_times(formatted_date)

# def get_available_times(date):
#     times = ['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']
#     bookings_on_date = st.session_state['booking_data'][st.session_state['booking_data']['Booking Date'] == date]
#     for index, booking in bookings_on_date.iterrows():
#         if booking['Booking Time'] in times:
#             times.remove(booking['Booking Time'])
#     return times

# def convert_date_format(input_date):
#     output_date = str(input_date) + " 00:00:00"
    
#     return output_date

# band_name = st.text_input('Band Name')
# min_date = pd.Timestamp.today()
# max_date = min_date + pd.DateOffset(days=14)

# submit_button = st.button('Book Now')

# if submit_button:
#     new_booking = {'Band Name': band_name, 'Booking Date': booking_date, 'Booking Time': booking_time}

# dates = pd.date_range(start=pd.Timestamp.today(), periods=14)
# booking_status = pd.DataFrame(index=dates, columns=['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']).fillna('🟢')
# booking_status['Date'] = booking_status.index.strftime('%d.%m.%Y')
# booking_status = booking_status[['Date', 'Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']]

# for index, row in st.session_state['booking_data'].iterrows():
#     booking_date_str = row['Booking Date'].strftime('%d.%m.%Y')
#     booking_status.loc[booking_status['Date'] == booking_date_str, row['Booking Time']] = '🔴 - ' + row['Band Name']

# bookings = st.session_state['booking_data'].apply(lambda row: f"{row['Band Name']} - {row['Booking Date'].strftime('%d.%m.%Y')} - {row['Booking Time']}", axis=1).values.tolist()
# selected_booking = st.selectbox('Select a booking to remove', bookings)
# remove_button = st.button('Remove Booking')

# if remove_button:
#     if selected_booking is not None:
#         band_name, booking_date_str, booking_time = selected_booking.split(' - ')
#         booking_date = pd.to_datetime(booking_date_str, format='%d.%m.%Y')
#     else:
#         st.warning('No booking selected.')

# booking_status.reset_index(drop=True)
