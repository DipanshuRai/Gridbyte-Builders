const express = require('express');
const router = express.Router();
const { isAuthenticatedUser } = require('../middlewares/auth');
const {
    saveSearchQuery,
    getSearchHistory
} = require('../controllers/searchHistoryController');

router.route('/history').post(isAuthenticatedUser, saveSearchQuery);
router.route('/history').get(isAuthenticatedUser, getSearchHistory);

module.exports = router;