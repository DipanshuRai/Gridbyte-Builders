import React from 'react';
import './AdComponent.css';

const AdComponent = ({ ad_name, description, image_url }) => {
    console.log("Image url: ",image_url);
    
    return (
        <a href='#' className="ad-card-container">
            <div className="ad-card-content">
                <span className="ad-badge">Ad</span>
                <h4 className="ad-title">{ad_name}</h4>
                <p className="ad-description">{description}</p>
            </div>
        </a>
    );
};

export default AdComponent;