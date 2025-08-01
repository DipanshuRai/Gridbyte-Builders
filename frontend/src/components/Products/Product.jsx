import './Product.css';
import StarIcon from '@mui/icons-material/Star';
import FavoriteIcon from '@mui/icons-material/Favorite';
import { Link } from 'react-router-dom';
import { getDiscount } from '../../utils/functions';
import { useDispatch, useSelector } from 'react-redux';
import { addToWishlist, removeFromWishlist } from '../../actions/wishlistAction';
import { useFirstWorkingImage } from '../../Hooks/useFirstWorkingImage';
import { useSnackbar } from 'notistack';

const Product = ({ asin, title, images, rating, reviews_count, final_price, discount_percentage }) => {

    const displayImage = useFirstWorkingImage(images);
    const dispatch = useDispatch();
    const { enqueueSnackbar } = useSnackbar();
    const discountAmount = Math.abs(Math.random() - 0.5);
    const { wishlistItems } = useSelector((state) => state.wishlist);



    const itemInWishlist = wishlistItems.some((i) => i.product === asin);

    const addToWishlistHandler = () => {
        if (itemInWishlist) {
            dispatch(removeFromWishlist(asin));
            enqueueSnackbar("Removed From Wishlist", { variant: "success" });
        } else {
            dispatch(addToWishlist(asin));
            enqueueSnackbar("Added To Wishlist", { variant: "success" });
        }
    };

    return (
        <div className="product-card">
            <Link to={`/product/${asin}`} className="product-link">
                <div className="product-image">
                    <img
                        draggable="false"
                        className="product-img"
                        src={displayImage}
                        alt=""
                    />
                </div>
                <h2 className="product-title">
                    {title.length > 85 ? `${title.substring(0, 85)}...` : title}
                </h2>
            </Link>

            <div className="product-details">
                <span className="product-rating">
                    <span className="rating-badge">
                        {rating} <StarIcon sx={{ fontSize: "14px" }} />
                    </span>
                    <span className="reviews-count">({reviews_count})</span>
                </span>

                <div className="product-price">
                    <span>₹{final_price}</span>
                    <span className="price-strike">₹{Math.round(final_price / (1 - discount_percentage / 100))}</span>
                    <span className="price-discount">
                        {Math.round(discount_percentage)}% off
                    </span>
                </div>
            </div>

            <span
                onClick={addToWishlistHandler}
                className={`wishlist-icon ${itemInWishlist ? "active" : ""}`}
            >
                <FavoriteIcon sx={{ fontSize: "18px" }} />
            </span>
        </div>
    );
};

export default Product;
