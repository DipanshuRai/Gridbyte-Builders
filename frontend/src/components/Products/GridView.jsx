import React from 'react';
import Product from './Product'; // Assuming Product is your card component
import './GridView.css';

const GridView = ({ products }) => {
    return (
        <div className="products-grid-view">
            {products.map((product) => (
                <Product {...product} key={product.asin} />
            ))}
        </div>
    );
};

export default GridView;