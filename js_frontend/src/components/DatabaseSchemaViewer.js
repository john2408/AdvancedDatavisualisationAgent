import React, { useState } from 'react';
import styled from 'styled-components';
import { FiChevronDown, FiChevronRight, FiDatabase } from 'react-icons/fi';
import { media } from '../styles/ResponsiveLayout';

const SchemaContainer = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  margin: 1rem 0;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
`;

const SchemaHeader = styled.div`
  padding: 1rem 1.5rem;
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: #f1f5f9;
  }
  
  h3 {
    margin: 0;
    color: #1f2937;
    font-size: 1rem;
    flex: 1;
  }
  
  ${media.mobile} {
    padding: 0.75rem 1rem;
    
    h3 {
      font-size: 0.9rem;
    }
  }
`;

const SchemaContent = styled.div`
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
  
  ${media.mobile} {
    padding: 1rem;
    max-height: 300px;
  }
`;

const SchemaText = styled.div`
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.85rem;
  line-height: 1.6;
  color: #374151;
  white-space: pre-wrap;
  
  h1, h2, h3, h4 {
    color: #1f2937;
    margin: 1rem 0 0.5rem 0;
  }
  
  h1 {
    font-size: 1.2rem;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.5rem;
  }
  
  h2 {
    font-size: 1.1rem;
    color: #3b82f6;
  }
  
  h3 {
    font-size: 1rem;
    color: #059669;
  }
  
  code {
    background-color: #f3f4f6;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    color: #dc2626;
  }
  
  pre {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1rem;
    overflow-x: auto;
    margin: 0.5rem 0;
    
    code {
      background: none;
      padding: 0;
      color: #374151;
    }
  }
  
  ul, ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
  }
  
  li {
    margin-bottom: 0.25rem;
  }
  
  strong {
    color: #1f2937;
    font-weight: 600;
  }
  
  em {
    color: #6b7280;
    font-style: italic;
  }
  
  ${media.mobile} {
    font-size: 0.8rem;
    
    pre {
      padding: 0.75rem;
      font-size: 0.75rem;
    }
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #6b7280;
  
  ${media.mobile} {
    padding: 1.5rem;
    font-size: 0.9rem;
  }
`;

const DatabaseSchemaViewer = ({ schema, isLoading = false, title = "📋 Database Schema" }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const formatSchemaText = (text) => {
    if (!text) return 'Schema not available';
    
    // Convert markdown-like formatting to basic styling
    return text
      .replace(/^## (.*$)/gm, '\n## $1\n')
      .replace(/^### (.*$)/gm, '\n### $1\n')
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .trim();
  };

  return (
    <SchemaContainer>
      <SchemaHeader onClick={toggleExpanded}>
        <FiDatabase />
        <h3>{title}</h3>
        {isExpanded ? <FiChevronDown /> : <FiChevronRight />}
      </SchemaHeader>
      
      {isExpanded && (
        <SchemaContent>
          {isLoading ? (
            <LoadingSpinner>
              <div>
                <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>📊</div>
                <div>Loading database schema...</div>
              </div>
            </LoadingSpinner>
          ) : (
            <SchemaText>
              {formatSchemaText(schema)}
            </SchemaText>
          )}
        </SchemaContent>
      )}
    </SchemaContainer>
  );
};

export default DatabaseSchemaViewer;
