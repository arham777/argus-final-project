import React, { useState, useEffect } from 'react';
import Logo from './Logo';

const Header = () => {
  const [scrolled, setScrolled] = useState(false);
  
  // Handle scroll effect for header
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header 
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ease-in-out py-3 backdrop-blur-sm ${
        scrolled ? 'bg-white/90 shadow-sm' : 'bg-white/80'
      }`}
    >
      <div className="container mx-auto flex items-center justify-between px-6">
        <div className="flex items-center space-x-2 animate-slideInLeft">
          <div className="overflow-hidden">
            <Logo />
          </div>
          <div className="h-7 w-px bg-gray-200 mx-2 opacity-70"></div>
          <h1 className="text-xl font-medium text-gray-800 tracking-tight">
            <span className="text-primary-500 font-semibold">RAG</span> Evaluation
          </h1>
        </div>
        
        <div className="animate-fadeIn opacity-0 animation-delay-500">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-500 tracking-wide">ARGUS System</span>
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 