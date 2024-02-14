import { useState } from 'react';
import { Link } from 'react-router-dom';
import { networkAdapter } from 'services/NetworkAdapter';
import { useNavigate } from 'react-router-dom';
import Toast from 'components/ux/toast/Toast';
import { REGISTRATION_MESSAGES } from 'utils/constants';

/**
 * Register Component
 * Renders a registration form that allows new users to create an account.
 * It captures user input for personal information and credentials, submitting these to a registration endpoint.
 * Upon successful registration, the user is notified and redirected to the login page.
 */
const Register = () => {
  const navigate = useNavigate();
  const [successMessage, setSuccessMessage] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });

  /**
   * Updates the form data state with the value of the input field that triggered the change.
   * This function ensures that the component's state reflects the user's input.
   *
   * @param {Object} e - The event object generated by the input field change.
   */
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  /**
   * Submits the registration form data to the server.
   * It performs an asynchronous operation to post the form data to a registration endpoint.
   * If registration is successful, a success message is displayed, and the user is redirected to the login page after a brief delay.
   * Otherwise, the user is informed of the failure.
   *
   * @param {Object} e - The event object generated by the form submission.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await networkAdapter.post('/api/register', formData);
    if (response && !response.errors) {
      setSuccessMessage(REGISTRATION_MESSAGES.SUCCESS);
      setShowSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    }
  };

  return (
    <>
      <div className="register__form">
        <div className="container mx-auto p-4 flex justify-center min-h-[600px] items-center">
          <form onSubmit={handleSubmit} className="w-full max-w-lg">
            <div className="text-center mb-10">
              <h2 className="text-3xl font-extrabold text-brand">
                Join Us Now
              </h2>
              <p className="text-gray-500">
                Create your account and start your journey with us
              </p>
            </div>
            <div className="flex flex-wrap -mx-3 mb-6">
              <div className="w-full md:w-1/2 px-3 mb-6 md:mb-0">
                <input
                  type="text"
                  name="firstName"
                  placeholder="First Name"
                  value={formData.firstName}
                  onChange={handleChange}
                  className="appearance-none block w-full bg-gray-200 text-gray-700 border rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white"
                />
              </div>
              <div className="w-full md:w-1/2 px-3">
                <input
                  type="text"
                  name="lastName"
                  placeholder="Last Name"
                  value={formData.lastName}
                  onChange={handleChange}
                  className="appearance-none block w-full bg-gray-200 text-gray-700 border rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white"
                />
              </div>
            </div>
            <div className="mb-6">
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                className="appearance-none block w-full bg-gray-200 text-gray-700 border rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white"
              />
            </div>
            <div className="mb-6">
              <input
                type="tel"
                name="phone"
                placeholder="Phone"
                value={formData.phone}
                onChange={handleChange}
                className="appearance-none block w-full bg-gray-200 text-gray-700 border rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white"
              />
            </div>
            <div className="mb-6">
              <input
                type="password"
                name="password"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
                className="appearance-none block w-full bg-gray-200 text-gray-700 border rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white"
              />
            </div>
            <div className="mb-6">
              <input
                type="password"
                name="confirmPassword"
                placeholder="Confirm Password"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="appearance-none block w-full bg-gray-200 text-gray-700 border rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white"
              />
            </div>
            <div className="flex items-center justify-between">
              <Link
                to="/login"
                className="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800"
              >
                Already registered? Login
              </Link>
              <button
                type="submit"
                className="bg-brand hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                Register
              </button>
            </div>
            {showSuccess && (
              <Toast type="success" message={successMessage} dismissError />
            )}
          </form>
        </div>
      </div>
    </>
  );
};

export default Register;
