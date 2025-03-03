import { useState } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import EvaluationForm from './components/EvaluationForm';
import ResultsTable from './components/ResultsTable';
import './App.css';

// Create a simple fade-in effect with CSS instead of Framer Motion
const App = () => {
  const [results, setResults] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  // Same sample queries as in the backend
  const sampleQueries = [
    "Who introduced the theory of relativity?",
    "Who was the first computer programmer?",
    "What did Isaac Newton contribute to science?",
    "Who won two Nobel Prizes for research on radioactivity?",
    "What is the theory of evolution by natural selection?"
  ];

  // Same expected responses as in the backend
  const expectedResponses = [
    "Albert Einstein proposed the theory of relativity, which transformed our understanding of time, space, and gravity.",
    "Ada Lovelace is regarded as the first computer programmer for her work on Charles Babbage's early mechanical computer, the Analytical Engine.",
    "Isaac Newton formulated the laws of motion and universal gravitation, laying the foundation for classical mechanics.",
    "Marie Curie was a physicist and chemist who conducted pioneering research on radioactivity and won two Nobel Prizes.",
    "Charles Darwin introduced the theory of evolution by natural selection in his book 'On the Origin of Species'."
  ];

  const runEvaluation = async (apiEndpoint) => {
    try {
      setError(null);
      setIsLoading(true);
      setProgress(0);
      
      // Initialize dataset similar to backend
      const dataset = [];
      const totalQueries = sampleQueries.length;
      
      // Loop through queries just like the backend does
      for (const [index, query] of sampleQueries.entries()) {
        try {
          // Update progress for each query
          setProgress(Math.floor((index / totalQueries) * 100));
          
          // Perform request with same params structure as backend
          const params = new URLSearchParams({
            groupid: '12',
            query: query,
            session_id: '111'
          });
          
          const response = await fetch(`${apiEndpoint}?${params}`, {
            method: 'GET',
            headers: {
              'accept': 'application/json',
            },
          });
          
          if (!response.ok) {
            throw new Error(`Error fetching from API: ${response.statusText}`);
          }
          
          const data = await response.json();
          const answer = data.answer || 'No answer provided';
          
          // Add to dataset in same format as backend
          dataset.push({
            user_input: query,
            response: answer,
            reference: expectedResponses[index],
          });
        } catch (queryError) {
          // Handle individual query errors but continue with others
          if (typeof console !== 'undefined') {
            console.error(`Error with query "${query}":`, queryError);
          }
          dataset.push({
            user_input: query,
            response: `Error: ${queryError.message}`,
            reference: expectedResponses[index],
          });
        }
        
        // Small delay to make progress visible
        await new Promise(resolve => setTimeout(resolve, 200));
      }
      
      // Set progress to 100% when all queries are done
      setProgress(100);
      
      // Calculate metrics similar to backend
      const contextRecall = dataset.filter(d => d.response === d.reference).length / dataset.length;
      
      const evaluationMetrics = {
        "Context Recall": contextRecall,
        "Faithfulness": 0.92, // Using same placeholder metrics as backend
        "Factual Correctness": 0.88 // Using same placeholder metrics as backend
      };
      
      setResults(dataset);
      setMetrics(evaluationMetrics);
    } catch (error) {
      if (typeof console !== 'undefined') {
        console.error('API request error:', error);
      }
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header />
      
      <main className="container mx-auto px-6 py-8 flex-grow mt-16">
        <div className="animate-slideInUp animation-delay-300">
          <EvaluationForm onRunEvaluation={runEvaluation} isLoading={isLoading} />
          
          {isLoading && (
            <div className="mb-8 bg-white rounded-lg shadow-sm p-6 animate-fadeIn border border-gray-100">
              <h3 className="text-lg font-medium text-gray-800 mb-3">Evaluation in Progress</h3>
              <div className="mb-3 flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                <span className="text-sm font-medium text-primary-500">{progress}%</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-1.5 mb-4 overflow-hidden">
                <div 
                  className="bg-primary-500 h-1.5 rounded-full transition-all duration-300 relative"
                  style={{ width: `${progress}%` }}>
                  <span className="absolute inset-0 bg-white opacity-30 animate-pulse"></span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <svg className="animate-spin mr-2 h-4 w-4 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="text-sm text-gray-600">
                    Processing query {Math.min(Math.ceil(progress / 20), 5)} of 5
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  Estimated time remaining: {Math.max(5 - Math.ceil(progress / 20), 0)}s
                </span>
              </div>
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 border border-red-100 rounded-lg p-4 mb-8 animate-fadeIn animation-delay-100">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zm-1 9a1 1 0 01-1-1v-4a1 1 0 112 0v4a1 1 0 01-1 1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              </div>
            </div>
          )}
          
          {results.length > 0 && <ResultsTable results={results} metrics={metrics} />}
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default App;
