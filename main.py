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
    booking_time = st.time_input('Booking Time')
    submit_button = st.form_submit_button('Book Now')

    # Update the DataFrame with the booking information when the form is submitted
    if submit_button:
        new_booking = {'Band Name': band_name, 'Booking Date': booking_date, 'Booking Time': booking_time}
        booking_data = booking_data.append(new_booking, ignore_index=True)

# Define calendar options and events
calendar_options = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
    },
    "slotMinTime": "06:00:00",
    "slotMaxTime": "18:00:00",
    "initialView": "resourceTimelineDay",
    "resourceGroupField": "building",
    "resources": [
        {"id": "a", "building": "Building A", "title": "Building A"},
        {"id": "b", "building": "Building A", "title": "Building B"},
        {"id": "c", "building": "Building B", "title": "Building C"},
        {"id": "d", "building": "Building B", "title": "Building D"},
        {"id": "e", "building": "Building C", "title": "Building E"},
        {"id": "f", "building": "Building C", "title": "Building F"},
    ],
}
calendar_events = [
    {"title": "Event 1", "start": "2023-07-31T08:30:00", "end": "2023-07-31T10:30:00", "resourceId": "a",},
    {"title": "Event 2", "start": "2023-07-31T07:30:00", "end": "2023-07-31T10:30:00", "resourceId": "b",},
    {"title": "Event 3", "start": "2023-07-31T10:40:00", "end": "2023-07-31T12:30:00", "resourceId": "a",},
]

# Create and display the calendar
calendar = calendar(events=calendar_events, options=calendar_options)
st.write(calendar)

# Display the booking information
AgGrid(booking_data)
