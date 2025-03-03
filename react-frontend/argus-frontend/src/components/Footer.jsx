import React from 'react';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-white border-t border-gray-100 py-5 mt-auto backdrop-blur-sm">
      <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center">
        <div className="flex items-center space-x-2 mb-3 md:mb-0">
          <div className="w-1.5 h-1.5 rounded-full bg-primary-500 opacity-80"></div>
          <p className="text-xs font-medium text-gray-600">ARGUS RAG</p>
        </div>
        
        <p className="text-xs text-gray-500">
          &copy; {currentYear} Cybergen AI Technologies | <span className="text-primary-500">Privacy Policy</span>
        </p>
        
        <div className="hidden md:flex items-center mt-3 md:mt-0">
          <span className="text-xs text-gray-400">Version 1.0.1</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 