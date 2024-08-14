// src/api.js

const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const fetchQuery = async (query) => {
  try {
    const response = await fetch(`${apiUrl}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching query:', error);
    throw error;
  }
};