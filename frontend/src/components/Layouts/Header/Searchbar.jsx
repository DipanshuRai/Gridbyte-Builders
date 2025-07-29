import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import axiosInstance from '../../../utils/axiosInstance';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import MicIcon from '@mui/icons-material/Mic';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

import { useDetectOutsideClick } from '../../../Hooks/useDetectOutsideClick';
import './Searchbar.css';

const Searchbar = () => {
    const [keyword, setKeyword] = useState("");
    const [searchHistory, setSearchHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);

    const navigate = useNavigate();
    const searchContainerRef = useRef(null);
    const searchInputRef = useRef(null);
    const silenceTimerRef = useRef(null);
    const lastTranscriptRef = useRef("");

    useDetectOutsideClick(searchContainerRef, () => setShowHistory(false));

    const { isAuthenticated } = useSelector((state) => state.user);

    // Speech recognition hook setup
    const {
        transcript,
        listening,
        resetTranscript,
        browserSupportsSpeechRecognition
    } = useSpeechRecognition();

    useEffect(() => {
        setKeyword(transcript);
    }, [transcript]);

    // Auto-stop mechanism when user stops speaking
    useEffect(() => {
        if (!listening) return;

        if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
        }

        if (transcript === lastTranscriptRef.current) {
            silenceTimerRef.current = setTimeout(() => {
                if (listening) {
                    SpeechRecognition.stopListening();
                }
            }, 2000);
        } else {
            lastTranscriptRef.current = transcript;
        }

        return () => {
            if (silenceTimerRef.current) {
                clearTimeout(silenceTimerRef.current);
            }
        };
    }, [transcript, listening]);

    useEffect(() => {
        return () => {
            if (silenceTimerRef.current) {
                clearTimeout(silenceTimerRef.current);
            }
        };
    }, []);

    useEffect(() => {
        let maxDurationTimer;
        
        if (listening) {
            maxDurationTimer = setTimeout(() => {
                SpeechRecognition.stopListening();
            }, 30000);
        }

        return () => {
            if (maxDurationTimer) {
                clearTimeout(maxDurationTimer);
            }
        };
    }, [listening]);

    const fetchHistory = async () => {
        if (!isAuthenticated) return;
        try {
            const { data } = await axiosInstance.get('/api/v1/history');
            if (data.success) {
                setSearchHistory(data.history);
            }
        } catch (error) {
            console.error("Failed to fetch search history", error);
        }
    };

    const saveSearch = async (query) => {
        if (!isAuthenticated || !query.trim()) return;
        try {
            await axiosInstance.post('/api/v1/history', { query });
        } catch (error) {
            console.error("Failed to save search history", error);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
        }
        
        if (listening) {
            SpeechRecognition.stopListening();
        }
        
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

    // Shows the history dropdown when the input is focused
    const handleFocus = () => {
        setShowHistory(true);
        fetchHistory();
    };

    // Handles clicking on a search history item
    const handleHistoryClick = (query) => {
        setKeyword(query);
        navigate(`/products/${query}`);
        setShowHistory(false);
    };

    // Toggles continuous voice search on and off
    const handleVoiceSearch = (e) => {
        e.preventDefault();
        
        if (listening) {
            if (silenceTimerRef.current) {
                clearTimeout(silenceTimerRef.current);
            }
            SpeechRecognition.stopListening();
        } else {
            resetTranscript();
            lastTranscriptRef.current = "";
            SpeechRecognition.startListening({ 
                continuous: true, 
                language: 'en-US'
            });
        }
        
        if (searchInputRef.current) {
            searchInputRef.current.focus();
        }
    };

    if (!browserSupportsSpeechRecognition) {
        return null;
    }

    return (
        <div ref={searchContainerRef} className="search-container">
            <form onSubmit={handleSubmit} className="searchbar">
                <button type="submit" className="search-button" title="Search">
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

                <button
                    type="button"
                    onClick={handleVoiceSearch}
                    className={`mic-button ${listening ? 'listening' : ''}`}
                    title="Search by voice"
                >
                    <MicIcon />
                </button>
            </form>

            {showHistory && isAuthenticated && searchHistory.length > 0 && (
                <ul className="search-history-list">
                    {searchHistory.map((query, index) => (
                        <li
                            key={index}
                            className="search-history-item"
                            onMouseDown={() => handleHistoryClick(query)}
                        >
                           <HistoryIcon sx={{ fontSize: '18px', color: '#878787' }}/>
                           <span>{query}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Searchbar;