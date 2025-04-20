import streamlit as st
from datetime import datetime, date, time
import requests
import json
from streamlit.components.v1 import html

# Set page config (must be first Streamlit command)
st.set_page_config(page_title="NY Taxi Fare Estimator", page_icon="🚖", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .big-font {
        font-size:24px !important;
        font-weight: bold;
    }
    .title {
        font-size:32px !important;
        font-weight: bold;
        color: #FF5733;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #FF5733;
        color: white;
        font-weight: bold;
        width: 100%;
        padding: 10px;
        border-radius: 5px;
    }
    #map {
        height: 500px;
        width: 100%;
        margin-bottom: 20px;
        border-radius: 10px;
    }
    .mapboxgl-ctrl-geocoder {
        width: 100% !important;
        max-width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# App title
st.markdown('<p class="title">NY TAXI FARE PREDICTOR</p>', unsafe_allow_html=True)

# Initialize session state for locations
if 'pickup_coords' not in st.session_state:
    st.session_state.pickup_coords = {"lat": 40.7128, "lng": -74.0060}  # Default NYC
if 'dropoff_coords' not in st.session_state:
    st.session_state.dropoff_coords = {"lat": 40.7128, "lng": -73.9960}  # Slightly east

# Mapbox configuration
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw"
map_html = f"""
<link href="https://api.mapbox.com/mapbox-gl-js/v2.6.1/mapbox-gl.css" rel="stylesheet">
<script src="https://api.mapbox.com/mapbox-gl-js/v2.6.1/mapbox-gl.js"></script>
<script src="https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-geocoder/v4.7.2/mapbox-gl-geocoder.min.js"></script>
<link rel="stylesheet" href="https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-geocoder/v4.7.2/mapbox-gl-geocoder.css">

<div id="map"></div>
<div id="coordinates" style="display:none;"></div>

<script>
mapboxgl.accessToken = '{MAPBOX_ACCESS_TOKEN}';
const map = new mapboxgl.Map({{
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [-74.0060, 40.7128], // NYC
    zoom: 12
}});

// Add geocoder control
const geocoder = new MapboxGeocoder({{
    accessToken: mapboxgl.accessToken,
    mapboxgl: mapboxgl,
    marker: false
}});
map.addControl(geocoder);

let pickupMarker = new mapboxgl.Marker({{ color: '#FF5733' }})
    .setLngLat([{st.session_state.pickup_coords['lng']}, {st.session_state.pickup_coords['lat']}])
    .addTo(map);

let dropoffMarker = new mapboxgl.Marker({{ color: '#4287f5' }})
    .setLngLat([{st.session_state.dropoff_coords['lng']}, {st.session_state.dropoff_coords['lat']}])
    .addTo(map);

let activeMarker = 'pickup';

// UI controls
const pickupBtn = document.createElement('button');
pickupBtn.textContent = 'Set Pickup';
pickupBtn.style.margin = '10px';
pickupBtn.style.padding = '5px 10px';
pickupBtn.style.backgroundColor = '#FF5733';
pickupBtn.style.color = 'white';
pickupBtn.style.border = 'none';
pickupBtn.style.borderRadius = '3px';
pickupBtn.addEventListener('click', () => {{ activeMarker = 'pickup'; }});

const dropoffBtn = document.createElement('button');
dropoffBtn.textContent = 'Set Dropoff';
dropoffBtn.style.margin = '10px';
dropoffBtn.style.padding = '5px 10px';
dropoffBtn.style.backgroundColor = '#4287f5';
dropoffBtn.style.color = 'white';
dropoffBtn.style.border = 'none';
dropoffBtn.style.borderRadius = '3px';
dropoffBtn.addEventListener('click', () => {{ activeMarker = 'dropoff'; }});

map.addControl(new mapboxgl.NavigationControl());
map.addControl(new mapboxgl.FullscreenControl());

const markerControls = document.createElement('div');
markerControls.style.position = 'absolute';
markerControls.style.top = '10px';
markerControls.style.right = '10px';
markerControls.style.zIndex = '1';
markerControls.appendChild(pickupBtn);
markerControls.appendChild(dropoffBtn);
map.getContainer().appendChild(markerControls);

// Handle map clicks
map.on('click', (e) => {{
    const coords = e.lngLat;

    if (activeMarker === 'pickup') {{
        pickupMarker.setLngLat(coords);
        document.getElementById('coordinates').textContent = JSON.stringify({{
            type: 'pickup',
            lat: coords.lat,
            lng: coords.lng
        }});
    }} else {{
        dropoffMarker.setLngLat(coords);
        document.getElementById('coordinates').textContent = JSON.stringify({{
            type: 'dropoff',
            lat: coords.lat,
            lng: coords.lng
        }});
    }}

    // Send coordinates to Streamlit
    window.parent.document.dispatchEvent(new CustomEvent('mapClick', {{
        detail: {{
            type: activeMarker,
            lat: coords.lat,
            lng: coords.lng
        }}
    }}));
}});

// Handle geocoder result
geocoder.on('result', (e) => {{
    const coords = e.result.center;

    if (activeMarker === 'pickup') {{
        pickupMarker.setLngLat(coords);
        document.getElementById('coordinates').textContent = JSON.stringify({{
            type: 'pickup',
            lat: coords[1],
            lng: coords[0]
        }});
    }} else {{
        dropoffMarker.setLngLat(coords);
        document.getElementById('coordinates').textContent = JSON.stringify({{
            type: 'dropoff',
            lat: coords[1],
            lng: coords[0]
        }});
    }}

    // Send coordinates to Streamlit
    window.parent.document.dispatchEvent(new CustomEvent('mapClick', {{
        detail: {{
            type: activeMarker,
            lat: coords[1],
            lng: coords[0]
        }}
    }}));
}});
</script>
"""

# Display the map
html(map_html, height=550)

# JavaScript to handle map clicks
html("""
<script>
window.addEventListener('load', function() {
    window.parent.document.addEventListener('mapClick', function(e) {
        const data = e.detail;
        window.streamlitApi.setComponentValue(data);
    });
});
</script>
""")

# Update coordinates from map clicks
if 'map_click' in st.session_state:
    click_data = st.session_state.map_click
    if click_data['type'] == 'pickup':
        st.session_state.pickup_coords = {"lat": click_data['lat'], "lng": click_data['lng']}
    elif click_data['type'] == 'dropoff':
        st.session_state.dropoff_coords = {"lat": click_data['lat'], "lng": click_data['lng']}

# Display coordinates (read-only)
col1, col2 = st.columns(2)
with col1:
    st.markdown('<p class="big-font">Pickup Location</p>', unsafe_allow_html=True)
    st.text_input("Pickup Latitude", value=st.session_state.pickup_coords['lat'], key="pickup_lat", disabled=True)
    st.text_input("Pickup Longitude", value=st.session_state.pickup_coords['lng'], key="pickup_lng", disabled=True)

with col2:
    st.markdown('<p class="big-font">Drop-off Location</p>', unsafe_allow_html=True)
    st.text_input("Dropoff Latitude", value=st.session_state.dropoff_coords['lat'], key="dropoff_lat", disabled=True)
    st.text_input("Dropoff Longitude", value=st.session_state.dropoff_coords['lng'], key="dropoff_lng", disabled=True)

# Date and time input
col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input(
        "Pickup date",
        value=date.today(),
        min_value=date.today()
    )
with col_time:
    selected_time = st.time_input(
        "Pickup time",
        value=time(11, 42, 6)
    )

# Combine date and time
selected_datetime = datetime.combine(selected_date, selected_time)

# Passenger count
passenger_count = st.selectbox("Number of passengers", [1, 2, 3, 4, 5, 6, 7, 8], index=0)

# API URL
url = 'https://taxifare.lewagon.ai/predict'

# Fare estimate button
if st.button("Get fare prediction", type="primary"):
    # Prepare API parameters
    params = {
        "pickup_datetime": selected_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "pickup_longitude": st.session_state.pickup_coords['lng'],
        "pickup_latitude": st.session_state.pickup_coords['lat'],
        "dropoff_longitude": st.session_state.dropoff_coords['lng'],
        "dropoff_latitude": st.session_state.dropoff_coords['lat'],
        "passenger_count": passenger_count
    }

    try:
        # Make API request
        response = requests.get(url, params=params)
        prediction = response.json().get('fare', 0)

        # Display prediction
        st.success(f"### Predicted Fare: ${prediction:.2f}")

    except Exception as e:
        st.error(f"Error getting prediction: {e}")
        st.markdown('''
            **Note:** If you want to use your own API instead of Le Wagon's,
            replace the URL variable with your API endpoint.
            ''')

# JavaScript to update Streamlit
html("""
<script>
window.streamlitApi = {
    setComponentValue: (value) => {
        const data = JSON.stringify(value);
        parent.window.postMessage({
            type: 'streamlit:setComponentValue',
            data: data
        }, '*');
    }
}

window.addEventListener('message', (event) => {
    if (event.data.type === 'streamlit:setComponentValue') {
        const data = JSON.parse(event.data.data);
        Streamlit.setComponentValue(data);
    }
});
</script>
""")
