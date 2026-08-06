import api from './api';

export const propertyService = {

  getProperties: async (params = {}) => {
    const response = await api.get('/properties/', { params });
    return response.data;
  },

  getPropertyById: async (id) => {
    const response = await api.get(`/properties/${id}`);
    return response.data;
  },

  deleteProperty: async (id) => {
    const response = await api.delete(`/properties/${id}`);
    return response.data;
  }
};
