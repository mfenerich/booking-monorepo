class NetworkAdapter {
  static #API_CONFIG = {
    MIRAGE: window.location.origin,
    EXPRESS: 'http://localhost:4000',
    USER_API: 'http://localhost:8000',
    HOTEL_API: 'http://localhost:8001'
  };
  
  // Helper to determine the appropriate API based on the endpoint
  #determineApiBaseUrl(endpoint, options = {}) {
    // If a specific API is explicitly requested, use it
    if (options.useApi && NetworkAdapter.#API_CONFIG[options.useApi]) {
      return NetworkAdapter.#API_CONFIG[options.useApi];
    }
    
    // Use Mirage in development unless specifically asked not to
    if (!options.notUseMirage) {
      return NetworkAdapter.#API_CONFIG.MIRAGE;
    }
    
    // Auto-detect which API to use based on the endpoint
    const hotelEndpoints = ['/api/v1/hotel', '/api/hotels', '/api/v1/availableCities', 
                          '/api/v1/nearbyHotels', '/api/v1/popularDestinations', 'api/v1/hotels/verticalFilters']; // TODO: improve way to detect hotel and other endpoints types
    
    // Use hotel API if endpoint matches any hotel endpoint pattern
    for (const pattern of hotelEndpoints) {
      if (endpoint.startsWith(pattern)) {
        return NetworkAdapter.#API_CONFIG.HOTEL_API;
      }
    }
    
    // Default to user API for all other endpoints
    return NetworkAdapter.#API_CONFIG.USER_API;
  }

  // Add endpoint version prefix if needed
  #ensureVersionPrefix(endpoint, baseUrl) {
    // For real APIs, make sure v1 is included for consistency
    if (baseUrl === NetworkAdapter.#API_CONFIG.USER_API || 
        baseUrl === NetworkAdapter.#API_CONFIG.HOTEL_API) {
      // If endpoint doesn't already have /v1/ and starts with /api/
      if (!endpoint.includes('/v1/') && endpoint.startsWith('/api/')) {
        return endpoint.replace('/api/', '/api/v1/');
      }
    }
    return endpoint;
  }
  
  async get(endpoint, params = {}, options = {}) {
    // Determine which API to use
    const baseUrl = this.#determineApiBaseUrl(endpoint, options);
    
    // Ensure endpoint has version prefix if needed
    const versionedEndpoint = this.#ensureVersionPrefix(endpoint, baseUrl);
    
    console.log(`Fetching from ${baseUrl}${versionedEndpoint}`);
    
    const url = new URL(versionedEndpoint, baseUrl);
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  
    const response = await fetch(url.toString(), {
      credentials: 'include',
      headers: options.headers || {},
    });
    
    const json = await response.json();
  
    if (!response.ok) {
      const error = new Error('Network response was not ok');
      error.response = { status: response.status, data: json };
      throw error;
    }
    
    return json;
  }  

  async post(endpoint, data = {}, options = {}) {
    try {
      const baseUrl = this.#determineApiBaseUrl(endpoint, options);
      const versionedEndpoint = this.#ensureVersionPrefix(endpoint, baseUrl);
      const url = new URL(versionedEndpoint, baseUrl);
      
      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {})
        },
        body: JSON.stringify(data),
        credentials: 'include',
      });

      return await response.json();
    } catch (error) {
      return {
        data: {},
        errors: [error.message],
      };
    }
  }

  async put(endpoint, data = {}, options = {}) {
    try {
      const baseUrl = this.#determineApiBaseUrl(endpoint, options);
      const versionedEndpoint = this.#ensureVersionPrefix(endpoint, baseUrl);
      const url = new URL(versionedEndpoint, baseUrl);
      
      const response = await fetch(url.toString(), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {})
        },
        body: JSON.stringify(data),
        credentials: 'include',
      });

      return await response.json();
    } catch (error) {
      return {
        data: {},
        errors: [error.message],
      };
    }
  }

  async delete(endpoint, options = {}) {
    try {
      const baseUrl = this.#determineApiBaseUrl(endpoint, options);
      const versionedEndpoint = this.#ensureVersionPrefix(endpoint, baseUrl);
      const url = new URL(versionedEndpoint, baseUrl);
      
      const response = await fetch(url.toString(), {
        method: 'DELETE',
        headers: options.headers || {},
        credentials: 'include',
      });

      return await response.json();
    } catch (error) {
      return {
        data: {},
        errors: [error.message],
      };
    }
  }

  async patch(endpoint, data = {}, options = {}) {
    try {
      const baseUrl = this.#determineApiBaseUrl(endpoint, options);
      const versionedEndpoint = this.#ensureVersionPrefix(endpoint, baseUrl);
      const url = new URL(versionedEndpoint, baseUrl);
      
      const response = await fetch(url.toString(), {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {})
        },
        body: JSON.stringify(data),
        credentials: 'include',
      });

      return await response.json();
    } catch (error) {
      return {
        data: {},
        errors: [error.message],
      };
    }
  }
}

export const networkAdapter = new NetworkAdapter();
