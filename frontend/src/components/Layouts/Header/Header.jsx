import React, { useState, useRef } from 'react';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import Searchbar from './Searchbar';
import logo from '../../../assets/images/logo.png';
import PrimaryDropDownMenu from './PrimaryDropDownMenu';
import SecondaryDropDownMenu from './SecondaryDropDownMenu';
import { useDetectOutsideClick } from '../../../Hooks/useDetectOutsideClick';
import './Header.css';

const Header = () => {
  const { isAuthenticated, user } = useSelector((state) => state.user);
  const { cartItems } = useSelector(state => state.cart);

  const [isPrimaryDropDownActive, setIsPrimaryDropDownActive] = useState(false);
  const primaryDropDownRef = useRef(null);
  useDetectOutsideClick(primaryDropDownRef, () => setIsPrimaryDropDownActive(false));

  const [isSecondaryDropDownActive, setIsSecondaryDropDownActive] = useState(false);
  const secondaryDropDownRef = useRef(null);
  useDetectOutsideClick(secondaryDropDownRef, () => setIsSecondaryDropDownActive(false));

  const handlePrimaryDropDownToggle = () => {
    setIsSecondaryDropDownActive(false);
    setIsPrimaryDropDownActive(prev => !prev);
  };

  const handleSecondaryDropDownToggle = () => {
    setIsPrimaryDropDownActive(false);
    setIsSecondaryDropDownActive(prev => !prev);
  };

  return (
    <header className="header-container">
      <div className="header-content">
        <div className="header-left">
          <Link className="logo-link" to="/">
            <img draggable="false" className="logo-image" src={logo} alt="Flipkart Logo" />
          </Link>
          <Searchbar />
        </div>

        <div className="header-right">
          {isAuthenticated === false ? (
            <Link to="/login" className="login-button">Login</Link>
          ) : (
            <div ref={primaryDropDownRef} className="dropdown-container">
              <span className="user-dropdown" onClick={handlePrimaryDropDownToggle}>
                {user?.name && user.name.split(" ", 1)}
                <span>
                  {isPrimaryDropDownActive ?
                    <ExpandLessIcon sx={{ fontSize: "16px" }} /> :
                    <ExpandMoreIcon sx={{ fontSize: "16px" }} />
                  }
                </span>
              </span>
              {isPrimaryDropDownActive && (
                <PrimaryDropDownMenu setTogglePrimaryDropDown={setIsPrimaryDropDownActive} user={user} />
              )}
            </div>
          )}

          <div ref={secondaryDropDownRef} className="dropdown-container">
            <span className="more-dropdown" onClick={handleSecondaryDropDownToggle}>
              More
              <span>
                {isSecondaryDropDownActive ?
                  <ExpandLessIcon sx={{ fontSize: "16px" }} /> :
                  <ExpandMoreIcon sx={{ fontSize: "16px" }} />
                }
              </span>
            </span>
            {isSecondaryDropDownActive && (
              <SecondaryDropDownMenu />
            )}
          </div>

          <Link to="/cart" className="cart-link">
            <span><ShoppingCartIcon /></span>
            {cartItems.length > 0 &&
              <div className="cart-item-count">
                {cartItems.length}
              </div>
            }
            Cart
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;