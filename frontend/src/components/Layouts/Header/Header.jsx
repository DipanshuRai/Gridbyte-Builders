import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import Searchbar from './Searchbar';
import logo from '../../../assets/images/logo.png';
import PrimaryDropDownMenu from './PrimaryDropDownMenu';
import SecondaryDropDownMenu from './SecondaryDropDownMenu';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { useDetectOutsideClick } from '../../../Hooks/useDetectOutsideClick';

const Header = () => {
  const { isAuthenticated, user } = useSelector((state) => state.user);
  const { cartItems } = useSelector(state => state.cart);

  const {
    isActive: isPrimaryDropDownActive,
    setIsActive: setIsPrimaryDropDownActive,
    triggerRef: primaryTriggerRef,
    nodeRef: primaryNodeRef,
  } = useDetectOutsideClick(false);

  const {
    isActive: isSecondaryDropDownActive,
    setIsActive: setIsSecondaryDropDownActive,
    triggerRef: secondaryTriggerRef,
    nodeRef: secondaryNodeRef,
  } = useDetectOutsideClick(false);

  const handlePrimaryDropDownToggle = () => {
    setIsSecondaryDropDownActive(false);
    setIsPrimaryDropDownActive(!isPrimaryDropDownActive);
  };

  const handleSecondaryDropDownToggle = () => {
    setIsPrimaryDropDownActive(false);
    setIsSecondaryDropDownActive(!isSecondaryDropDownActive);
  };

  return (
    <header className="bg-primary-blue fixed top-0 py-2.5 w-full z-10">
      <div className="w-full sm:w-9/12 px-1 sm:px-4 m-auto flex justify-between items-center relative">
        <div className="flex items-center flex-1">
          <Link className="h-7 mr-1 sm:mr-4" to="/">
            <img draggable="false" className="h-full w-full object-contain" src={logo} alt="Flipkart Logo" />
          </Link>
          <Searchbar />
        </div>

        <div className="flex items-center justify-between ml-1 sm:ml-0 gap-0.5 sm:gap-7 relative">
          {console.log("isAuthenticated: ",isAuthenticated)}
          
          {isAuthenticated === false ?
            <Link to="/login" className="px-3 sm:px-9 py-0.5 text-primary-blue bg-white border font-medium rounded-sm cursor-pointer">Login</Link>
            :
            (
              <span
                ref={primaryTriggerRef}
                className="userDropDown flex items-center text-white font-medium gap-1 cursor-pointer"
                onClick={handlePrimaryDropDownToggle}
              >
                {user?.name && user?.name.split(" ", 1)}
                <span>{isPrimaryDropDownActive ? <ExpandLessIcon sx={{ fontSize: "16px" }} /> : <ExpandMoreIcon sx={{ fontSize: "16px" }} />}</span>
              </span>
            )
          }

          {isPrimaryDropDownActive && <div ref={primaryNodeRef}><PrimaryDropDownMenu setTogglePrimaryDropDown={setIsPrimaryDropDownActive} user={user} /></div>}

          <span
            ref={secondaryTriggerRef}
            className="moreDropDown hidden sm:flex items-center text-white font-medium gap-1 cursor-pointer"
            onClick={handleSecondaryDropDownToggle}
          >
            More
            <span>{isSecondaryDropDownActive ? <ExpandLessIcon sx={{ fontSize: "16px" }} /> : <ExpandMoreIcon sx={{ fontSize: "16px" }} />}</span>
          </span>

          {isSecondaryDropDownActive && <div ref={secondaryNodeRef}><SecondaryDropDownMenu /></div>}

          <Link to="/cart" className="flex items-center text-white font-medium gap-2 relative">
            <span><ShoppingCartIcon /></span>
            {cartItems.length > 0 &&
              <div className="w-5 h-5 p-2 bg-red-500 text-xs rounded-full absolute -top-2 left-3 flex justify-center items-center border">
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