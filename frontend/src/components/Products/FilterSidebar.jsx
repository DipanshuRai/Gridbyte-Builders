import React, { useState } from 'react';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import Slider from '@mui/material/Slider';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import StarIcon from '@mui/icons-material/Star';
import { categories } from '../../utils/constants';
import './FilterSidebar.css';

const FilterSidebar = ({ price, priceHandler, category, setCategory, ratings, setRatings, clearFilters }) => {

    const [categoryToggle, setCategoryToggle] = useState(true);
    const [ratingsToggle, setRatingsToggle] = useState(true);

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
                    <div className="filter-section">
                        <span className="filter-section-title">PRICE</span>
                        <Slider
                            value={price}
                            onChange={priceHandler}
                            valueLabelDisplay="auto"
                            getAriaLabel={() => 'Price range slider'}
                            min={0}
                            max={200000}
                        />
                        <div className="price-inputs-container">
                            <span className="price-input-box">₹{price[0].toLocaleString()}</span>
                            <span className="price-input-separator">to</span>
                            <span className="price-input-box">₹{price[1].toLocaleString()}</span>
                        </div>
                    </div>

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
                                            <FormControlLabel value={el} control={<Radio size="small" />} label={<span className="radio-label">{el}</span>} key={i} />
                                        ))}
                                    </RadioGroup>
                                </FormControl>
                            </div>
                        )}
                    </div>

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