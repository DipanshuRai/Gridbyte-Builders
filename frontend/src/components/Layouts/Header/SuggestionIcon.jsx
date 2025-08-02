import React from 'react';
import SearchIcon from '@mui/icons-material/Search';
import CategoryIcon from '@mui/icons-material/Category';
import StorefrontIcon from '@mui/icons-material/Storefront';
import placeholderImage from '../../../assets/image-placeholder.png';

const SuggestionIcon = ({ item }) => {
    if (item.type === 'product' && item.image) {
        return (
            <img
                src={item.image}
                alt={item.suggestion}
                className="suggestion-image"
                onError={(e) => (e.target.src = placeholderImage)}
            />
        );
    }
    
    // For products without an image, show a placeholder
    if (item.type === 'product') {
        return (
            <img
                src={placeholderImage}
                alt="No preview"
                className="suggestion-image"
            />
        );
    }

    // Render the appropriate icon based on the suggestion type
    let icon;
    switch (item.type) {
        case 'query':
            icon = <SearchIcon className="suggestion-icon" />;
            break;
        case 'category':
            icon = <CategoryIcon className="suggestion-icon" />;
            break;
        case 'brand':
            icon = <StorefrontIcon className="suggestion-icon" />;
            break;
        default:
            icon = <SearchIcon className="suggestion-icon" />;
    }

    return (
        <div className="suggestion-icon-wrapper">
            {icon}
        </div>
    );
};

export default SuggestionIcon;