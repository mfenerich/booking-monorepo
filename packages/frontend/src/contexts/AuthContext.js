import React, { createContext, useState } from 'react';
import { networkAdapter } from 'services/NetworkAdapter';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userDetails, setUserDetails] = useState(null);

  // Extract the auth check logic into its own async function
  const checkAuthStatus = async () => {
    try {
      const response = await networkAdapter.get(
        'api/v1/users/auth-user',
        {},
        { notUseMirage: true } // TODO: Remove notUseMirage
      );
      if (response && response.data) {
        setIsAuthenticated(response.data.isAuthenticated);
        setUserDetails(response.data.userDetails);
      }
    } catch (error) {
      if (error.response && error.response.status === 401) {
        setIsAuthenticated(false);
        setUserDetails(null);
      } else {
        console.error('Error checking authentication status:', error);
      }
    }
  };

  // triggerAuthCheck now returns a promise
  const triggerAuthCheck = async () => {
    await checkAuthStatus();
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, userDetails, triggerAuthCheck }}>
      {children}
    </AuthContext.Provider>
  );
};
