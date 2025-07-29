import {
  Notifications, BusinessCenter, LiveHelp,
  TrendingUp, Download
} from '@mui/icons-material';
import './SecondaryDropDownMenu.css';

const SecondaryDropDownMenu = () => {
  const navs = [
    { title: "Notification Preferences", icon: <Notifications fontSize="small" />, redirect: "https://www.flipkart.com/communication-preferences/push" },
    { title: "Sell on Flipkart", icon: <BusinessCenter fontSize="small" />, redirect: "https://seller.flipkart.com/sell-online" },
    { title: "24x7 Customer Care", icon: <LiveHelp fontSize="small" />, redirect: "https://www.flipkart.com/helpcentre" },
    { title: "Advertise", icon: <TrendingUp fontSize="small" />, redirect: "https://advertising.flipkart.com" },
    { title: "Download App", icon: <Download fontSize="small" />, redirect: "https://www.flipkart.com/mobile-apps" },
  ];

  return (
    <div className="secondary-dropdown">
      {navs.map(({ title, icon, redirect }, i) => (
        <a className="dropdown-item" href={redirect} key={i}>
          <span className="icon blue">{icon}</span>
          {title}
        </a>
      ))}
      <div className="dropdown-arrow-container">
        <div className="dropdown-arrow"></div>
      </div>
    </div>
  );
};

export default SecondaryDropDownMenu;
