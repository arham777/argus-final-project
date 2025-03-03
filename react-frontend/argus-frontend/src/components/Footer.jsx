import React from 'react';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-secondary-800 text-white py-6 mt-auto">
      <div className="container mx-auto px-4 text-center">
        <p className="text-sm">&copy; {currentYear} ARGUS RAG Evaluation System. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer; 