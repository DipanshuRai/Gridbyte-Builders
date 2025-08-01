import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import axios from 'axios';
import axiosInstance from '../../../utils/axiosInstance';

import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import MicIcon from '@mui/icons-material/Mic';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';

import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { useDetectOutsideClick } from '../../../Hooks/useDetectOutsideClick';
import placeholderImage from '../../../assets/image-placeholder.png';
import './Searchbar.css';

const Searchbar = () => {
    const [keyword, setKeyword] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const [searchHistory, setSearchHistory] = useState([]);
    
    const navigate = useNavigate();
    const { isAuthenticated } = useSelector((state) => state.user);
    
    const searchContainerRef = useRef(null);
    const searchInputRef = useRef(null);
    const categoryDropdownRef = useRef(null);

    const [topDepartments, setTopDepartments] = useState([]);
    const [isCategoryDropdownVisible, setIsCategoryDropdownVisible] = useState(false);    
    
    const [isDropdownVisible, setIsDropdownVisible] = useState(false);

    useDetectOutsideClick(searchContainerRef, () => setIsDropdownVisible(false));
    useDetectOutsideClick(categoryDropdownRef, () => setIsCategoryDropdownVisible(false));

    const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();
    
    const baseURL = process.env.REACT_APP_API_BASE_URL;

    useEffect(() => {
        const fetchTopDepartments = async () => {
            try {
                const { data } = await axios.get(`${baseURL}/autosuggest/departments`);
                setTopDepartments(data.departments || []);
            } catch (err) {
                console.error("Failed to fetch top departments:", err);
            }
        };
        fetchTopDepartments();
    }, [baseURL]);

    useEffect(() => {
        const fetchSuggestions = async () => {
            if (!keyword.trim()) {
                setSuggestions([]);
                return;
            }
            try {
                const { data } = await axios.get(`${baseURL}/autosuggest?q=${keyword}`);
                console.log(data.suggestions);
                
                setSuggestions(data.suggestions || []);
            } catch (err) {
                console.error("Autosuggest error:", err);
                setSuggestions([]);
            }
        };
        const debounce = setTimeout(fetchSuggestions, 300);
        return () => clearTimeout(debounce);
    }, [keyword]);
    
    useEffect(() => {
        setKeyword(transcript);
    }, [transcript]);

    useEffect(() => {
        if (keyword.trim() === '' && isDropdownVisible) {
            fetchHistory();
        }
    }, [keyword, isDropdownVisible]);

    const fetchHistory = async () => {
        if (!isAuthenticated) return;
        try {
            const { data } = await axiosInstance.get('/api/v1/history');
            if (data.success) setSearchHistory(data.history);
        } catch (err) {
            console.error("History fetch failed", err);
        }
    };
    
    const handleFocus = () => {
        setIsDropdownVisible(true);
        if (!keyword.trim()) {
            fetchHistory();
        }
    };

    const saveSearch = async (query) => {
        if (!isAuthenticated || !query.trim()) return;
        try {
            await axiosInstance.post('/api/v1/history', { query });
        } catch (err) {
            console.error("Save search failed", err);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (listening) SpeechRecognition.stopListening();
        
        const finalKeyword = keyword.trim();
        if (finalKeyword) {
            saveSearch(finalKeyword);
            navigate(`/products/${finalKeyword}`);
        } else {
            navigate('/products');
        }
        
        setIsDropdownVisible(false);
        searchInputRef.current.blur();
        resetTranscript();
    };

    const handleVoiceSearch = (e) => {
        e.preventDefault();
        if (listening) {
            SpeechRecognition.stopListening();
        } else {
            resetTranscript();
            setKeyword("");
            SpeechRecognition.startListening({ continuous: true, language: 'en-US' });
        }
        searchInputRef.current?.focus();
    };
    
    const handleSuggestionClick = (item) => {
        const suggestionText = item.suggestion;
        setKeyword(suggestionText);
        setSuggestions([]);
        saveSearch(suggestionText); 
        navigate(`/products/${suggestionText}`);
        setIsDropdownVisible(false);
    };

    const handleHistoryClick = (query) => {
        setKeyword(query);
        navigate(`/products/${query}`);
        setIsDropdownVisible(false);
    };

    const handleCategorySelect = (department) => {
        setIsCategoryDropdownVisible(false);
        setKeyword(department);
        navigate(`/products/${department}`);
    };

    if (!browserSupportsSpeechRecognition) return null;

    const renderDropdownContent = () => {
        if (keyword.trim().length > 0 && suggestions.length > 0) {
            return suggestions.map((item, index) => (
                <li key={index} className="suggestion-item" onMouseDown={() => handleSuggestionClick(item)}>
                    <div className="suggestion-image-container">
                        {index < 4 ? (
                            <SearchIcon className="suggestion-icon" />
                        ) : item.image ? (
                            <img
                                src={item.image}
                                alt={item.suggestion}
                                className="suggestion-image"
                                onError={(e) => (e.target.src = placeholderImage)}
                            />
                        ) : (
                            <img
                                src={placeholderImage}
                                alt="No preview"
                                className="suggestion-image"
                            />
                        )}
                    </div>
                    <span className="suggestion-text">{item.suggestion}</span>
                </li>
            ));
        }

        if (isAuthenticated && searchHistory.length > 0) {
            return searchHistory.map((query, index) => (
                <li key={index} className="search-history-item" onMouseDown={() => handleHistoryClick(query)}>
                    <HistoryIcon className="history-icon" />
                    <span className="history-text">{query}</span>
                </li>
            ));
        }
        return null;
    };

    const dropdownContent = isDropdownVisible && (!keyword.trim() || (keyword.trim() && suggestions.length > 0)) ? renderDropdownContent() : null;

    return (
        <div ref={searchContainerRef} className="search-container">
            <form onSubmit={handleSubmit} className="searchbar">
                <div ref={categoryDropdownRef} className="category-dropdown-container">
                    <button type="button" className="category-dropdown-button" onClick={() => setIsCategoryDropdownVisible(!isCategoryDropdownVisible)}>
                        <span>All</span>
                        <ArrowDropDownIcon />
                    </button>
                    {isCategoryDropdownVisible && (
                        <ul className="category-dropdown-list">
                            {topDepartments.map((dept, i) => (
                                <li key={i} onMouseDown={() => handleCategorySelect(dept)}>
                                    {dept}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                <button type="submit" className="search-button">
                    <SearchIcon />
                </button>

                <input
                    ref={searchInputRef}
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    onFocus={handleFocus}
                    className="search-input"
                    type="text"
                    placeholder={listening ? "Listening... speak now" : "Search for products, brands and more"}
                />

                <button type="button" onClick={handleVoiceSearch} className={`mic-button ${listening ? 'listening' : ''}`} title="Search by voice">
                    <MicIcon />
                </button>
            </form>

            {dropdownContent && (
                <ul className="search-dropdown">
                    {dropdownContent}
                </ul>
            )}
        </div>
    );
};

export default Searchbar;