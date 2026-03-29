const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://api.realms2riches.com";
const ANALYTICS_ENABLED = import.meta.env.VITE_ANALYTICS_ENABLED === 'true';

// Thin abstraction layer for event tracking
export const trackEvent = async (eventName, payload = {}) => {
  // Console logging for development
  console.log(`[Analytics] ${eventName}`, payload);
  
  if (!ANALYTICS_ENABLED) return;

  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/analytics/event`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        event_type: eventName,
        product_id: payload.product_id,
        campaign_id: payload.campaign_id,
        user_id: payload.user_id,
        details: payload
      })
    });
    if (!res.ok) console.warn("Failed to send analytics event to backend");
  } catch (err) {
    console.error("Analytics network error:", err);
  }
};