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
  },

  createProperty: async (payload) => {
    const response = await api.post('/properties/', payload);
    return response.data;
  },

  uploadPropertyImages: async (propertyId, files) => {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    const response = await api.post(`/properties/${propertyId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  getPropertyContact: async (propertyId) => {
    const response = await api.post(`/properties/${propertyId}/contact`);
    return response.data;
  },

  verifyProperty: async (id, status) => {
    const response = await api.put(`/properties/${id}/verify?status=${status}`);
    return response.data;
  }
};



