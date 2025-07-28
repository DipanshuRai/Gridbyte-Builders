if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

const path = require('path');
const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const fileUpload = require('express-fileupload');
const cloudinary = require('cloudinary');
const morgan = require('morgan')
const cors = require('cors');
const Fuse = require("fuse.js");

const connectDatabase = require('./config/database.js');
const errorMiddleware = require('./middlewares/error');
const CompressedTrie = require('./compressedTrie');
const ProductLite = require("./models/ProductLite");

console.log("Requiring database.js...");
connectDatabase();
console.log("✅ database.js loaded");

const app = express();

// Cloudinary config
cloudinary.config({
  cloud_name: process.env.CLOUDINARY_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET,
});

// Middleware
app.use(cors({ origin: process.env.FRONTEND_URL, credentials: true }));
app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(fileUpload());

// Global variables for autosuggest
let compressedTrie;
let fuse;
let productNames = [];

// Build Trie & Fuse index

const buildSearchStructures = async () => {
  try {
    const products = await ProductLite.find({});
    productNames = products.map(p => p.productName);

    // Build Fuse index
    fuse = new Fuse(products, {
      keys: ['productName', 'description'],
      threshold: 0.3,
    });

    // Build Compressed Trie
    compressedTrie = new CompressedTrie();
    productNames.forEach(name => compressedTrie.insert(name));

    console.log("Autosuggestion structures built (CompressedTrie + Fuse)");
  } catch (err) {
    console.error("Error building autosuggest structures:", err.message);
  }
};

buildSearchStructures();


app.use('/api/v1', require('./routes/userRoute'));
app.use('/api/v1', require('./routes/productRoute'));
app.use('/api/v1', require('./routes/orderRoute'));
app.use('/api/v1', require('./routes/paymentRoute'));


// Health route
app.get('/', (req, res) => {
  res.send('Server is Running! 🚀');
});

// Autosuggestion route
app.get("/suggest", (req, res) => {
  const q = req.query.q?.toLowerCase();
  if (!q || q.length < 1) return res.json({ suggestions: [] });

  if (!compressedTrie || !fuse) {
    return res.json({ suggestions: [] });
  }

const trieSuggestions = compressedTrie.getSuggestions(q, 5);  // for brand or name prefixes
const fuseSuggestions = fuse.search(q).map(r => r.item.productName).slice(0, 5);


  console.log("Trie suggestions:", trieSuggestions);
  console.log("Fuse suggestions:", fuseSuggestions);

  const suggestions = Array.from(
    new Map(
      [...trieSuggestions, ...fuseSuggestions].map(s => [s.toLowerCase(), s])
    ).values()
  );


  return res.status(200).json({ suggestions: Array.isArray(suggestions) ? suggestions : [] });
});


app.use(errorMiddleware);

// Start server
const PORT = process.env.PORT || 4000;
const server = app.listen(PORT, () => {
  console.log(`Server running on PORT: ${PORT}`);
});

// handle unhandled promise rejections
process.on('unhandledRejection', err => {
  console.error('Unhandled Rejection:', err.message);
  server.close(() => process.exit(1));
});

process.on('uncaughtException', err => {
  console.error('Uncaught Exception:', err.message);
  process.exit(1);
});

