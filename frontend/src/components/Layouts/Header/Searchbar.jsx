import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchIcon from '@mui/icons-material/Search';
import MicIcon from '@mui/icons-material/Mic';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import './Searchbar.css';

const Searchbar = () => {
    const [keyword, setKeyword] = useState("");
    const navigate = useNavigate();

    const {
        transcript,
        listening,
        resetTranscript,
        browserSupportsSpeechRecognition
    } = useSpeechRecognition();

    // This useEffect will update the input field whenever the transcript changes.
    useEffect(() => {
        setKeyword(transcript);
    }, [transcript]);

    // Add this useEffect for debugging
    // useEffect(() => {
    //     console.log('Transcript:', transcript);
    //     console.log('Listening:', listening);
    // }, [transcript, listening]);


    const handleSubmit = (e) => {
        e.preventDefault();
        if (keyword.trim()) {
            navigate(`/products/${keyword}`);
        } else {
            navigate('/products');
        }
        resetTranscript();
    };

    // Toggles microphone on and off
    const handleVoiceSearch = (e) => {
        e.preventDefault(); // prevent form submission
        if (listening) {
            SpeechRecognition.stopListening();
        } else {
            resetTranscript();
            // Pass the language code for better accuracy, e.g., 'en-US'
            SpeechRecognition.startListening({ language: 'en-US' });
        }
    };

    if (!browserSupportsSpeechRecognition) {
        // Render nothing or a message if the browser doesn't support the API
        return null;
    }

    return (
        <form onSubmit={handleSubmit} className="searchbar">
            <button type="submit" className="search-button">
                <SearchIcon />
            </button>
            <input
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="search-input"
                type="text"
                placeholder={listening ? "Listening..." : "Search for products, brands and more"}
            />
            {/* The mic button is now a standard button to avoid form submission issues */}
            <button
                type="button" // Important: type="button" to prevent form submission
                onClick={handleVoiceSearch}
                className={`mic-button ${listening ? 'listening' : ''}`}
            >
                <MicIcon />
            </button>
        </form>
    );
};

export default Searchbar;