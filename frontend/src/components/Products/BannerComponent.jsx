import React from 'react';
import './BannerComponent.css';

const BannerComponent = ({ image_url, link, category }) => {
    return (
        <a href={link} className="banner-container" aria-label={`Promotional banner for ${category}`}>
            <img src={image_url} alt={`Banner for ${category}`} className="banner-image" />
        </a>
    );
};

export default BannerComponent;