import { Link, useNavigate } from 'react-router-dom';
import EqualizerIcon from '@mui/icons-material/Equalizer';
import ShoppingBagIcon from '@mui/icons-material/ShoppingBag';
import InventoryIcon from '@mui/icons-material/Inventory';
import GroupIcon from '@mui/icons-material/Group';
import ReviewsIcon from '@mui/icons-material/Reviews';
import AddBoxIcon from '@mui/icons-material/AddBox';
import LogoutIcon from '@mui/icons-material/Logout';
import AccountBoxIcon from '@mui/icons-material/AccountBox';
import CloseIcon from '@mui/icons-material/Close';
import Avatar from '@mui/material/Avatar';
import { useDispatch, useSelector } from 'react-redux';
import './Sidebar.css';
import { useSnackbar } from 'notistack';
import { logoutUser } from '../../../actions/userAction';
import { useState } from 'react';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

// The navMenu array must be defined here
const navMenu = [
    {
        icon: <EqualizerIcon />,
        label: "Dashboard",
        ref: "/admin/dashboard",
    },
    {
        icon: <ShoppingBagIcon />,
        label: "Orders",
        ref: "/admin/orders",
    },
    {
        icon: <InventoryIcon />,
        label: "Products",
        ref: "/admin/products",
    },
    {
        icon: <AddBoxIcon />,
        label: "Add Product",
        ref: "/admin/new_product",
    },
    {
        icon: <GroupIcon />,
        label: "Users",
        ref: "/admin/users",
    },
    {
        icon: <ReviewsIcon />,
        label: "Reviews",
        ref: "/admin/reviews",
    },
    {
        icon: <AccountBoxIcon />,
        label: "My Profile",
        ref: "/account",
    },
    {
        icon: <LogoutIcon />,
        label: "Logout",
    },
];


const Sidebar = ({ activeTab, setToggleSidebar }) => {

    const dispatch = useDispatch();
    const navigate = useNavigate();
    const { enqueueSnackbar } = useSnackbar();
    const [isCollapsed, setIsCollapsed] = useState(false);

    const { user } = useSelector((state) => state.user);

    const handleLogout = () => {
        dispatch(logoutUser());
        enqueueSnackbar("Logout Successfully", { variant: "success" });
        navigate("/login");
    }

    const toggleCollapse = () => {
        setIsCollapsed(!isCollapsed);
    }

    return (
        <aside className={`sidebar z-10 sm:z-0 block min-h-screen fixed left-0 pb-14 max-h-screen ${isCollapsed ? 'w-20' : 'w-3/4 sm:w-1/5'} bg-gray-800 text-white overflow-x-hidden border-r transition-all duration-300`}>
            
            <div className={`flex items-center gap-3 p-2 rounded-lg my-4 mx-3.5 ${isCollapsed && 'justify-center'}`}>
                {!isCollapsed && (
                    <div className="flex items-center gap-3">
                        <Avatar
                            alt="Avatar"
                            src={user.avatar.url}
                        />
                        <div className="flex flex-col gap-0">
                            <span className="font-medium text-lg">{user.name}</span>
                            <span className="text-gray-300 text-sm">{user.email}</span>
                        </div>
                    </div>
                )}

                <button onClick={toggleCollapse} className="hidden sm:block bg-gray-700 hover:bg-gray-600 ml-auto rounded-full w-10 h-10 flex-shrink-0 flex items-center justify-center">
                    {isCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
                </button>
                
                <button onClick={()=>setToggleSidebar(false)} className="sm:hidden bg-gray-800 ml-auto rounded-full w-10 h-10 flex items-center justify-center">
                    <CloseIcon/>
                </button>
            </div>

            <div className="flex flex-col w-full gap-0 my-8">
                {navMenu.map((item, index) => {
                    const { icon, label, ref } = item;
                    return (
                        <>
                            {label === "Logout" ? (
                                <button onClick={handleLogout} className={`hover:bg-gray-700 flex gap-3 items-center py-3 px-4 font-medium ${isCollapsed && 'justify-center'}`}>
                                    <span>{icon}</span>
                                    {!isCollapsed && <span>{label}</span>}
                                </button>
                            ) : (
                                <Link to={ref} className={`${activeTab === index ? "bg-gray-700" : "hover:bg-gray-700"} flex gap-3 items-center py-3 px-4 font-medium ${isCollapsed && 'justify-center'}`}>
                                    <span>{icon}</span>
                                    {!isCollapsed && <span>{label}</span>}
                                </Link>
                            )}
                        </>
                    )
                }
                )}
            </div>

        </aside>
    )
};

export default Sidebar;