import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Link } from 'react-router-dom';
import './MinCategory.css';

const MinCategory = ({ categories }) => {
    return (
        <section className="min-category">
            <div className="min-category-wrapper">
                {categories.slice(0, 8).map((el, i) => (
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
