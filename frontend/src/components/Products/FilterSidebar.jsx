import React, { useState } from 'react';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import Slider from '@mui/material/Slider';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import StarIcon from '@mui/icons-material/Star';
import './FilterSidebar.css';

const FilterSidebar = ({ price, priceHandler, category, setCategory, categories, ratings, setRatings, discount, setDiscount, clearFilters, maxPrice }) => {

    const [categoryToggle, setCategoryToggle] = useState(true);
    const [ratingsToggle, setRatingsToggle] = useState(true);
    const [discountToggle, setDiscountToggle] = useState(true);

    const discountOptions = [50, 40, 30, 20, 10];

    return (
        <div className="filter-sidebar">
            <div className="filter-container">
                <div className="filter-header">
                    <p className="filter-title">Filters</p>
                    <span className="filter-clear-all" onClick={clearFilters}>
                        clear all
                    </span>
                </div>

                <div className="filter-sections-wrapper">
                    
                    {/* Price Filter */}
                    <div className="filter-section">
                        <span className="filter-section-title">PRICE</span>
                        <Slider
                            value={price}
                            onChange={priceHandler}
                            valueLabelDisplay="auto"
                            getAriaLabel={() => 'Price range slider'}
                            min={0}
                            max={maxPrice}
                        />
                        <div className="price-inputs-container">
                            <span className="price-input-box">₹{price[0].toLocaleString()}</span>
                            <span className="price-input-separator">to</span>
                            <span className="price-input-box">₹{price[1].toLocaleString()}</span>
                        </div>
                    </div>

                    {/* Category Filter */}
                    <div className="filter-section">
                        <div className="filter-toggle-header" onClick={() => setCategoryToggle(!categoryToggle)}>
                            <p className="filter-section-title uppercase">Category</p>
                            {categoryToggle ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </div>
                        {categoryToggle && (
                            <div className="filter-options-container">
                                <FormControl>
                                    <RadioGroup
                                        aria-labelledby="category-radio-buttons-group"
                                        onChange={(e) => setCategory(e.target.value)}
                                        name="category-radio-buttons"
                                        value={category}
                                    >
                                        {categories.map((el, i) => (
                                            <FormControlLabel
                                                key={i}
                                                value={el}
                                                control={<Radio size="small" />}
                                                label={<span className="radio-label">{el}</span>}
                                            />
                                        ))}
                                    </RadioGroup>
                                </FormControl>
                            </div>
                        )}
                    </div>

                    {/* --- NEW DISCOUNT FILTER --- */}
                    <div className="filter-section">
                        <div className="filter-toggle-header" onClick={() => setDiscountToggle(!discountToggle)}>
                            <p className="filter-section-title uppercase">Discount</p>
                            {discountToggle ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </div>
                        {discountToggle && (
                            <div className="filter-options-container">
                                <FormControl>
                                    <RadioGroup
                                        aria-labelledby="discount-radio-buttons-group"
                                        onChange={(e) => setDiscount(e.target.value)}
                                        value={discount}
                                        name="discount-radio-buttons"
                                    >
                                        {discountOptions.map((el, i) => (
                                            <FormControlLabel value={el} key={i} control={<Radio size="small" />} label={<span className="radio-label">{el}% or more</span>} />
                                        ))}
                                    </RadioGroup>
                                </FormControl>
                            </div>
                        )}
                    </div>

                    {/* Ratings Filter */}
                    <div className="filter-section">
                        <div className="filter-toggle-header" onClick={() => setRatingsToggle(!ratingsToggle)}>
                            <p className="filter-section-title uppercase">ratings</p>
                            {ratingsToggle ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </div>
                        {ratingsToggle && (
                            <div className="filter-options-container">
                                <FormControl>
                                    <RadioGroup
                                        aria-labelledby="ratings-radio-buttons-group"
                                        onChange={(e) => setRatings(e.target.value)}
                                        value={ratings}
                                        name="ratings-radio-buttons"
                                    >
                                        {[4, 3, 2, 1].map((el, i) => (
                                            <FormControlLabel value={el} key={i} control={<Radio size="small" />} label={
                                                <span className="rating-label">
                                                    {el}<StarIcon sx={{ fontSize: "12px", margin: "0 0.5rem" }} /> & above
                                                </span>}
                                            />
                                        ))}
                                    </RadioGroup>
                                </FormControl>
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );
};

export default FilterSidebar;