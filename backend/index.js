if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

const path = require('path');
const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const fileUpload = require('express-fileupload');
const cloudinary = require('cloudinary');
const cors = require('cors');

const connectDatabase = require('./config/database.js');
const errorMiddleware = require('./middlewares/error');

// handle uncaught exceptions
process.on('uncaughtException', err => {
  console.error('Uncaught Exception:', err.message);
  process.exit(1);
});

const app = express();

// database connection
connectDatabase();

// Cloudinary config
cloudinary.config({
  cloud_name: process.env.CLOUDINARY_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET,
});

app.use(cors({
  origin: process.env.FRONTEND_URL, 
  credentials: true, 
}));

// middleware
app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(fileUpload());

// import routes
app.use('/api/v1', require('./routes/userRoute'));
app.use('/api/v1', require('./routes/productRoute'));
app.use('/api/v1', require('./routes/orderRoute'));
app.use('/api/v1', require('./routes/paymentRoute'));

app.get('/', (req, res) => {
  res.send('Server is Running! 🚀');
});

// global error handler
app.use(errorMiddleware);

const PORT = process.env.PORT || 4000;
const server = app.listen(PORT, () => {
  console.log(`Server running on PORT: ${PORT}`);
});

// handle unhandled promise rejections
process.on('unhandledRejection', err => {
  console.error('Unhandled Rejection:', err.message);
  server.close(() => process.exit(1));
});
