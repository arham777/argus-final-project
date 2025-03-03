import React from 'react';
import jsPDF from 'jspdf';

const ResultsTable = ({ results, metrics }) => {
  const tableRef = React.useRef();
  const metricsRef = React.useRef();
  const containerRef = React.useRef();
  
  // High-quality PDF generation function
  const downloadPDF = async () => {
    if (!results || results.length === 0) return;
    
    let loadingElement = null;
    
    try {
      // Show loading indicator
      loadingElement = document.createElement('div');
      loadingElement.className = 'fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50';
      loadingElement.innerHTML = '<div class="bg-white p-4 rounded-md shadow-md">Generating high-quality PDF...</div>';
      document.body.appendChild(loadingElement);
      
      // Set up PDF document
      const doc = new jsPDF({
        orientation: 'landscape',
        unit: 'mm',
        format: 'a4',
        compress: true,
        precision: 2
      });
      
      // Get page dimensions
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 15;
      
      // Add document metadata
      doc.setProperties({
        title: 'ARGUS RAG Evaluation Results',
        subject: 'Evaluation Results for RAG System',
        author: 'ARGUS System',
        creator: 'ARGUS RAG Evaluation Dashboard'
      });
      
      // Create professional header
      doc.setFillColor(0, 102, 255); // Primary blue header
      doc.rect(0, 0, pageWidth, 20, 'F');
      
      doc.setTextColor(255, 255, 255); // White text for header
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(16);
      doc.text('ARGUS RAG Evaluation Results', margin, 13);
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Generated: ${new Date().toLocaleString()}`, pageWidth - margin - 50, 13, { align: 'right' });
      
      // Current Y position tracker
      let yPos = 30;
      
      // Add metrics section with professional styling
      if (metrics) {
        // Section title
        doc.setTextColor(70, 70, 70);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(12);
        doc.text('Evaluation Metrics', margin, yPos);
        yPos += 8;
        
        // Create metrics table - professional bordered style
        const metricWidth = (pageWidth - (margin * 2)) / 3;
        
        // Draw table header for metrics
        doc.setFillColor(240, 240, 240);
        doc.setDrawColor(220, 220, 220);
        doc.rect(margin, yPos, pageWidth - (margin * 2), 8, 'FD');
        
        // Add metric headers
        doc.setTextColor(70, 70, 70);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        let xPos = margin + 5;
        Object.keys(metrics).forEach((key, index) => {
          doc.text(key, xPos + (metricWidth * index), yPos + 5.5);
        });
        
        // Add metric values
        yPos += 8;
        doc.setFillColor(250, 250, 250);
        doc.rect(margin, yPos, pageWidth - (margin * 2), 10, 'FD');
        
        doc.setTextColor(0, 102, 255);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(12);
        xPos = margin + 5;
        Object.values(metrics).forEach((value, index) => {
          doc.text(`${(value * 100).toFixed(1)}%`, xPos + (metricWidth * index), yPos + 6.5);
        });
        
        yPos += 18; // Move past metrics section
      }
      
      // Create professional table header
      doc.setTextColor(70, 70, 70);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(12);
      doc.text('Results Table', margin, yPos);
      yPos += 8;
      
      // Create professional table directly, without using html2canvas
      // Define column widths for better formatting
      const colWidths = {
        userQuery: 60,
        generatedResponse: 100,
        referenceAnswer: 100
      };
      
      // Table header row
      doc.setFillColor(240, 240, 240);
      doc.setDrawColor(220, 220, 220);
      doc.rect(margin, yPos, pageWidth - (margin * 2), 10, 'FD');
      
      doc.setTextColor(70, 70, 70);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(10);
      
      let colX = margin + 5;
      doc.text('User Query', colX, yPos + 6);
      
      colX += colWidths.userQuery;
      doc.text('Generated Response', colX, yPos + 6);
      
      colX += colWidths.generatedResponse;
      doc.text('Reference Answer', colX, yPos + 6);
      
      yPos += 10;
      
      // Draw table data rows
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(50, 50, 50);
      
      const pageContentHeight = pageHeight - margin - 15;
      let currentPage = 1;
      
      // Function to add a new page with proper headers
      const addNewPage = () => {
        doc.addPage();
        currentPage++;
        
        // Add header to new page
        doc.setFillColor(0, 102, 255);
        doc.rect(0, 0, pageWidth, 20, 'F');
        
        doc.setTextColor(255, 255, 255);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(16);
        doc.text('ARGUS RAG Evaluation Results (Continued)', margin, 13);
        
        // Add table header on new page
        yPos = 30;
        
        doc.setFillColor(240, 240, 240);
        doc.setDrawColor(220, 220, 220);
        doc.rect(margin, yPos, pageWidth - (margin * 2), 10, 'FD');
        
        doc.setTextColor(70, 70, 70);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        
        let colX = margin + 5;
        doc.text('User Query', colX, yPos + 6);
        
        colX += colWidths.userQuery;
        doc.text('Generated Response', colX, yPos + 6);
        
        colX += colWidths.generatedResponse;
        doc.text('Reference Answer', colX, yPos + 6);
        
        yPos += 10;
        
        // Add footer
        addFooter(currentPage);
      };
      
      // Function to add footer to each page
      const addFooter = (pageNum) => {
        const totalPages = doc.getNumberOfPages();
        doc.setPage(pageNum);
        
        doc.setFillColor(240, 240, 240);
        doc.rect(0, pageHeight - 10, pageWidth, 10, 'F');
        
        doc.setTextColor(100, 100, 100);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.text(`© ${new Date().getFullYear()} ARGUS RAG Evaluation System`, margin, pageHeight - 3);
        doc.text(`Page ${pageNum} of ${totalPages}`, pageWidth - margin, pageHeight - 3, { align: 'right' });
      };
      
      // Helper function to add multiline text with wrapping
      const addWrappedText = (text, x, y, maxWidth, lineHeight) => {
        if (!text) return 0;
        
        const lines = doc.splitTextToSize(text, maxWidth);
        const totalHeight = lines.length * lineHeight;
        
        for (let i = 0; i < lines.length; i++) {
          doc.text(lines[i], x, y + (i * lineHeight));
        }
        
        return totalHeight;
      };
      
      // Process each result row
      for (let i = 0; i < results.length; i++) {
        const result = results[i];
        const rowHeight = 20; // Base row height
        const rowFill = i % 2 === 0 ? 255 : 245; // Alternate row colors
        
        // Check if we need to start a new page
        if (yPos + rowHeight > pageContentHeight) {
          addNewPage();
        }
        
        // Draw row background
        doc.setFillColor(rowFill, rowFill, rowFill);
        doc.setDrawColor(220, 220, 220);
        doc.rect(margin, yPos, pageWidth - (margin * 2), rowHeight, 'FD');
        
        // Draw text content with proper wrapping
        let colX = margin + 5;
        
        // User query
        doc.setTextColor(50, 50, 50);
        addWrappedText(result.user_input, colX, yPos + 5, colWidths.userQuery - 10, 4);
        
        // Generated response
        colX += colWidths.userQuery;
        addWrappedText(result.response, colX, yPos + 5, colWidths.generatedResponse - 10, 4);
        
        // Reference answer
        colX += colWidths.generatedResponse;
        addWrappedText(result.reference, colX, yPos + 5, colWidths.referenceAnswer - 10, 4);
        
        yPos += rowHeight;
      }
      
      // Add footer to first page
      addFooter(1);
      
      // Save the PDF
      doc.save('argus_rag_evaluation_results.pdf');
      
    } catch (error) {
      if (typeof console !== 'undefined') {
        console.error('Error generating PDF:', error);
      }
      alert('There was an error generating the PDF. Please try again.');
    } finally {
      // Clean up loading indicator
      if (loadingElement && document.body.contains(loadingElement)) {
        document.body.removeChild(loadingElement);
      }
    }
  };

  if (!results || results.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6" ref={containerRef}>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Evaluation Results</h2>
        
        <button
          onClick={downloadPDF}
          className="px-4 py-2 bg-secondary-700 text-white font-medium rounded-md shadow-sm hover:bg-secondary-800 focus:outline-none focus:ring-2 focus:ring-secondary-700 focus:ring-offset-2 transition-colors flex items-center hover:scale-105 active:scale-95"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clipRule="evenodd" />
          </svg>
          Download PDF
        </button>
      </div>

      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6" ref={metricsRef}>
          {Object.entries(metrics).map(([key, value]) => (
            <div key={key} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <h3 className="text-sm font-medium text-gray-500">{key}</h3>
              <p className="text-2xl font-semibold text-primary-600 mt-1">{(value * 100).toFixed(1)}%</p>
            </div>
          ))}
        </div>
      )}
      
      <div className="overflow-x-auto" ref={tableRef}>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                User Query
              </th>
              <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Generated Response
              </th>
              <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Reference Answer
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {results.map((result, index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-6 py-4 text-left whitespace-normal text-sm text-gray-900">{result.user_input}</td>
                <td className="px-6 py-4 text-left whitespace-normal text-sm text-gray-900">{result.response}</td>
                <td className="px-6 py-4 text-left whitespace-normal text-sm text-gray-900">{result.reference}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResultsTable; 