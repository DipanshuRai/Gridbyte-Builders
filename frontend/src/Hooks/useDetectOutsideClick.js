import { useEffect, useRef } from 'react';

/**
 * A custom hook that detects a click outside of a specified element.
 * @param {React.RefObject<HTMLElement>} ref - The ref of the element to monitor.
 * @param {() => void} handler - The function to call when a click outside is detected.
 */
export const useDetectOutsideClick = (ref, handler) => {
  useEffect(() => {
    const listener = (event) => {
      // Do nothing if the click is inside the ref's element or its descendants
      if (!ref.current || ref.current.contains(event.target)) {
        return;
      }
      // Otherwise, call the provided handler function
      handler(event);
    };

    // Add the event listeners
    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    // Cleanup function to remove the listeners when the component unmounts
    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
    // The dependency array ensures this effect runs only when the ref or handler changes.
  }, [ref, handler]);
};