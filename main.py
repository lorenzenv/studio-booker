# Import necessary libraries
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from streamlit_calendar import calendar

# Read in data from the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url, on_bad_lines="skip")

# Load the booking data from the Google Sheet
sheets_url = st.secrets["public_gsheets_url"]
booking_data = load_data(sheets_url)

booking_data

# Create a Streamlit app
st.title('Band Studio Booking')

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
    # Write the updated DataFrame back to the Google Sheet
    booking_data.to_csv(sheets_url, index=False)
    booking_date_str = booking_date.strftime('%d.%m.%Y')
    booking_status.loc[booking_status['Date'] == booking_date_str, booking_time] = '🔴 - ' + band_name

# Display the booking status
AgGrid(booking_status.reset_index(drop=True))
