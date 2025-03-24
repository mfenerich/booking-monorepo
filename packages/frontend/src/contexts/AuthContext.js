import React, { createContext, useState, useEffect } from 'react';
import { networkAdapter } from 'services/NetworkAdapter';

export const AuthContext = createContext();

/**
 * Provides authentication state and user details to the application.
 * @namespace AuthProvider
 * @component
 */
export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userDetails, setUserDetails] = useState(null);
  const [authCheckTrigger, setAuthCheckTrigger] = useState(false);

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await networkAdapter.get('api/v1/users/auth-user', {}, { notUseMirage: true }); // TODO: Remove notUseMirage
        if (response && response.data) {
          setIsAuthenticated(response.data.isAuthenticated);
          setUserDetails(response.data.userDetails);
          console.log('User details logouuuuuuuuuutttttttttt');
        }
      } catch (error) {
        // If a 401 error is returned, set the user as logged out
        if (error.response && error.response.status === 401) {
          setIsAuthenticated(false);
          setUserDetails(null);
          console.log('User details logouuuuuuuuuutttttttttt75489375984375894375893');
        } else {
          console.error('Error checking authentication status:', error);
        }
      }
    };

    checkAuthStatus();
  }, [authCheckTrigger]);

  const triggerAuthCheck = () => {
    setAuthCheckTrigger((prev) => !prev);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, userDetails, triggerAuthCheck }}>
      {children}
    </AuthContext.Provider>
  );
};
