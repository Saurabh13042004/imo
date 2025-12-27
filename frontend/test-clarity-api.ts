/**
 * Test script to validate Clarity API response structure
 * Run this in browser console to debug API issues
 */

async function testClarityAPI() {
  const CLARITY_API_ENDPOINT = import.meta.env.VITE_CLARITY_API_ENDPOINT;
  const CLARITY_TOKEN = import.meta.env.VITE_CLARITY_API_TOKEN;

  console.log('Testing Clarity API...');
  console.log('Endpoint:', CLARITY_API_ENDPOINT);
  console.log('Token exists:', !!CLARITY_TOKEN);

  if (!CLARITY_API_ENDPOINT || !CLARITY_TOKEN) {
    console.error('Missing API endpoint or token');
    return;
  }

  try {
    const params = new URLSearchParams({
      numOfDays: '1',
      dimension1: 'Device',
    });

    const url = `${CLARITY_API_ENDPOINT}?${params}`;
    console.log('Making request to:', url);

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${CLARITY_TOKEN}`,
        'Content-Type': 'application/json',
      },
    });

    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', response.status, errorText);
      return;
    }

    const data = await response.json();
    console.log('Raw API Response:', data);

    // Check structure
    if (Array.isArray(data)) {
      console.log('✓ Response is an array');
      console.log('Number of metrics:', data.length);

      data.forEach((metric: any, idx: number) => {
        console.log(`\nMetric ${idx}:`, {
          metricName: metric.metricName,
          informationLength: Array.isArray(metric.information) ? metric.information.length : 0,
          sampleInfo: metric.information?.[0],
        });
      });
    } else {
      console.error('✗ Response is not an array:', typeof data);
    }
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Run test
testClarityAPI();
