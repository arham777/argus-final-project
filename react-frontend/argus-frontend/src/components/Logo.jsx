import React from 'react';

const Logo = () => {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      width="32" 
      height="32" 
      viewBox="0 0 32 32" 
      className="mr-2"
    >
      <rect width="32" height="32" rx="6" fill="#0066FF"/>
      <path d="M8 16H24M16 8V24" stroke="white" strokeWidth="3" strokeLinecap="round"/>
    </svg>
  );
};

export default Logo; 