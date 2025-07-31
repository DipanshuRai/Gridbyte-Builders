import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Pagination from '@mui/material/Pagination';

import Loader from '../Layouts/Loader';
import MinCategory from '../Layouts/MinCategory';
import Product from './Product';
import FilterSidebar from './FilterSidebar';
import MetaData from '../Layouts/MetaData';
import './Products.css';

const Products = () => {
    const params = useParams();
    const keyword = params.keyword || "";

    // State for filters
    const [price, setPrice] = useState([0, 200000]);
    const [category, setCategory] = useState("");
    const [ratings, setRatings] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);

    // State for fetching products
    const [allProducts, setAllProducts] = useState([]);
    const [filteredProducts, setFilteredProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const resultPerPage = 8;

    // Fetch products from the backend
    useEffect(() => {
        setLoading(true);
        const fetchProducts = async () => {
            try {
                const { data } = await axios.get(`http://localhost:8000/search?q=${keyword}`);
                setAllProducts(data.results || []);
            } catch (err) {
                setError(err.message);
                console.error("Failed to fetch products:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchProducts();
    }, [keyword]);

    // Apply filters whenever products or filter criteria change
    useEffect(() => {
        let tempProducts = [...allProducts];

        // Price Filter
        tempProducts = tempProducts.filter(p => p.final_price >= price[0] && p.final_price <= price[1]);
        
        // Category Filter (if a category is selected)
        if (category) {
            tempProducts = tempProducts.filter(p => p.department === category);
        }

        // Ratings Filter
        tempProducts = tempProducts.filter(p => p.rating >= ratings);

        setFilteredProducts(tempProducts);
        setCurrentPage(1);
    }, [allProducts, price, category, ratings]);

    const priceHandler = (e, newPrice) => {
        setPrice(newPrice);
    };

    const clearFilters = () => {
        setPrice([0, 200000]);
        setCategory("");
        setRatings(0);
    };

    // Pagination logic
    const count = Math.ceil(filteredProducts.length / resultPerPage);
    const currentPagedProducts = filteredProducts.slice((currentPage - 1) * resultPerPage, currentPage * resultPerPage);

    return (
        <>
            <MetaData title="All Products | Flipkart" />
            <MinCategory />
            <main className="products-page-container">
                <div className="products-page-layout">
                    <FilterSidebar
                        price={price}
                        priceHandler={priceHandler}
                        category={category}
                        setCategory={setCategory}
                        ratings={ratings}
                        setRatings={setRatings}
                        clearFilters={clearFilters}
                    />

                    <div className="products-column">
                        {loading ? <Loader /> : (
                            <>
                                {currentPagedProducts.length === 0 ? (
                                    <div className="no-results-container">
                                        <img draggable="false" className="no-results-image" src="https://static-assets-web.flixcart.com/www/linchpin/fk-cp-zion/img/error-no-search-results_2353c5.png" alt="Search Not Found" />
                                        <h1 className="no-results-title">Sorry, no results found!</h1>
                                        <p className="no-results-subtitle">Please check the spelling or try searching for something else</p>
                                    </div>
                                ) : (
                                    <div className="products-display-container">
                                        <div className="products-grid">
                                            {currentPagedProducts.map((product) => (
                                                <Product {...product} key={product.asin} />
                                            ))}
                                        </div>
                                        {count > 1 && (
                                            <div className="pagination-container">
                                                <Pagination
                                                    count={count}
                                                    page={currentPage}
                                                    onChange={(e, val) => setCurrentPage(val)}
                                                    color="primary"
                                                />
                                            </div>
                                        )}
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>
            </main>
        </>
    );
};

export default Products;