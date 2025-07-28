import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchIcon from '@mui/icons-material/Search';

const Searchbar = () => {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const navigate = useNavigate();

  // Fetch autosuggestions
  useEffect(() => {
    const fetchSuggestions = async () => {
      try {
        const res = await fetch(`http://localhost:4000/suggest?q=${query}`);
        const data = await res.json();
        setSuggestions(data.suggestions);
      } catch (err) {
        console.error("Error fetching suggestions:", err);
      }
    };

    if (query.trim().length > 0) fetchSuggestions();
    else setSuggestions([]);
  }, [query]);

  // Submit search
  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/products/${query}`);
      setSuggestions([]);
    } else {
      navigate('/products');
    }
  };

  // Click suggestion
  const handleSuggestionClick = (text) => {
    setQuery(text);
    navigate(`/products/${text}`);
    setSuggestions([]);
  };

  return (
    <div className="relative w-full sm:w-9/12">
      <form
        onSubmit={handleSubmit}
        className="w-full px-1 sm:px-4 py-1.5 flex justify-between items-center shadow-md bg-white rounded-sm overflow-hidden"
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="text-sm flex-1 outline-none border-none placeholder-gray-500"
          type="text"
          placeholder="Search for products, brands and more"
        />
        <button type="submit" className="text-primary-blue">
          <SearchIcon />
        </button>
      </form>

     
      {suggestions.length > 0 && (
        <ul className="absolute top-full left-0 w-full bg-white shadow-md rounded-b-sm border-t z-50 max-h-60 overflow-y-auto">
          {suggestions.map((s, i) => (
            <li
              key={i}
              onClick={() => handleSuggestionClick(s)}
              className="px-4 py-2 text-sm hover:bg-sky-100 cursor-pointer"
            >
              {s}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Searchbar;


