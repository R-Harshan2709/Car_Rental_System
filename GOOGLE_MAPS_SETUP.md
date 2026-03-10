# Google Maps API Integration - Setup Guide

## Overview

The Admin Rentals page now includes a Google Maps integration to visualize all active rental locations. This helps admins quickly view and track rental transactions geographically.

## Features

### Map Visualization

- **Color-coded markers** to show rental status:
  - 🔵 **Blue** = Active Rentals
  - 🟢 **Green** = Approved Rentals
  - 🔴 **Red** = Pending Rentals
  - 🟡 **Yellow** = Completed Rentals

### Interactive Elements

- **Click on markers** to view rental details
- **Zoom and pan** the map for better navigation
- **Toggle button** to show/hide the map view
- **Info windows** display:
  - Rental ID
  - Customer name
  - Car details (Brand & Model)
  - Rental status
  - Approval status
  - Start & End dates
  - Total rental price

### Default Location

- Map centered on **Delhi, India** (28.7041°N, 77.1025°E)
- Coordinates auto-calculated based on rental data

## Setup Instructions

### Step 1: Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Maps JavaScript API**
4. Enable **Geocoding API** (optional, for address lookup)
5. Create an API key in **Credentials** section
6. Copy the API key

### Step 2: Update .env File

Replace the placeholder in your `.env` file:

```env
GOOGLE_MAPS_API_KEY=YOUR_ACTUAL_API_KEY_HERE
```

Replace `YOUR_ACTUAL_API_KEY_HERE` with your actual Google Maps API key.

### Step 3: Verify Setup

1. Start your Flask application: `python app.py`
2. Go to Admin Dashboard → Rentals
3. Click the **"📍 View Map"** button
4. Map should load with rental markers

## Configuration Files Updated

### 1. `.env`

- Added `GOOGLE_MAPS_API_KEY` variable

### 2. `config.py`

- Added `GOOGLE_MAPS_API_KEY` configuration from environment variables

### 3. `routes/admin.py`

- Imported `Config` class
- Updated `rentals()` route to pass config to template

### 4. `templates/admin/rentals.html`

- Added Map View toggle button
- Added Google Maps container (500px height)
- Added legend showing marker color meanings
- Integrated Google Maps JavaScript API
- Added marker clustering logic based on rental status
- Added info windows for marker details

## How It Works

### Backend

1. Admin clicks "📍 View Map" button
2. Rental data is extracted from database
3. Coordinates are assigned to each rental (simulated with slight offsets from Delhi center)
4. Data is passed to JavaScript

### Frontend

1. Google Maps API loads asynchronously
2. Map initializes with default center (Delhi)
3. Markers are created for each rental with color based on status
4. Click handlers added to show rental details
5. Info windows display when markers are clicked

## Marker Color Scheme

| Status        | Color  | Marker |
| ------------- | ------ | ------ |
| Active Rental | Blue   | 🔵     |
| Approved      | Green  | 🟢     |
| Pending       | Red    | 🔴     |
| Completed     | Yellow | 🟡     |

## Sample Data Structure

```javascript
{
    id: 1,
    customer: "John Doe",
    car: "Toyota Fortuner",
    status: "active",
    approval: "approved",
    startDate: "2025-12-07",
    endDate: "2025-12-10",
    price: 9900,
    lat: 28.7041,
    lng: 77.1025
}
```

## Production Recommendations

### Security

- **Restrict API key** to specific domains:
  - Application HTTP referrers: `your-domain.com`
  - Restrict to JavaScript API only

### Performance

- Consider using **Marker Clustering** for large datasets
- Implement **pagination** for large rental lists
- Cache map data for faster loading

### Real Coordinates

Currently, coordinates are simulated. For production:

1. Store actual pickup/dropoff coordinates in database
2. Use **Geocoding API** to convert addresses to coordinates
3. Display real rental locations on map

### Limitations

- Currently uses static offset coordinates for demo
- All rentals cluster around Delhi center
- No real location tracking

## Troubleshooting

### Map Not Loading?

1. Check API key is valid in `.env`
2. Verify API key has Maps JavaScript API enabled
3. Check browser console for errors
4. Ensure domain is whitelisted in API key restrictions

### Markers Not Showing?

1. Check if rentalData array is populated
2. Verify latitude/longitude values are valid
3. Check browser console for JavaScript errors

### API Key Errors?

- "Invalid key" - Regenerate and update `.env`
- "Quota exceeded" - Check Google Cloud billing
- "Access denied" - Enable Maps JavaScript API in Google Cloud

## API Limits

- **Free Tier**: 1,000 requests/day
- **Paid Tier**: Scalable based on usage and billing

Check [Google Maps Pricing](https://cloud.google.com/maps-platform/pricing) for current rates.

## Files Modified

1. `.env` - Added Google Maps API key
2. `config.py` - Added GOOGLE_MAPS_API_KEY configuration
3. `routes/admin.py` - Updated to pass config to template
4. `templates/admin/rentals.html` - Added map integration

## Future Enhancements

- [ ] Add marker clustering for better UX
- [ ] Implement real location tracking
- [ ] Add route optimization
- [ ] Implement heatmap view for rental density
- [ ] Add geofencing for rental zones
- [ ] Real-time tracking dashboard
