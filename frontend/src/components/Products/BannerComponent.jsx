import React, { useMemo } from 'react';
import './BannerComponent.css';

import banner1 from '../../assets/images/Banners/fashion-sale.webp';
import banner2 from '../../assets/images/Banners/fashionsale.jpg';
import banner3 from '../../assets/images/Banners/gadget-sale.jpg';
import banner4 from '../../assets/images/Banners/kitchen-sale.jpg';
import banner5 from '../../assets/images/Banners/oppo-reno7.webp';
import banner6 from '../../assets/images/Banners/poco-m4-pro.webp';
import banner7 from '../../assets/images/Banners/realme-9-pro.webp';

const images = [banner1, banner2, banner3, banner4, banner5, banner6, banner7];

const BannerComponent = () => {
    const randomImage = useMemo(() => {
        const randomIndex = Math.floor(Math.random() * images.length);
        return images[randomIndex];
    }, []);

    return (
        <a href='#' className="banner-container" aria-label={`Promotional banner`}>
            <img src={randomImage} alt="" className="banner-image" />
        </a>
    );
};

export default BannerComponent;
