// hooks/useDetectOutsideClick.js
import { useState, useEffect, useRef } from 'react';

export const useDetectOutsideClick = (initialState) => {
  const triggerRef = useRef(null);
  const nodeRef = useRef(null);

  const [isActive, setIsActive] = useState(initialState);

  const handleClickOutside = (event) => {
    if (triggerRef.current && triggerRef.current.contains(event.target)) {
      return setIsActive(!isActive);
    }

    if (nodeRef.current && !nodeRef.current.contains(event.target)) {
      setIsActive(false);
    }
  };

  useEffect(() => {
    document.addEventListener('click', handleClickOutside, true);
    return () => {
      document.removeEventListener('click', handleClickOutside, true);
    };
  });

  return { triggerRef, nodeRef, isActive, setIsActive };
};