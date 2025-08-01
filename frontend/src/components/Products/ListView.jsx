import React from 'react';
import { Link } from 'react-router-dom';
import StarIcon from '@mui/icons-material/Star';
import { useFirstWorkingImage } from '../../Hooks/useFirstWorkingImage';
import './ListView.css';

const ProductListItem = ({ product }) => {
    const displayImage = useFirstWorkingImage(product.images);
    const renderSummary = () => {
        // --- PRIMARY METHOD: Use product specifications if they exist ---
        if (product.product_specifications && product.product_specifications.length > 0) {
            return (
                <ul className="list-item-specs">
                    {product.product_specifications.slice(0, 6).map((spec, i) => (
                        spec.value && spec.key && <li key={i}>{spec.key}: {spec.value}</li>
                    ))}
                </ul>
            );
        }

        // --- FALLBACK METHOD: Use a truncated description if specs are missing ---
        if (product.description) {
            const truncatedDesc = product.description.slice(0, 150) + (product.description.length > 150 ? "..." : "");
            return <p className="list-item-description">{truncatedDesc}</p>;
        }

        return null;
    };

    return (
        <Link to={`/product/${product.asin}`} className="product-list-item">
            <div className="list-item-image-container">
                <img
                    src={displayImage}
                    alt={product.title}
                    className="list-item-image"
                />
            </div>
            <div className="list-item-details-container">
                <p className="list-item-title">{product.title}</p>
                <div className="list-item-rating-container">
                    <span className="list-item-rating">
                        {product.rating} <StarIcon />
                    </span>
                    <span className="list-item-reviews">({product.reviews_count.toLocaleString()} Reviews)</span>
                </div>
                {renderSummary()}
            </div>
            <div className="list-item-pricing-container">
                <p className="list-item-price">₹{product.final_price.toLocaleString()}</p>
                <div className="list-item-discount-container">
                    <span className="list-item-initial-price">₹{Math.round(product.final_price / (1 - product.discount_percentage / 100))}</span>
                    <span className="list-item-discount">{Math.round(product.discount_percentage)}% off</span>
                </div>
                <p className="list-item-delivery">Free Delivery</p>
            </div>
        </Link>
    );
};

const ListView = ({ products }) => {
    return (
        <div className="products-list-view">
            {products.map((product) => (
                <ProductListItem product={product} key={product.asin} />
            ))}
        </div>
    );
};

export default ListView;