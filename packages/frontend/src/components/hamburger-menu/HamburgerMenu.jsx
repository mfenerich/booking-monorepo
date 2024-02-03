import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faXmark } from '@fortawesome/free-solid-svg-icons';
import { Link, useNavigate } from 'react-router-dom';
import DropdownButton from '../dropdown-button/DropdownButton';

/**
 * HamburgerMenu Component
 * Renders a hamburger menu with navigation links. It can be toggled visible or hidden.
 * The menu contains links to Home, Hotels, About Us, and depending on the authentication status,
 * a link to either the user profile or the login/register page.
 *
 * @param {Object} props - Props for the component.
 * @param {boolean} props.isVisible - Controls the visibility of the hamburger menu.
 * @param {Function} props.onHamburgerMenuToggle - Callback function to toggle the visibility of the menu.
 * @param {boolean} props.isAuthenticated - Indicates whether the user is authenticated.
 */
const HamburgerMenu = (props) => {
  const navigate = useNavigate();
  const dropdownOptions = [
    { name: 'Profile', onClick: () => navigate('/user-profile') },
    { name: 'Logout' },
  ];

  const { isVisible, onHamburgerMenuToggle, isAuthenticated } = props;
  return (
    <div
      data-testid="hamburger-menu"
      className={`bg-brand shadow-2xl z-10 ${
        isVisible ? 'absolute right-0 w-1/2 top-0 h-screen' : 'hidden'
      }`}
    >
      <div className="absolute right-5 top-2">
        <FontAwesomeIcon
          data-testid="menu-close__button"
          icon={faXmark}
          size="2x"
          color="#fff"
          onClick={onHamburgerMenuToggle}
        />
      </div>
      <ul className="list-none">
        <li className="p-4 hover:bg-sky-700">
          <Link to="/" className="uppercase font-medium text-slate-100">
            Home
          </Link>
        </li>
        <li className="p-4 hover:bg-sky-700">
          <Link to="/hotels" className="uppercase font-medium text-slate-100">
            Hotels
          </Link>
        </li>
        <li className="p-4 hover:bg-sky-700">
          <Link to="/about-us" className="uppercase font-medium text-slate-100">
            About us
          </Link>
        </li>
        <li className={`${!isAuthenticated && 'p-4'}`}>
          {isAuthenticated ? (
            <DropdownButton triggerType="click" options={dropdownOptions} />
          ) : (
            <Link
              to="/login"
              className="uppercase font-medium text-slate-100 hover-underline-animation"
            >
              Login/Register
            </Link>
          )}
        </li>
      </ul>
    </div>
  );
};

export default HamburgerMenu;
