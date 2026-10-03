import api from './api';

export const subscriptionService = {
  // Get public gateway configuration and plan information
  getConfig: async () => {
    const res = await api.get('/subscriptions/config');
    return res.data;
  },

  // Get authenticated user's current subscription status and dates
  getMySubscription: async () => {
    const res = await api.get('/subscriptions/me');
    return res.data;
  },

  // Initiate an order on the backend with server-enforced amount
  createOrder: async () => {
    const res = await api.post('/subscriptions/create-order');
    return res.data;
  },

  // Verify payment cryptographically with Razorpay HMAC signature on the backend
  verifyPayment: async ({ razorpay_order_id, razorpay_payment_id, razorpay_signature }) => {
    const res = await api.post('/subscriptions/verify-payment', {
      razorpay_order_id,
      razorpay_payment_id,
      razorpay_signature
    });
    return res.data;
  },

  // Cancel an active subscription
  cancelSubscription: async () => {
    const res = await api.post('/subscriptions/cancel');
    return res.data;
  },

  // Admin: list all user subscriptions and statuses
  getAdminSubscriptions: async () => {
    const res = await api.get('/admin/subscriptions');
    return res.data;
  }
};
