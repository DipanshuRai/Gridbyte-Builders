const SearchHistory = require('../models/searchHistoryModel');
const asyncErrorHandler = require('../middlewares/asyncErrorHandler');

exports.saveSearchQuery = asyncErrorHandler(async (req, res, next) => {
    const { query } = req.body;
    const userId = req.user.id;

    if (!query || !query.trim()) {
        return res.status(200).json({ success: true });
    }

    await SearchHistory.findOneAndUpdate(
        { user: userId, query: query.trim().toLowerCase() },
        { $set: { user: userId, query: query.trim()} },
        { upsert: true, new: true }
    );

    res.status(200).json({
        success: true,
    });
});

exports.getSearchHistory = asyncErrorHandler(async (req, res, next) => {
    const userId = req.user.id;

    const history = await SearchHistory.find({ user: userId })
        .sort({ updatedAt: -1 }) // Sort by most recently updated
        .limit(8) // Limit to the most recent 8
        .select('query');

    const queries = history.map(item => item.query);

    res.status(200).json({
        success: true,
        history: queries,
    });
});