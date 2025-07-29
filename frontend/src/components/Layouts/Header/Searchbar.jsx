import SearchIcon from '@mui/icons-material/Search';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Searchbar = () => {
    const [keyword, setKeyword] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        if(keyword.trim()){
            navigate(`/products/${keyword}`)
        } else {
            navigate('/products');
        }
    };

    const baseURL = process.env.REACT_APP_API_BASE_URL;
    // 🔍 Fetch autosuggestions
    useEffect(() => {
        const fetchSuggestions = async () => {
            if (keyword.trim() === "") {
                setSuggestions([]);
                return;
            }

            try {
                // const res = await axios.get(`http://localhost:8000/autosuggest?q=${keyword}`);
                const res = await axios.get(`${baseURL}/autosuggest?q=${keyword}`);
                setSuggestions(res.data.suggestions || []);
            } catch (err) {
                console.error("Autosuggest error:", err);
            }
        };

        const debounce = setTimeout(fetchSuggestions, 300); // ⏳ Debounce API calls
        return () => clearTimeout(debounce);
    }, [keyword]);

    // 🔁 When suggestion is clicked
    const handleSuggestionClick = (suggestion) => {
        setKeyword(suggestion);
        setSuggestions([]);
        navigate(`/products/${suggestion}`);
    };

    return (
        <div className="relative w-full sm:w-9/12">
            <form 
                onSubmit={handleSubmit} 
                className="px-1 sm:px-4 py-1.5 flex justify-between items-center shadow-md bg-white rounded-sm overflow-hidden"
            >
                <input 
                    value={keyword} 
                    onChange={(e) => setKeyword(e.target.value)} 
                    className="text-sm flex-1 outline-none border-none placeholder-gray-500" 
                    type="text" 
                    placeholder="Search for products, brands and more" 
                />
                <button type="submit" className="text-primary-blue"><SearchIcon /></button>
            </form>

            {/* 🔽 Suggestions Dropdown */}
            {suggestions.length > 0 && (
                <ul className="absolute top-full left-0 right-0 bg-white border shadow-lg z-10 max-h-60 overflow-y-auto">
                    {suggestions.map((item, index) => (
                        <li 
                            key={index} 
                            className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-sm"
                            onClick={() => handleSuggestionClick(item.suggestion)}
                        >
                            {item.suggestion}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Searchbar;

