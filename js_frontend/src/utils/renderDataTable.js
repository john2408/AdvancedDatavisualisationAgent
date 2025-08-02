import React from 'react';
import { ResponsiveTableContainer } from '../styles/ResponsiveLayout';

/**
 * Data Table Rendering Module - Handles displaying SQL query results as formatted tables
 */

/**
 * React component that renders SQL query data as a formatted table
 * Optimized with React.memo to prevent unnecessary re-renders
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of objects representing table rows
 * @param {Object} props.options - Optional configuration for table rendering
 * @returns {JSX.Element|null} - Rendered table component or null if no data
 */
export const DataTable = React.memo(({ data, options = {} }) => {
  console.log('🐛 DataTable component called with:', { dataLength: data?.length, options });
  
  // Validate input data
  if (!data || !Array.isArray(data) || data.length === 0) {
    console.warn('DataTable: No data provided or data is empty');
    return null;
  }

  // Validate that data contains objects
  if (!data[0] || typeof data[0] !== 'object') {
    console.warn('DataTable: Data must be an array of objects', { firstItem: data[0] });
    return null;
  }

  console.log('🐛 DataTable: Validation passed, rendering table...');

  const {
    maxRows = null, // Limit number of rows displayed
    formatNumbers = true, // Format numbers with commas/decimals
    capitalizeHeaders = true, // Capitalize and format headers
    showRowNumbers = false, // Show row index column
    className = '', // Additional CSS class
    title = null // Optional table title
  } = options;

  // Get column headers from first row
  const headers = Object.keys(data[0]);
  
  // Limit rows if specified
  const displayData = maxRows ? data.slice(0, maxRows) : data;
  
  // Format header text
  const formatHeader = (header) => {
    if (!capitalizeHeaders) return header;
    return header.replace(/_/g, ' ').toUpperCase();
  };

  // Format cell value
  const formatCellValue = (value) => {
    if (value === null || value === undefined) return '—';
    
    if (typeof value === 'number' && formatNumbers) {
      // Integer numbers: format with commas
      if (value % 1 === 0) {
        return value.toLocaleString();
      }
      // Decimal numbers: format with 2 decimal places
      return value.toFixed(2);
    }
    
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }
    
    return String(value);
  };

  try {
    return (
      <ResponsiveTableContainer className={className}>
        {title && <h3 style={{ marginBottom: '1rem', color: '#1f2937' }}>{title}</h3>}
        <table>
          <thead>
            <tr>
              {showRowNumbers && <th>#</th>}
              {headers.map(header => (
                <th key={header}>{formatHeader(header)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayData.map((row, index) => (
              <tr key={index}>
                {showRowNumbers && <td>{index + 1}</td>}
                {headers.map(header => (
                  <td key={header}>
                    {formatCellValue(row[header])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {maxRows && data.length > maxRows && (
          <p style={{ 
            textAlign: 'center', 
            color: '#6b7280', 
            marginTop: '1rem',
            fontSize: '0.9rem'
          }}>
            Showing {maxRows} of {data.length} rows
          </p>
        )}
      </ResponsiveTableContainer>
    );
  } catch (error) {
    console.error('Error rendering data table:', error);
    return (
      <div style={{ 
        padding: '1rem', 
        background: '#fef2f2', 
        border: '1px solid #fecaca',
        borderRadius: '0.5rem',
        color: '#dc2626'
      }}>
        <strong>Table Rendering Error:</strong> {error.message}
      </div>
    );
  }
});

export default DataTable;
