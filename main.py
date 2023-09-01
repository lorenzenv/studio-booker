# Import necessary libraries
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from streamlit_calendar import calendar

# Create a pandas DataFrame to store the booking information
booking_data = pd.DataFrame(columns=['Band Name', 'Booking Date', 'Booking Time'])

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
booking_status = pd.DataFrame(index=dates, columns=['Tagsüber (bis 19 Uhr)', 'Abends (ab 19 Uhr)']).fillna(False)
booking_status['Date'] = booking_status.index
booking_status['Date'] = pd.to_datetime(booking_status['Date']).dt.strftime('%d.%m.%Y')

# Update the DataFrame with the booking information when the form is submitted
if submit_button:
    new_booking = {'Band Name': band_name, 'Booking Date': booking_date, 'Booking Time': booking_time}
    booking_data = booking_data.append(new_booking, ignore_index=True)
    booking_date_str = booking_date.strftime('%d.%m.%Y')
    booking_status.loc[booking_status['Date'] == booking_date_str, booking_time] = True

# Display the booking status
AgGrid(booking_status.reset_index(drop=True))
