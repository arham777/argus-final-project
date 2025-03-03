import React from 'react';
import { motion } from 'framer-motion';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

const ResultsTable = ({ results, metrics }) => {
  const tableRef = React.useRef();
  const metricsRef = React.useRef();
  const containerRef = React.useRef();

  const downloadPDF = async () => {
    if (!containerRef.current || results.length === 0) return;

    try {
      // Show a loading indicator while generating PDF
      const element = document.createElement('div');
      element.className = 'fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50';
      element.innerHTML = '<div class="bg-white p-4 rounded-md shadow-md">Generating PDF...</div>';
      document.body.appendChild(element);

      // Create a new PDF document
      const pdfDoc = new jsPDF({
        orientation: 'landscape',
        unit: 'mm',
        format: 'a4',
        compress: true
      });
      
      // Ensure the autoTable plugin is available on pdfDoc
      if (typeof pdfDoc.autoTable !== 'function') {
        if (typeof console !== 'undefined') {
          console.log('Adding autoTable functionality to jsPDF');
        }
        // If autoTable isn't available on the instance, add it manually
        pdfDoc.autoTable = autoTable;
      }
      
      // Add PDF metadata
      pdfDoc.setProperties({
        title: 'ARGUS RAG Evaluation Results',
        subject: 'Evaluation of RAG system performance',
        author: 'ARGUS System',
        creator: 'ARGUS RAG Evaluation Dashboard'
      });
      
      // Page dimensions
      const pageWidth = pdfDoc.internal.pageSize.getWidth();
      const pageHeight = pdfDoc.internal.pageSize.getHeight();
      const margin = 15;
      const contentWidth = pageWidth - (margin * 2);
      
      // Add title
      pdfDoc.setFontSize(24);
      pdfDoc.setTextColor(0, 102, 255); // Primary blue
      pdfDoc.text('ARGUS RAG Evaluation Results', margin, margin + 5);
      
      // Add date
      pdfDoc.setFontSize(10);
      pdfDoc.setTextColor(100, 100, 100); // Gray
      const currentDate = new Date().toLocaleString();
      pdfDoc.text(`Generated on: ${currentDate}`, margin, margin + 12);
      
      // Add horizontal line
      pdfDoc.setDrawColor(0, 102, 255); // Primary blue
      pdfDoc.setLineWidth(0.5);
      pdfDoc.line(margin, margin + 15, pageWidth - margin, margin + 15);
      
      // Add metrics section
      if (metrics) {
        let yPos = margin + 20;
        
        // Title for metrics
        pdfDoc.setFontSize(16);
        pdfDoc.setTextColor(60, 60, 60); // Dark gray
        pdfDoc.text('Evaluation Metrics', margin, yPos);
        yPos += 8;
        
        // Background rectangle for metrics
        pdfDoc.setFillColor(245, 247, 250); // Light blue-gray background
        pdfDoc.setDrawColor(230, 230, 230); // Light gray border
        pdfDoc.setLineWidth(0.2);
        
        const metricsTableHeight = 15;
        pdfDoc.roundedRect(margin, yPos, contentWidth, metricsTableHeight, 3, 3, 'FD');
        
        // Add metrics data
        pdfDoc.setFontSize(12);
        pdfDoc.setTextColor(0, 0, 0);
        
        const metricSpacing = contentWidth / 3;
        Object.entries(metrics).forEach(([key, value], index) => {
          const xPos = margin + 10 + (index * metricSpacing);
          
          // Metric name
          pdfDoc.setFont(undefined, 'bold');
          pdfDoc.text(key, xPos, yPos + 6);
          
          // Metric value
          pdfDoc.setFont(undefined, 'normal');
          pdfDoc.setTextColor(0, 102, 255); // Primary blue
          pdfDoc.text(`${(value * 100).toFixed(1)}%`, xPos, yPos + 12);
          pdfDoc.setTextColor(0, 0, 0);
        });
        
        yPos += metricsTableHeight + 10;
        
        // Table title
        pdfDoc.setFontSize(16);
        pdfDoc.setTextColor(60, 60, 60); // Dark gray
        pdfDoc.text('Results Table', margin, yPos);
        yPos += 8;
        
        // Prepare table data for autotable
        const tableHeaders = [
          { header: 'User Query', dataKey: 'query' },
          { header: 'Generated Response', dataKey: 'response' },
          { header: 'Reference Answer', dataKey: 'reference' }
        ];
        
        const tableData = results.map(result => ({
          query: result.user_input,
          response: result.response,
          reference: result.reference
        }));
        
        // Add table using autotable plugin for perfect rendering
        try {
          pdfDoc.autoTable({
            startY: yPos,
            head: [['User Query', 'Generated Response', 'Reference Answer']],
            body: tableData.map(row => [row.query, row.response, row.reference]),
            headStyles: {
              fillColor: [245, 247, 250],
              textColor: [60, 60, 60],
              fontStyle: 'bold',
              halign: 'left'
            },
            alternateRowStyles: {
              fillColor: [250, 250, 250]
            },
            rowPageBreak: 'auto',
            bodyStyles: {
              valign: 'top'
            },
            columnStyles: {
              0: { cellWidth: 45 },
              1: { cellWidth: 90 },
              2: { cellWidth: 90 }
            },
            margin: { left: margin, right: margin },
            styles: {
              overflow: 'linebreak',
              cellPadding: 4,
              fontSize: 10,
              font: 'helvetica',
              textColor: [60, 60, 60],
              lineColor: [220, 220, 220],
              lineWidth: 0.1
            },
            didDrawPage: function(data) {
              // Add header to each page
              pdfDoc.setFontSize(8);
              pdfDoc.setTextColor(100, 100, 100);
              pdfDoc.text('ARGUS RAG Evaluation Results', margin, 10);
              
              // Add footer to each page
              pdfDoc.text(`© ${new Date().getFullYear()} ARGUS RAG Evaluation System`, margin, pageHeight - 10);
              pdfDoc.text(`Page ${data.pageNumber} of ${data.pageCount}`, pageWidth - margin, pageHeight - 10, { align: 'right' });
            }
          });
        } catch (tableError) {
          // Fallback to manual table rendering if autoTable fails
          if (typeof console !== 'undefined') {
            console.error('Error with autoTable, using fallback table rendering', tableError);
          }
          
          // Use html2canvas as fallback
          const canvas = await html2canvas(tableRef.current, {
            scale: 2,
            useCORS: true,
            logging: false,
            backgroundColor: '#ffffff'
          });
          
          // Calculate dimensions while preserving aspect ratio
          const imgData = canvas.toDataURL('image/jpeg', 1.0);
          const imageWidth = contentWidth;
          const imageHeight = (canvas.height * imageWidth) / canvas.width;
          
          // Add table image
          pdfDoc.addImage(imgData, 'JPEG', margin, yPos, imageWidth, Math.min(imageHeight, pageHeight - yPos - margin - 10));
          
          // Add a note about the rendering
          pdfDoc.setFontSize(8);
          pdfDoc.setTextColor(100, 100, 100);
          pdfDoc.text('* Table rendered as image due to compatibility issues.', margin, pageHeight - 15);
        }
      }
      
      // Save the PDF
      pdfDoc.save('argus_rag_evaluation_results.pdf');
      
      // Remove loading indicator
      document.body.removeChild(element);
    } catch (error) {
      // Add a check before using console
      if (typeof console !== 'undefined') {
        console.error('Error generating PDF:', error);
      }
      alert('There was an error generating the PDF. Please try again.');
    }
  };

  if (!results || results.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6" ref={containerRef}>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Evaluation Results</h2>
        
        <motion.button
          onClick={downloadPDF}
          className="px-4 py-2 bg-secondary-700 text-white font-medium rounded-md shadow-sm hover:bg-secondary-800 focus:outline-none focus:ring-2 focus:ring-secondary-700 focus:ring-offset-2 transition-colors flex items-center"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clipRule="evenodd" />
          </svg>
          Download PDF
        </motion.button>
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
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User Query
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Generated Response
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Reference Answer
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {results.map((result, index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-6 py-4 whitespace-normal text-sm text-gray-900">{result.user_input}</td>
                <td className="px-6 py-4 whitespace-normal text-sm text-gray-900">{result.response}</td>
                <td className="px-6 py-4 whitespace-normal text-sm text-gray-900">{result.reference}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResultsTable; 