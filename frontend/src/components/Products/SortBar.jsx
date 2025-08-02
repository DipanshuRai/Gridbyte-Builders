import React from 'react';
import './SortBar.css';

const SortBar = ({ totalResults, keyword, sortOption, setSortOption }) => {
    
    const sortOptions = [
        { key: 'relevance', label: 'Relevance' },
        { key: 'popularity', label: 'Popularity' },
        { key: 'price_asc', label: 'Price -- Low to High' },
        { key: 'price_desc', label: 'Price -- High to Low' },
        { key: 'newest', label: 'Newest First' },
    ];

    return (
        <div className="sort-bar-container">
            <div className="results-info">
                Showing 1 – {Math.min(40, totalResults)} of {totalResults.toLocaleString()} results for "{keyword}"
            </div>
            <div className="sort-options">
                <span className="sort-by-label">Sort By</span>
                {sortOptions.map(option => (
                    <button
                        key={option.key}
                        className={`sort-option-btn ${sortOption === option.key ? 'active' : ''}`}
                        onClick={() => setSortOption(option.key)}
                    >
                        {option.label}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default SortBar;