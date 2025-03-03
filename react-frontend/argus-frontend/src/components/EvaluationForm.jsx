import React, { useState } from 'react';
import { motion } from 'framer-motion';

const EvaluationForm = ({ onRunEvaluation, isLoading }) => {
  const [apiEndpoint, setApiEndpoint] = useState('http://10.229.222.15:8000/knowledgebase');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await onRunEvaluation(apiEndpoint);
    } catch (error) {
      if (typeof console !== 'undefined') {
        console.error('Error running evaluation:', error);
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Configure Evaluation</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="apiEndpoint" className="block text-sm font-medium text-gray-700 mb-1">
            API Endpoint URL
          </label>
          <input
            type="text"
            id="apiEndpoint"
            value={apiEndpoint}
            onChange={(e) => setApiEndpoint(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Enter API endpoint URL"
            required
          />
        </div>
        
        <motion.button
          type="submit"
          className="px-6 py-2 bg-primary-500 text-white font-medium rounded-md shadow-sm hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : (
            'Run Evaluation'
          )}
        </motion.button>
      </form>
    </div>
  );
};

export default EvaluationForm; 