# Google Maps API Setup Guide

## Overview
This application now includes location functionality for groups using the Google Maps API. Users can select locations on a map when creating or modifying groups.

## Setup Instructions

### 1. Get a Google Maps API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Places API
   - Geocoding API
4. Go to "Credentials" and create an API key
5. Restrict the API key to your domain for security

### 2. Update the API Key

Replace `YOUR_GOOGLE_MAPS_API_KEY` in the following files with your actual API key:

- `templates/groups_add.html` (line with Google Maps API script)
- `templates/modify_group.html` (line with Google Maps API script)

### 3. Database Migration

Run the SQL migration to add location columns to the collection table:

```sql
-- Run this SQL script in your database
ALTER TABLE collection 
ADD COLUMN latitude DECIMAL(10, 8) NULL,
ADD COLUMN longitude DECIMAL(11, 8) NULL,
ADD COLUMN location_name VARCHAR(255) NULL,
ADD COLUMN location_address TEXT NULL;

-- Add indexes for location queries
CREATE INDEX idx_collection_location ON collection(latitude, longitude);
CREATE INDEX idx_collection_location_name ON collection(location_name);
```

## Features

### Location Selection
- **Interactive Map**: Click anywhere on the map to set a location
- **Search Box**: Type an address or place name to search and select
- **Reverse Geocoding**: Automatically fills in the address when clicking on the map
- **Location Name**: Optional field for custom location names
- **Address Field**: Automatically populated with the full address

### Data Storage
- **Latitude/Longitude**: Precise coordinates stored as decimal values
- **Location Name**: Custom name for the location (optional)
- **Address**: Full formatted address (optional)

### Security
- API key should be restricted to your domain
- Location data is stored securely in the database
- Only authenticated users can access location features

## Usage

1. **Creating a Group**: 
   - Fill in the basic group information
   - Use the map to select a location or search for an address
   - The location data will be automatically saved with the group

2. **Modifying a Group**:
   - Existing location data will be displayed on the map
   - You can update the location by clicking on the map or searching
   - Changes are saved when you submit the form

## Troubleshooting

### Map Not Loading
- Check that your API key is correct
- Ensure the Maps JavaScript API is enabled
- Check browser console for any JavaScript errors

### Search Not Working
- Verify the Places API is enabled
- Check that the API key has the Places API permission

### Location Not Saving
- Check that the database migration has been run
- Verify the form fields are being submitted correctly
- Check server logs for any database errors

## Cost Considerations

Google Maps API has usage limits and costs:
- Free tier: $200 monthly credit
- Typical usage for this application: Very low cost
- Monitor usage in Google Cloud Console
- Consider setting up billing alerts

## Security Best Practices

1. **API Key Restrictions**:
   - Restrict to your domain only
   - Enable only necessary APIs
   - Monitor usage regularly

2. **Data Privacy**:
   - Location data is stored locally
   - No location data is shared with Google beyond API calls
   - Users control their own location data

## Support

If you encounter issues:
1. Check the browser console for JavaScript errors
2. Verify API key and enabled services
3. Check database connection and migration status
4. Review server logs for backend errors 