import { useState, useEffect } from 'react';
import placeholderImage from '../assets/no-image-available.jpg';

export const useFirstWorkingImage = (imageUrls) => {
    const [displaySrc, setDisplaySrc] = useState(placeholderImage);

    useEffect(() => {
        if (!Array.isArray(imageUrls) || imageUrls.length === 0) {
            setDisplaySrc(placeholderImage);
            return;
        }

        let isMounted = true;

        const testImage = (url) => {
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.onload = () => resolve(url);
                img.onerror = () => reject();
                img.src = url;
            });
        };

        const findFirstImage = async () => {
            for (const url of imageUrls) {
                try {
                    const workingUrl = await testImage(url);
                    if (isMounted) {
                        setDisplaySrc(workingUrl);
                        return;
                    }
                } catch (error) {
                }
            }
            if (isMounted) {
                setDisplaySrc(placeholderImage);
            }
        };

        findFirstImage();

        return () => {
            isMounted = false;
        };

    }, [imageUrls]);

    return displaySrc;
};