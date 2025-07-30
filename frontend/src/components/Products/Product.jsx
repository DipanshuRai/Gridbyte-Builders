import StarIcon from '@mui/icons-material/Star';
import FavoriteIcon from '@mui/icons-material/Favorite';
import { Link } from 'react-router-dom';
import { getDiscount } from '../../utils/functions';
import { useDispatch, useSelector } from 'react-redux';
import { addToWishlist, removeFromWishlist } from '../../actions/wishlistAction';
import { useSnackbar } from 'notistack';

const Product = ({ _id, title, images, ratings, review_count, final_price, cuttedPrice }) => {

    const dispatch = useDispatch();
    const { enqueueSnackbar } = useSnackbar();
    const discountAmount = Math.abs(Math.random()-0.5);
    const { wishlistItems } = useSelector((state) => state.wishlist);

    const itemInWishlist = wishlistItems.some((i) => i.product === _id);

    const addToWishlistHandler = () => {
        if (itemInWishlist) {
            dispatch(removeFromWishlist(_id));
            enqueueSnackbar("Remove From Wishlist", { variant: "success" });
        } else {
            dispatch(addToWishlist(_id));
            enqueueSnackbar("Added To Wishlist", { variant: "success" });
        }
    }

    return (
        <div className="flex flex-col items-start gap-2 px-4 py-6 relative hover:shadow-lg rounded-sm">
            {/* <!-- image & product title --> */}
            <Link to={`/product/${_id}`} className="flex flex-col items-center text-center group">
                <div className="w-44 h-48">
                    <img draggable="false" className="w-full h-full object-contain" src={images && images[0].url} alt="" />
                </div>
                <h2 className="text-sm mt-4 group-hover:text-primary-blue text-left">{title.length > 85 ? `${title.substring(0, 85)}...` : title}</h2>
            </Link>
            {/* <!-- image & product title --> */}

            {/* <!-- product description --> */}
            <div className="flex flex-col gap-2 items-start">
                {/* <!-- rating badge --> */}
                <span className="text-sm text-gray-500 font-medium flex gap-2 items-center">
                    <span className="text-xs px-1.5 py-0.5 bg-primary-green rounded-sm text-white flex items-center gap-0.5">{ratings} <StarIcon sx={{ fontSize: "14px" }} /></span>
                    <span>({review_count})</span>
                </span>
                {/* <!-- rating badge --> */}

                {/* <!-- price container --> */}
                <div className="flex items-center gap-1.5 text-md font-medium">
                    <span>₹{(Math.round((1-discountAmount)*final_price)).toLocaleString()}</span>
                    <span className="text-gray-500 line-through text-xs">₹{final_price.toLocaleString()}</span>
                    <span className="text-xs text-primary-green">{getDiscount(Math.round((1-discountAmount)*final_price), final_price)}%&nbsp;off</span>
                </div>
                {/* <!-- price container --> */}
            </div>
            {/* <!-- product description --> */}

            {/* <!-- wishlist badge --> */}
            <span onClick={addToWishlistHandler} className={`${itemInWishlist ? "text-red-500" : "hover:text-red-500 text-gray-300"} absolute top-6 right-6 cursor-pointer`}><FavoriteIcon sx={{ fontSize: "18px" }} /></span>
            {/* <!-- wishlist badge --> */}

        </div>
    );
};

export default Product;
