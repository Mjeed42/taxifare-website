import streamlit as st
import requests

'''
# TaxiFareModel front
'''

st.markdown('''
Remember that there are several ways to output content into your web page...

Either as with the title by just creating a string (or an f-string). Or as with this paragraph using the `st.` functions
''')

'''
## Here we would like to add some controllers in order to ask the user to select the parameters of the ride

1. Let's ask for:
- date and time
- pickup longitude
- pickup latitude
- dropoff longitude
- dropoff latitude
- passenger count
'''

# Input fields for user to provide ride details
st.sidebar.header("Ride Parameters")
pickup_datetime = st.sidebar.text_input("Date and time (YYYY-MM-DD HH:MM:SS)", "2023-01-01 12:00:00")
pickup_longitude = st.sidebar.number_input("Pickup longitude", value=0.0)
pickup_latitude = st.sidebar.number_input("Pickup latitude", value=0.0)
dropoff_longitude = st.sidebar.number_input("Dropoff longitude", value=0.0)
dropoff_latitude = st.sidebar.number_input("Dropoff latitude", value=0.0)
passenger_count = st.sidebar.number_input("Passenger count", min_value=1, max_value=8, value=1)

'''
## Once we have these, let's call our API in order to retrieve a prediction

See ? No need to load a `model.joblib` file in this app, we do not even need to know anything about Data Science in order to retrieve a prediction...

🤔 How could we call our API ? Off course... The `requests` package 💡
'''

url = 'https://taxifare.lewagon.ai/predict'

if url == 'https://taxifare.lewagon.ai/predict':
    st.markdown('Maybe you want to use your own API for the prediction, not the one provided by Le Wagon...')

'''
2. Let's build a dictionary containing the parameters for our API...

3. Let's call our API using the `requests` package...

4. Let's retrieve the prediction from the **JSON** returned by the API...

## Finally, we can display the prediction to the user
'''

# Build the dictionary for the API request
params = {
    "pickup_datetime": pickup_datetime,
    "pickup_longitude": pickup_longitude,
    "pickup_latitude": pickup_latitude,
    "dropoff_longitude": dropoff_longitude,
    "dropoff_latitude": dropoff_latitude,
    "passenger_count": passenger_count
}

# Call the API and retrieve the prediction
if st.sidebar.button("Get Fare Prediction"):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        prediction = response.json().get("fare", "No prediction available")
        st.success(f"Predicted Fare: ${prediction}")
    else:
        st.error("Error: Unable to fetch prediction. Please check your inputs or try again later.")
