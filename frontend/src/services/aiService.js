import api from './api';

export const aiService = {
  analyzeProperty: async (id) => {
    const response = await api.get(`/ai/analyze-property/${id}`);
    return response.data;
  },

  downloadPdfReport: async (id) => {
    const response = await api.get(`/ai/property-report/${id}/pdf`, {
      responseType: 'blob',
    });
    
    // Trigger browser file download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `PropPulse_AI_Report_${id}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
};
