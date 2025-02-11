# 🌍 Coastal Landscape Pattern Analysis using Google Earth Engine 🌊

## 📌 Project Overview
This project analyzes **coastal landscape patterns** using **Google Earth Engine (GEE)** and **Landsat satellite imagery**.  
It classifies land cover types such as **water bodies, vegetation, urban areas, and wetlands**, helping in **coastal monitoring, ecosystem protection, and urban planning**.

The project features a **Streamlit web app** where users can **select a region on an interactive map**, analyze **historical land cover changes**, and get a **classified visualization** along with an **insightful summary**.

---

## 🚀 Features
✅ **Interactive Map Selection** – Users can draw a region on the map for analysis.  
✅ **Automated Data Processing** – Fetches Landsat images, applies cloud masking, and classifies land cover.  
✅ **Coastal Pattern Classification** – Identifies water, vegetation, urban, and wetland areas.  
✅ **Dynamic Summary Generation** – Provides an **insightful report** instead of raw pixel statistics.  
✅ **Error Handling & Logging** – Prevents crashes and logs issues for debugging.  
✅ **Supports Multiple Timeframes** – Analyze coastal changes from **1984 to 2024**.  
✅ **Google Earth Engine Integration** – Uses **GEE API** for large-scale geospatial analysis.

---

## 🛠️ Installation & Setup
### **1️⃣ Prerequisites**
Ensure you have the following installed:
- **Python 3.8 or later**  
- **pip** (Python Package Installer)  
- **Google Earth Engine API (GEE)**  
- **Streamlit** (for the web app)  
- **Folium** (for interactive mapping)  
- **geemap** (for GEE integration)  

### **2️⃣ Clone the Repository**
```bash
git clone https://github.com/Vilas8/coastal-landscape-analysis.git
cd coastal-landscape-analysis
