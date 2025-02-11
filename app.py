import streamlit as st
from streamlit_folium import st_folium
import folium
import ee
import geemap.foliumap as geemap
import pandas as pd
import time

# Authenticate and initialize GEE
try:
    ee.Initialize(project='coastal-analysis-2k25')
except ee.EEException:
    st.error("Google Earth Engine authentication required!")
    st.stop()

st.title("Coastal Landscape Pattern Analysis")

# Define the map
m = folium.Map(location=[31.0, 121.0], zoom_start=10)

# Function to get Landsat collection for a given period and location
def get_landsat_collection(geometry, start_year, end_year):
    return ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterBounds(geometry) \
        .filterDate(f'{start_year}-01-01', f'{end_year}-12-31') \
        .map(mask_clouds)

# Improved cloud masking function
def mask_clouds(image):
    qa = image.select('QA_PIXEL')
    cloud_mask = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
    return image.updateMask(cloud_mask.Not())

# Function to generate training data (Land cover classification)
def get_training_data():
    landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").filterDate('2020-01-01', '2020-12-31').median()
    bands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']

    water = ee.Geometry.Rectangle([-80.0, 25.0, -79.5, 25.5])  # Coastal Water
    sand = ee.Geometry.Rectangle([-80.5, 25.5, -80.0, 26.0])   # Coastal Sand
    vegetation = ee.Geometry.Rectangle([-81.0, 26.0, -80.5, 26.5])  # Coastal Vegetation
    urban = ee.Geometry.Rectangle([-81.5, 26.5, -81.0, 27.0])   # Urban Areas

    water_samples = landsat.select(bands).sample(region=water, scale=30, numPixels=100).map(lambda f: f.set('landcover', 0))
    sand_samples = landsat.select(bands).sample(region=sand, scale=30, numPixels=100).map(lambda f: f.set('landcover', 1))
    vegetation_samples = landsat.select(bands).sample(region=vegetation, scale=30, numPixels=100).map(lambda f: f.set('landcover', 2))
    urban_samples = landsat.select(bands).sample(region=urban, scale=30, numPixels=100).map(lambda f: f.set('landcover', 3))

    return water_samples.merge(sand_samples).merge(vegetation_samples).merge(urban_samples)

# Function to classify an image
def classify_image(image):
    bands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']
    training_data = get_training_data()

    try:
        classifier = ee.Classifier.smileRandomForest(10).train(
            features=training_data,
            classProperty='landcover',
            inputProperties=bands
        )
        return image.select(bands).classify(classifier)
    except Exception as e:
        st.error(f"Classification Error: {e}")
        return None

# Function to export to Google Drive
def export_to_drive(image, region):
    """Exports the classified image with colors to Google Drive."""

    # Define visualization parameters for coastal classification
    vis_params = {
        'min': 0,
        'max': 3,
        'palette': ['#0000FF',  # Water (Blue)
                    '#FFD700',  # Sand (Golden Yellow)
                    '#008000',  # Vegetation (Green)
                    '#FF0000']  # Urban (Red)
    }

    # Apply visualization
    colored_image = image.visualize(**vis_params)

    # Export the colored image
    task = ee.batch.Export.image.toDrive(
        image=colored_image,
        description="coastal_classification",
        folder="GEE_Exports",
        fileNamePrefix="coastal_classified",
        region=region,
        scale=30,
        fileFormat="GeoTIFF"
    )
    task.start()

    st.write("Exporting **coastal classified image** to Google Drive. Please wait...")

    while task.active():
        st.write(f"Task status: {task.status()['state']}...")
        time.sleep(10)  # Check every 10 seconds

    st.success("Export complete! Download `coastal_classified.tif` from Google Drive (GEE_Exports folder).")

# Streamlit sidebar controls
st.sidebar.header("Analysis Parameters")
start_year = st.sidebar.selectbox("Start Year", range(1984, 2024))
end_year = st.sidebar.selectbox("End Year", range(1984, 2024))
analyze_btn = st.sidebar.button("Analyze Selected Region")

# Draw polygon tool on the map
m = folium.Map(location=[20.593684, 78.96288], zoom_start=6)
draw = folium.plugins.Draw(draw_options={'polygon': True, 'rectangle': True}, export=True)
draw.add_to(m)
map_output = st_folium(m, width=700, height=500)

# Process user selection
if analyze_btn:
    if map_output and 'last_active_drawing' in map_output and map_output['last_active_drawing']:
        try:
            drawn_geojson = map_output['last_active_drawing']
            if 'geometry' not in drawn_geojson or not drawn_geojson['geometry']:
                st.error("Invalid drawn region! Please draw again.")
                st.stop()

            geometry_type = drawn_geojson['geometry']['type']
            coordinates = drawn_geojson['geometry']['coordinates']

            if geometry_type == 'Polygon':
                ee_geometry = ee.Geometry.Polygon(coordinates)
            else:
                st.error("Unsupported geometry type! Please draw a polygon.")
                st.stop()

            # Get satellite images and classify them
            collection = get_landsat_collection(ee_geometry, start_year, end_year)
            median_image = collection.median()
            classified_image = classify_image(median_image)

            if classified_image:
                st.write("### Classified Image Preview")
                map_display = geemap.Map(height="500px")
                vis_params = {
                    'min': 0,
                    'max': 3,
                    'palette': ['#0000FF', '#FFD700', '#008000', '#FF0000']
                }
                map_display.addLayer(classified_image, vis_params, "Coastal Classification")
                map_display.to_streamlit()
                
                export_to_drive(classified_image, ee_geometry)
            else:
                st.error("Classification failed. Please check input data.")

        except Exception as e:
            st.error(f"Error processing request: {str(e)}")
    else:
        st.warning("Please draw a region on the map first!")
