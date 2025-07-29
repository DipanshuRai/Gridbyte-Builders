const mongoose = require('mongoose');

const searchHistorySchema = new mongoose.Schema({
    query: {
        type: String,
        required: true,
        trim: true,
    },
    user: {
        type: mongoose.Schema.ObjectId,
        ref: 'User',
        required: true,
    },
}, {
    timestamps: true
});

// To prevent storing the exact same query multiple times for the same user
searchHistorySchema.index({ user: 1, query: 1 }, { unique: true });

module.exports = mongoose.model('SearchHistory', searchHistorySchema);