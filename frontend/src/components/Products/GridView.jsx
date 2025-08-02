import React from 'react';
import Product from './Product';
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