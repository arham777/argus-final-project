import React, { useRef, useEffect } from 'react';
import cybergenLogo from '../assets/cybergen-logo-black.svg';

const Logo = () => {
  const logoRef = useRef(null);
  
  useEffect(() => {
    const logo = logoRef.current;
    if (!logo) return;
    
    // Subtle entrance animation
    logo.style.opacity = '0';
    logo.style.transform = 'translateY(8px)';
    
    setTimeout(() => {
      logo.style.transition = 'all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
      logo.style.opacity = '1';
      logo.style.transform = 'translateY(0)';
    }, 100);
  }, []);
  
  return (
    <div className="relative">
      <img 
        ref={logoRef}
        src={cybergenLogo} 
        alt="Cybergen Logo" 
        className="h-7 w-auto filter drop-shadow-sm hover:drop-shadow-md transition-all duration-300"
      />
      <div className="absolute -bottom-1 -right-1 w-1.5 h-1.5 bg-primary-500 rounded-full opacity-80"></div>
    </div>
  );
};

export default Logo; 