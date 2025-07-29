import React from 'react';
import {
  AccountCircle, OfflineBolt, AddCircle, ShoppingBag,
  Favorite, Chat, ConfirmationNumber, AccountBalanceWallet,
  Notifications, PowerSettingsNew, Dashboard
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useSnackbar } from 'notistack';
import { logoutUser } from '../../../actions/userAction';
import './PrimaryDropDownMenu.css';

const PrimaryDropDownMenu = ({ setTogglePrimaryDropDown, user }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const { wishlistItems } = useSelector((state) => state.wishlist);

  const handleLogout = () => {
    dispatch(logoutUser());
    navigate("/login");
    enqueueSnackbar("Logout Successfully", { variant: "success" });
    setTogglePrimaryDropDown(false);
  };

  const navs = [
    { title: "Supercoin Zone", icon: <OfflineBolt fontSize="small" />, redirect: "/" },
    { title: "Flipkart Plus Zone", icon: <AddCircle fontSize="small" />, redirect: "/" },
    { title: "Orders", icon: <ShoppingBag fontSize="small" />, redirect: "/orders" },
    { title: "Wishlist", icon: <Favorite fontSize="small" />, redirect: "/wishlist" },
    { title: "My Chats", icon: <Chat fontSize="small" />, redirect: "/" },
    { title: "Coupons", icon: <ConfirmationNumber fontSize="small" />, redirect: "/" },
    { title: "Gift Cards", icon: <AccountBalanceWallet fontSize="small" />, redirect: "/" },
    { title: "Notifications", icon: <Notifications fontSize="small" />, redirect: "/" },
  ];

  return (
    <div className="primary-dropdown">
      {user.role === "admin" && (
        <Link className="dropdown-item" to="/admin/dashboard">
          <span className="icon blue"><Dashboard fontSize="small" /></span>
          Admin Dashboard
        </Link>
      )}

      <Link className="dropdown-item" to="/account">
        <span className="icon blue"><AccountCircle fontSize="small" /></span>
        My Profile
      </Link>

      {navs.map(({ title, icon, redirect }, i) => (
        <Link className="dropdown-item" to={redirect} key={i}>
          <span className="icon blue">{icon}</span>
          {title}
          {title === "Wishlist" && (
            <span className="wishlist-count">{wishlistItems.length}</span>
          )}
        </Link>
      ))}

      <div className="dropdown-item logout" onClick={handleLogout}>
        <span className="icon blue"><PowerSettingsNew fontSize="small" /></span>
        Logout
      </div>

      <div className="dropdown-arrow-container">
        <div className="dropdown-arrow"></div>
      </div>
    </div>
  );
};

export default PrimaryDropDownMenu;
