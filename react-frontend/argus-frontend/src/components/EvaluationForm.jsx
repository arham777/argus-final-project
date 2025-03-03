import React, { useState } from 'react';

const EvaluationForm = ({ onRunEvaluation, isLoading }) => {
  const [apiEndpoint, setApiEndpoint] = useState('http://10.229.222.15:8000/knowledgebase');
  const [isFocused, setIsFocused] = useState(false);

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
    <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-100 transition-all duration-200 hover:shadow-md">
      <div className="flex items-center mb-4">
        <div className="w-1 h-5 bg-primary-500 rounded-full mr-2"></div>
        <h2 className="text-lg font-medium text-gray-800">Configure Evaluation</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="animate-fadeIn">
        <div className="mb-5">
          <label 
            htmlFor="apiEndpoint" 
            className={`block text-sm transition-all duration-200 ${
              isFocused ? 'text-primary-500 font-medium' : 'text-gray-600 font-normal'
            } mb-2`}
          >
            API Endpoint URL
          </label>
          <div className={`relative transition-all duration-300 ${
            isFocused ? 'transform -translate-y-1' : ''
          }`}>
            <input
              type="text"
              id="apiEndpoint"
              value={apiEndpoint}
              onChange={(e) => setApiEndpoint(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              className={`w-full px-4 py-2 bg-gray-50 border transition-all duration-200 ${
                isFocused 
                  ? 'border-primary-400 shadow-sm ring-1 ring-primary-200'
                  : 'border-gray-200'
              } rounded-md focus:outline-none`}
              placeholder="Enter API endpoint URL"
              required
            />
            {isFocused && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-primary-400">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
            )}
          </div>
          <div className="text-xs text-gray-400 mt-1 ml-1">
            Enter the URL of your RAG API endpoint
          </div>
        </div>
        
        <button
          type="submit"
          className={`px-6 py-2 bg-white border border-primary-400 text-primary-500 font-medium rounded-md 
            transition-all duration-300 hover:bg-primary-500 hover:text-white hover:shadow-md
            focus:outline-none focus:ring-2 focus:ring-primary-300 focus:ring-offset-2 
            transform ${isLoading ? 'opacity-70 cursor-not-allowed' : 'hover:-translate-y-0.5'}`}
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : (
            <span className="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Run Evaluation
            </span>
          )}
        </button>
      </form>
    </div>
  );
};

export default EvaluationForm; 