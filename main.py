# Import necessary libraries
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

# Create a pandas DataFrame to store the booking information
booking_data = pd.DataFrame(columns=['Band Name', 'Booking Date', 'Booking Time'])

# Create a Streamlit app
st.title('Band Studio Booking')

# Import the streamlit_calendar package
import streamlit_calendar

# Create an interactive calendar widget
booking_date = streamlit_calendar.st_calendar()

# Create a form for booking
with st.form('Booking Form'):
    band_name = st.text_input('Band Name')
    booking_time = st.time_input('Booking Time')
    submit_button = st.form_submit_button('Book Now')

    # Update the DataFrame with the booking information when the form is submitted
    if submit_button:
        new_booking = {'Band Name': band_name, 'Booking Date': booking_date, 'Booking Time': booking_time}
        booking_data = booking_data.append(new_booking, ignore_index=True)

# Display the booking information
AgGrid(booking_data)
