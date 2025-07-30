
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import axios from 'axios';
import axiosInstance from '../../../utils/axiosInstance';

import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import MicIcon from '@mui/icons-material/Mic';

import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { useDetectOutsideClick } from '../../../Hooks/useDetectOutsideClick';
import './Searchbar.css';

const Searchbar = () => {
    const [keyword, setKeyword] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const [searchHistory, setSearchHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);

    const navigate = useNavigate();
    const { isAuthenticated } = useSelector((state) => state.user);

    const searchContainerRef = useRef(null);
    const searchInputRef = useRef(null);
    const silenceTimerRef = useRef(null);
    const lastTranscriptRef = useRef("");

    useDetectOutsideClick(searchContainerRef, () => setShowHistory(false));

    const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();

    const baseURL = process.env.REACT_APP_API_BASE_URL;

    // 🟢 Handle autosuggestions
    useEffect(() => {
        const fetchSuggestions = async () => {
            if (!keyword.trim()) {
                setSuggestions([]);
                return;
            }

            try {
                const res = await axios.get(`${baseURL}/autosuggest?q=${keyword}`);
                setSuggestions(res.data.suggestions || []);
            } catch (err) {
                console.error("Autosuggest error:", err);
            }
        };

        const debounce = setTimeout(fetchSuggestions, 300);
        return () => clearTimeout(debounce);
    }, [keyword]);

    // 🟢 Speech recognition sets keyword
    useEffect(() => {
        setKeyword(transcript);
    }, [transcript]);

    // 🟢 Silence handling
    useEffect(() => {
        if (!listening) return;

        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

        if (transcript === lastTranscriptRef.current) {
            silenceTimerRef.current = setTimeout(() => {
                SpeechRecognition.stopListening();
            }, 2000);
        } else {
            lastTranscriptRef.current = transcript;
        }

        return () => clearTimeout(silenceTimerRef.current);
    }, [transcript, listening]);

    // 🟢 Max duration voice input
    useEffect(() => {
        let maxTimer;
        if (listening) {
            maxTimer = setTimeout(() => {
                SpeechRecognition.stopListening();
            }, 30000);
        }
        return () => clearTimeout(maxTimer);
    }, [listening]);

    const fetchHistory = async () => {
        if (!isAuthenticated) return;
        try {
            const { data } = await axiosInstance.get('/api/v1/history');
            if (data.success) setSearchHistory(data.history);
        } catch (err) {
            console.error("History fetch failed", err);
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
        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
        if (listening) SpeechRecognition.stopListening();

        if (keyword.trim()) {
            saveSearch(keyword);
            navigate(`/products/${keyword}`);
            setShowHistory(false);
        } else {
            navigate('/products');
        }

        resetTranscript();
        lastTranscriptRef.current = "";
        searchInputRef.current.blur();
    };

    const handleFocus = () => {
        setShowHistory(true);
        fetchHistory();
    };

    const handleVoiceSearch = (e) => {
        e.preventDefault();

        if (listening) {
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
            SpeechRecognition.stopListening();
        } else {
            resetTranscript();
            lastTranscriptRef.current = "";
            SpeechRecognition.startListening({ continuous: true, language: 'en-US' });
        }

        searchInputRef.current?.focus();
    };

    const handleSuggestionClick = (suggestion) => {
        setKeyword(suggestion);
        setSuggestions([]);
        saveSearch(suggestion);
        navigate(`/products/${suggestion}`);
    };

    const handleHistoryClick = (query) => {
        setKeyword(query);
        navigate(`/products/${query}`);
        setShowHistory(false);
    };

    if (!browserSupportsSpeechRecognition) return null;

    return (
        <div ref={searchContainerRef} className="relative w-full sm:w-9/12">
            <form onSubmit={handleSubmit} className="px-1 sm:px-4 py-1.5 flex justify-between items-center shadow-md bg-white rounded-sm overflow-hidden">
                <button type="submit" className="text-primary-blue"><SearchIcon /></button>

                <input
                    ref={searchInputRef}
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    onFocus={handleFocus}
                    className="text-sm flex-1 outline-none border-none placeholder-gray-500"
                    type="text"
                    placeholder={listening ? "Listening... speak now" : "Search for products, brands and more"}
                />

                <button type="button" onClick={handleVoiceSearch} className={`mic-button ${listening ? 'listening' : ''}`} title="Search by voice">
                    <MicIcon />
                </button>
            </form>


            {/* 🔽 Suggestions Dropdown */}
{suggestions.length > 0 && (
  <ul className="absolute top-full left-0 right-0 bg-white border shadow-lg z-10 max-h-60 overflow-y-auto rounded-md">
    {suggestions.map((item, index) => (
      <li
        key={index}
        onMouseDown={() => handleSuggestionClick(item.suggestion)}
        className="px-4 py-2 hover:bg-gray-100 cursor-pointer flex items-center gap-3"
      >
        {item.image && (
          <img
            src={item.image}
            alt="product"
            className="w-6 h-6 object-cover rounded"
          />
        )}

        <div className="flex flex-col">
          <span className="text-sm text-gray-800">{item.suggestion}</span>
          {item.type === "category" && (
            <span className="text-xs text-gray-500">(Category)</span>
          )}
        </div>
      </li>
    ))}
  </ul>
)}


            {/* 🕘 History */}
            {showHistory && isAuthenticated && searchHistory.length > 0 && (
                <ul className="search-history-list">
                    {searchHistory.map((query, index) => (
                        <li
                            key={index}
                            className="search-history-item"
                            onMouseDown={() => handleHistoryClick(query)}
                        >
                            <HistoryIcon sx={{ fontSize: '18px', color: '#878787' }} />
                            <span>{query}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Searchbar;


