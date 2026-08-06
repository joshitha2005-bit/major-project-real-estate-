import api from './api';

export const locationService = {
  searchLocation: async (query) => {
    const response = await api.get('/location/search-location', {
      params: { query }
    });
    return response.data;
  },

  reverseGeocode: async (lat, lon) => {
    const response = await api.get('/location/reverse-geocode', {
      params: { lat, lon }
    });
    return response.data;
  },

  getNearbyPlaces: async (lat, lon, radius = 5000) => {
    const response = await api.get('/location/nearby-places', {
      params: { lat, lon, radius }
    });
    return response.data;
  },

  getLocalityStats: async (locality, lat = null, lon = null) => {
    const response = await api.get('/location/locality-stats', {
      params: { locality, lat, lon }
    });
    return response.data;
  },

  getCurrentLocation: async (lat, lon) => {
    const response = await api.get('/location/reverse-geocode', {
      params: { lat, lon }
    });
    return response.data;
  },

  getSearchHistory: async (limit = 10) => {
    const response = await api.get('/location/history', {
      params: { limit }
    });
    return response.data;
  },

  getSavedLocations: async () => {
    const response = await api.get('/location/saved-locations');
    return response.data;
  },

  saveLocation: async (locationData) => {
    const response = await api.post('/location/save-location', locationData);
    return response.data;
  },

  deleteSavedLocation: async (id) => {
    const response = await api.delete(`/location/saved-locations/${id}`);
    return response.data;
  }
};
