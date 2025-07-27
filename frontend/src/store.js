import { configureStore } from '@reduxjs/toolkit';
import thunk from 'redux-thunk';
// Import your reducers:
import {
  forgotPasswordReducer,
  profileReducer,
  userReducer,
  allUsersReducer,
  userDetailsReducer,
} from './reducers/userReducer';
import {
  newProductReducer,
  newReviewReducer,
  productDetailsReducer,
  productReducer,
  productsReducer,
  productReviewsReducer,
  reviewReducer,
} from './reducers/productReducer';
import { cartReducer } from './reducers/cartReducer';
import { saveForLaterReducer } from './reducers/saveForLaterReducer';
import {
  allOrdersReducer,
  myOrdersReducer,
  newOrderReducer,
  orderDetailsReducer,
  orderReducer,
  paymentStatusReducer,
} from './reducers/orderReducer';
import { wishlistReducer } from './reducers/wishlistReducer';

const reducer = {
  user: userReducer,
  profile: profileReducer,
  forgotPassword: forgotPasswordReducer,
  products: productsReducer,
  productDetails: productDetailsReducer,
  newReview: newReviewReducer,
  cart: cartReducer,
  saveForLater: saveForLaterReducer,
  newOrder: newOrderReducer,
  myOrders: myOrdersReducer,
  paymentStatus: paymentStatusReducer,
  orderDetails: orderDetailsReducer,
  allOrders: allOrdersReducer,
  order: orderReducer,
  newProduct: newProductReducer,
  product: productReducer,
  users: allUsersReducer,
  userDetails: userDetailsReducer,
  reviews: productReviewsReducer,
  review: reviewReducer,
  wishlist: wishlistReducer,
};

const initialState = {
  cart: {
    cartItems: localStorage.getItem('cartItems')
      ? JSON.parse(localStorage.getItem('cartItems'))
      : [],
    shippingInfo: localStorage.getItem('shippingInfo')
      ? JSON.parse(localStorage.getItem('shippingInfo'))
      : {},
  },
  saveForLater: {
    saveForLaterItems: localStorage.getItem('saveForLaterItems')
      ? JSON.parse(localStorage.getItem('saveForLaterItems'))
      : [],
  },
  wishlist: {
    wishlistItems: localStorage.getItem('wishlistItems')
      ? JSON.parse(localStorage.getItem('wishlistItems'))
      : [],
  },
};

const store = configureStore({
  reducer,
  preloadedState: initialState,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      // you can disable serializable check if needed, but RTK handles it by default
      serializableCheck: {
        ignoredActions: [], // default, override if you have non-serializable actions
      },
    }).concat(thunk),
  devTools: process.env.NODE_ENV !== 'production',
});

export default store;
