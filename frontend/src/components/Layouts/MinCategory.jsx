import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Link } from 'react-router-dom';
import './MinCategory.css';

const categories = [
    "Electronics",
    "TVs & Appliances",
    "Men",
    "Women",
    "Baby & Kids",
    "Home & Furniture",
    "Sports, Books & More",
    "Flights",
    "Offer Zone",
    "Grocery",
];

const MinCategory = () => {
    return (
        <section className="min-category">
            <div className="min-category-wrapper">
                {categories.map((el, i) => (
                    <Link to="/products" key={i} className="category-link">
                        {el}
                        <span className="category-icon">
                            <ExpandMoreIcon sx={{ fontSize: "16px" }} />
                        </span>
                    </Link>
                ))}
            </div>
        </section>
    );
};

export default MinCategory;
