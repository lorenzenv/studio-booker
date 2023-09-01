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
    booking_data = conn.read("studio-booker/booking_times.csv", input_format="csv", ttl=600)
except FileNotFoundError:
    booking_data = pd.DataFrame(columns=['Band Name', 'Booking Date', 'Booking Time'])
    # Write the DataFrame to a CSV file in the local file system.
    booking_data.to_csv("booking_times.csv", index=False)
    # Upload the file to the S3 bucket.
    s3.Bucket('studio-booker').upload_file("booking_times.csv", "booking_times.csv")
booking_data

# Create a form for booking
with st.form('Booking Form'):
    band_name = st.text_input('Band Name')
    booking_date = st.date_input('Booking Date')
    booking_time = st.selectbox('Booking Time', ['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)'])
    submit_button = st.form_submit_button('Book Now')

    # Update the DataFrame with the booking information when the form is submitted
    if submit_button:
        new_booking = {'Band Name': band_name, 'Booking Date': booking_date, 'Booking Time': booking_time}
        booking_data = booking_data.append(new_booking, ignore_index=True)

# Create a DataFrame for the next 14 days
dates = pd.date_range(start=pd.Timestamp.today(), periods=14)
booking_status = pd.DataFrame(index=dates, columns=['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']).fillna('🟢')
booking_status['Date'] = booking_status.index.strftime('%d.%m.%Y')

# Update the DataFrame with the booking information when the form is submitted
if submit_button:
    new_booking = {'Band Name': band_name, 'Booking Date': booking_date, 'Booking Time': booking_time}
    booking_data = booking_data.append(new_booking, ignore_index=True)
    booking_date_str = booking_date.strftime('%d.%m.%Y')
    booking_status.loc[booking_status['Date'] == booking_date_str, booking_time] = '🔴 - ' + band_name

# Display the booking status
AgGrid(booking_status.reset_index(drop=True))
