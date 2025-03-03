import React from 'react';
import Logo from './Logo';
import { motion } from 'framer-motion';

const Header = () => {
  return (
    <header className="bg-white shadow-md py-4">
      <div className="container mx-auto px-4 flex items-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center"
        >
          <Logo />
          <h1 className="text-2xl font-semibold text-gray-800">RAG Evaluation Dashboard</h1>
        </motion.div>
      </div>
    </header>
  );
};

export default Header; 