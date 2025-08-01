import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Pagination from '@mui/material/Pagination';
import Loader from '../Layouts/Loader';
import MinCategory from '../Layouts/MinCategory';
import FilterSidebar from './FilterSidebar';
import MetaData from '../Layouts/MetaData';
import GridView from './GridView';
import ListView from './ListView';
import SortBar from './SortBar';
import './Products.css';

const Products = () => {
    const params = useParams();
    const keyword = params.keyword || "";

    const [maxPrice, setMaxPrice] = useState(200000);
    const [price, setPrice] = useState([0, 200000]);
    const [category, setCategory] = useState("");
    const [categories, setCategories] = useState([]); // for top 5 departments
    const [ratings, setRatings] = useState(0);
    const [discount, setDiscount] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [sortOption, setSortOption] = useState('relevance');

    const [allProducts, setAllProducts] = useState([]);
    const [filteredProducts, setFilteredProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [viewMode, setViewMode] = useState('grid');

    const resultPerPage = viewMode === 'grid' ? 8 : 5;

    useEffect(() => {
        setLoading(true);
        setError(null);
        const fetchProducts = async () => {
            try {
                const { data } = await axios.get(`http://localhost:8000/search?q=${keyword}`);

                console.log(data);

                const topDepartments = (data.facets?.departments || [])
                    .sort((a, b) => b.doc_count - a.doc_count)
                    .slice(0, 5)
                    .map(dep => dep.key);

                setCategories(topDepartments);
                setCategory("");
                const products = data.results || [];

                const calculatedMaxPrice = products.reduce((max, p) => {
                    return p.final_price > max ? p.final_price : max;
                }, 0);

                setMaxPrice(calculatedMaxPrice);
                setPrice([0, calculatedMaxPrice*10]);
                setAllProducts(products);
                setViewMode(data.view_preference || 'grid');

            } catch (err) {
                setError(err.message);
                setAllProducts([]);
            } finally {
                setLoading(false);
            }
        };
        fetchProducts();
    }, [keyword]);

    useEffect(() => {
        let tempProducts = [...allProducts];

        if (price) {
            tempProducts = tempProducts.filter(p => p.final_price >= price[0] && p.final_price <= price[1]);
        }
        if (category) {
            tempProducts = tempProducts.filter(p => p.department === category);
        }
        if (ratings > 0) {
            tempProducts = tempProducts.filter(p => p.rating >= ratings);
        }
        if (discount > 0) {
            tempProducts = tempProducts.filter(p => p.discount_percentage >= discount);
        }

        switch (sortOption) {
            case 'popularity':
                tempProducts.sort((a, b) => b.bought_past_month - a.bought_past_month);
                break;
            case 'price_asc':
                tempProducts.sort((a, b) => a.final_price - b.final_price);
                break;
            case 'price_desc':
                tempProducts.sort((a, b) => b.final_price - a.final_price);
                break;
            case 'newest':
                // tempProducts.sort((a, b) => new Date(b.date_added) - new Date(a.date_added));
                break;
            case 'relevance':
            default:
                break;
        }

        setFilteredProducts(tempProducts);
        setCurrentPage(1);
    }, [allProducts, price, category, ratings, discount, sortOption]);

    const clearFilters = () => {
        setPrice([0, 200000]);
        setCategory("");
        setRatings(0);
        setDiscount(0);
        setSortOption('relevance');
    };

    const pageCount = Math.ceil(filteredProducts.length / resultPerPage);
    const currentPagedProducts = filteredProducts.slice((currentPage - 1) * resultPerPage, currentPage * resultPerPage);

    const renderProductView = () => {
        if (currentPagedProducts.length === 0 && !loading) {
            return (
                <div className="no-results-container">
                    <img draggable="false" className="no-results-image" src="https://static-assets-web.flixcart.com/www/linchpin/fk-cp-zion/img/error-no-search-results_2353c5.png" alt="No Results Found" />
                    <h1 className="no-results-title">Sorry, no results found!</h1>
                    <p className="no-results-subtitle">Please check the spelling or try searching for something else</p>
                </div>
            );
        }
        return viewMode === 'grid' ? <GridView products={currentPagedProducts} /> : <ListView products={currentPagedProducts} />;
    };

    return (
        <>
            <MetaData title="All Products | Search" />
            <MinCategory />
            <main className="products-page-main">
                <div className="products-page-layout">
                    <FilterSidebar
                        price={price}
                        priceHandler={(e, newPrice) => setPrice(newPrice)}
                        category={category}
                        setCategory={setCategory}
                        categories={categories}
                        ratings={ratings}
                        setRatings={setRatings}
                        discount={discount}
                        setDiscount={setDiscount}
                        clearFilters={clearFilters}
                        maxPrice={maxPrice}
                    />
                    <div className="products-column">
                        {loading ? <Loader /> : (
                            <div className="products-view">
                                <SortBar 
                                    totalResults={filteredProducts.length}
                                    keyword={keyword}
                                    sortOption={sortOption}
                                    setSortOption={setSortOption}
                                />
                                {renderProductView()}
                                {pageCount > 1 && (
                                    <div className="pagination-container">
                                        <Pagination
                                            count={pageCount}
                                            page={currentPage}
                                            onChange={(e, val) => setCurrentPage(val)}
                                            color="primary"
                                        />
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </>
    );
};

export default Products;