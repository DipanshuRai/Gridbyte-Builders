const mongoose = require("mongoose");

const productLiteSchema = new mongoose.Schema({
  productName: String,
  description: String
});

module.exports = mongoose.model("ProductLite", productLiteSchema, "products");
// "products" is the exact name of your MongoDB collection
