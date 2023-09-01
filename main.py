# Import necessary libraries
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from streamlit_calendar import calendar
from st_files_connection import FilesConnection

# Create a Streamlit app
st.title('Band Studio Booking')
# Create a connection object.
conn = st.experimental_connection('s3', type=FilesConnection)

# Define a function to update the booking times file and the S3 bucket
def update_booking_times(booking_data):
    # Write the updated DataFrame to a CSV file in the local file system.
    booking_data.to_csv("booking_times.csv", index=False)
    # Upload the updated file to the S3 bucket.
    s3.Bucket('studio-booker').upload_file("booking_times.csv", "booking_times.csv")

# Define a function to get the booking status
def get_booking_status(booking_data):
    # Create a DataFrame for the next 14 days
    dates = pd.date_range(start=pd.Timestamp.today(), periods=14)
    booking_status = pd.DataFrame(index=dates, columns=['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']).fillna('🟢')
    booking_status['Date'] = booking_status.index.strftime('%d.%m.%Y')

    # Iterate over the booking_data DataFrame and update the booking_status DataFrame with the booking information
    for index, row in st.session_state['booking_data'].iterrows():
        booking_date_str = row['Booking Date'].strftime('%d.%m.%Y')
        booking_status.loc[booking_status['Date'] == booking_date_str, row['Booking Time']] = '🔴 - ' + row['Band Name']

    return booking_status

def get_available_times(date):
    # Define the possible booking times
    times = ['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']
    # Get the bookings for the given date
    bookings_on_date = st.session_state['booking_data'][st.session_state['booking_data']['Booking Date'] == date]
    # Remove the booked times from the list of possible times
    for index, booking in bookings_on_date.iterrows():
        if booking['Booking Time'] in times:
            times.remove(booking['Booking Time'])
    return times

# Import the boto3 library.
import boto3

# Create a session using your AWS credentials.
session = boto3.Session(
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["AWS_DEFAULT_REGION"]
)

# Create a resource object using the session and the service name (in this case, 's3').
s3 = session.resource('s3')

# Try to read the file. If it does not exist, create a new DataFrame and write it to the file.
try:
    if 'booking_data' not in st.session_state:
        st.session_state['booking_data'] = pd.read_csv("booking_times.csv")
        st.session_state['booking_data']['Booking Date'] = pd.to_datetime(st.session_state['booking_data']['Booking Date'])
except FileNotFoundError:
    st.session_state['booking_data'] = pd.DataFrame(columns=['Band Name', 'Booking Date', 'Booking Time'])
    # Write the DataFrame to a CSV file in the local file system.
    st.session_state['booking_data'].to_csv("booking_times.csv", index=False)
    # Upload the file to the S3 bucket.
    s3.Bucket('studio-booker').upload_file("booking_times.csv", "booking_times.csv")
st.session_state['booking_data']

# Create a form for booking
column1, column2 = st.columns(2)
with column1:
    with st.form('Booking Form'):
        band_name = st.text_input('Band Name')
        min_date = pd.Timestamp.today()
        max_date = min_date + pd.DateOffset(days=14)
        booking_date = st.date_input('Booking Date', min_value=min_date, max_value=max_date, format="MM.DD.YYYY")
        available_times = get_available_times(booking_date)
        if available_times:
            booking_time = st.selectbox('Booking Time', available_times)
            submit_button = st.form_submit_button('Book Now')
        else:
            st.info('No available times for this date.')
            submit_button = st.form_submit_button('Book Now', disabled=True)

        # Update the DataFrame with the booking information when the form is submitted
        if submit_button:
            new_booking = {'Band Name': band_name, 'Booking Date': booking_date, 'Booking Time': booking_time}
            st.session_state['booking_data'] = st.session_state['booking_data'].append(new_booking, ignore_index=True)

# Create a DataFrame for the next 14 days
dates = pd.date_range(start=pd.Timestamp.today(), periods=14)
booking_status = pd.DataFrame(index=dates, columns=['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']).fillna('🟢')
booking_status['Date'] = booking_status.index.strftime('%d.%m.%Y')

# This block of code is removed as it is a duplicate of the code inside the 'Booking Form'

# Iterate over the booking_data DataFrame and update the booking_status DataFrame with the booking information
for index, row in st.session_state['booking_data'].iterrows():
    booking_date_str = row['Booking Date'].strftime('%d.%m.%Y')
    booking_status.loc[booking_status['Date'] == booking_date_str, row['Booking Time']] = '🔴 - ' + row['Band Name']


with column2:
    with st.form('Remove Booking Form'):
        # Create a list of bookings in the format "Band Name - Booking Date - Booking Time"
        bookings = st.session_state['booking_data'].apply(lambda row: f"{row['Band Name']} - {row['Booking Date'].strftime('%d.%m.%Y')} - {row['Booking Time']}", axis=1).values.tolist()
        # Create a selectbox that lists all the bookings
        selected_booking = st.selectbox('Select a booking to remove', bookings)
        # Create a 'Remove Booking' button to submit the form
        remove_button = st.form_submit_button('Remove Booking')

        # Update the booking data, booking times file, and S3 bucket when the 'Remove Booking' button is clicked
        if remove_button:
            # Split the selected booking into band name, booking date, and booking time
            if selected_booking is not None:
                band_name, booking_date_str, booking_time = selected_booking.split(' - ')
                booking_date = pd.to_datetime(booking_date_str, format='%d.%m.%Y')
                # Find the booking in the booking_data DataFrame that matches the selected booking
                booking_to_remove = st.session_state['booking_data'][(st.session_state['booking_data']['Band Name'] == band_name) & (st.session_state['booking_data']['Booking Date'] == booking_date) & (st.session_state['booking_data']['Booking Time'] == booking_time)]
                # Remove the booking from the booking data DataFrame
                st.session_state['booking_data'] = st.session_state['booking_data'].drop(booking_to_remove.index)
                # Update the booking times file and the S3 bucket
                update_booking_times(st.session_state['booking_data'])
                # Update the booking status DataFrame
                booking_status = get_booking_status(st.session_state['booking_data'])
            else:
                st.warning('No booking selected.')


        # This line of code is removed from here
# Define a function to get the booking status
def get_booking_status(booking_data):
    # Create a DataFrame for the next 14 days
    dates = pd.date_range(start=pd.Timestamp.today(), periods=14)
    booking_status = pd.DataFrame(index=dates, columns=['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']).fillna('🟢')
    booking_status['Date'] = booking_status.index.strftime('%d.%m.%Y')

    # Iterate over the booking_data DataFrame and update the booking_status DataFrame with the booking information
    for index, row in booking_data.iterrows():
        booking_date_str = row['Booking Date'].strftime('%d.%m.%Y')
        booking_status.loc[booking_status['Date'] == booking_date_str, row['Booking Time']] = '🔴 - ' + row['Band Name']

    return booking_status

# Display the booking status
AgGrid(booking_status.reset_index(drop=True))
# Define a function to get the booking status
def get_booking_status(booking_data):
    # Create a DataFrame for the next 14 days
    dates = pd.date_range(start=pd.Timestamp.today(), periods=14)
    booking_status = pd.DataFrame(index=dates, columns=['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']).fillna('🟢')
    booking_status['Date'] = booking_status.index.strftime('%d.%m.%Y')

    # Iterate over the booking_data DataFrame and update the booking_status DataFrame with the booking information
    for index, row in booking_data.iterrows():
        booking_date_str = row['Booking Date'].strftime('%d.%m.%Y')
        booking_status.loc[booking_status['Date'] == booking_date_str, row['Booking Time']] = '🔴 - ' + row['Band Name']

    return booking_status
# Function to check the availability of booking times for a given date
def get_available_times(date):
    # Define the possible booking times
    times = ['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']
    # Get the bookings for the given date
    bookings_on_date = st.session_state['booking_data'][st.session_state['booking_data']['Booking Date'] == date]
    # Remove the booked times from the list of possible times
    for index, booking in bookings_on_date.iterrows():
        if booking['Booking Time'] in times:
            times.remove(booking['Booking Time'])
    return times
