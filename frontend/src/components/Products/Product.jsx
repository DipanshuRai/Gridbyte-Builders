import './Product.css';
import StarIcon from '@mui/icons-material/Star';
import FavoriteIcon from '@mui/icons-material/Favorite';
import { Link } from 'react-router-dom';
import { getDiscount } from '../../utils/functions';
import { useDispatch, useSelector } from 'react-redux';
import { addToWishlist, removeFromWishlist } from '../../actions/wishlistAction';
import { useSnackbar } from 'notistack';

const Product = ({ _id, title, image, rating, reviews_count, final_price }) => {
    const dispatch = useDispatch();
    const { enqueueSnackbar } = useSnackbar();
    const discountAmount = Math.abs(Math.random() - 0.5);
    const { wishlistItems } = useSelector((state) => state.wishlist);

    const itemInWishlist = wishlistItems.some((i) => i.product === _id);

    const addToWishlistHandler = () => {
        if (itemInWishlist) {
            dispatch(removeFromWishlist(_id));
            enqueueSnackbar("Removed From Wishlist", { variant: "success" });
        } else {
            dispatch(addToWishlist(_id));
            enqueueSnackbar("Added To Wishlist", { variant: "success" });
        }
    };

    return (
        <div className="product-card">
            <Link to={`/product/${_id}`} className="product-link">
                <div className="product-image">
                    <img
                        draggable="false"
                        className="product-img"
                        src={image}
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
                    <span>₹{(Math.round((1 - discountAmount) * final_price)).toLocaleString()}</span>
                    <span className="price-strike">₹{final_price.toLocaleString()}</span>
                    <span className="price-discount">
                        {getDiscount(Math.round((1 - discountAmount) * final_price), final_price)}% off
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
