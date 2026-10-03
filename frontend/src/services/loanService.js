import api from './api';

export const loanService = {
  // Fetch list of verified Indian bank loan products
  getBanks: async () => {
    const response = await api.get('/loans/banks');
    return response.data;
  },

  // Calculate simple EMI for specific amount, rate, and tenure
  calculateLoan: async (calculationData) => {
    const response = await api.post('/loans/calculate', calculationData);
    return response.data;
  },

  // Run comprehensive multi-bank comparison with indicative eligibility
  compareLoans: async (comparisonData) => {
    const response = await api.post('/loans/compare', comparisonData);
    return response.data;
  },

  // Download high-fidelity PDF mortgage report
  downloadReportPdf: async (comparisonData, propertyId) => {
    const response = await api.post('/loans/report', comparisonData, {
      responseType: 'blob',
    });
    
    // Create blob link and trigger download
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `GeoSmart_Home_Loan_Report_Prop_${propertyId || 'General'}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    return true;
  },
};

export default loanService;
