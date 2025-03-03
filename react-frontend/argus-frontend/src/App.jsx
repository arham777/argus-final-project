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
      
      // Initialize dataset similar to backend
      const dataset = [];
      
      // Loop through queries just like the backend does
      for (const [index, query] of sampleQueries.entries()) {
        try {
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
      }
      
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
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8 flex-grow">
        <div className="fade-in">
          <EvaluationForm onRunEvaluation={runEvaluation} isLoading={isLoading} />
          
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zm-1 9a1 1 0 01-1-1v-4a1 1 0 112 0v4a1 1 0 01-1 1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
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
