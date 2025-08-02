import styled from 'styled-components';
import { ResponsiveCard, media } from './ResponsiveLayout';

// Enhanced Styled Components for remaining elements
export const SidebarHeader = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  
  h1 {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    
    ${media.mobile} {
      font-size: 1.25rem;
    }
  }
  
  p {
    margin: 0;
    color: #6b7280;
    font-size: 0.9rem;
    
    ${media.mobile} {
      font-size: 0.8rem;
    }
  }
`;

export const Message = styled.div`
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  max-width: 85%;
  word-wrap: break-word;
  
  ${props => props.isUser ? `
    background-color: #3b82f6;
    color: white;
    margin-left: auto;
    text-align: right;
  ` : `
    background-color: #f1f5f9;
    color: #1f2937;
    border: 1px solid #e2e8f0;
  `}
  
  ${media.mobile} {
    max-width: 95%;
    padding: 0.5rem;
    font-size: 0.9rem;
  }
`;

export const Input = styled.input`
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #000000;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  outline: none;
  
  &:focus {
    border-color: #3b82f6;
  }
  
  ${media.mobile} {
    width: 100%;
    margin-bottom: 0.5rem;
  }
`;

export const MetricCard = styled(ResponsiveCard)`
  h3 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    
    ${media.mobile} {
      font-size: 0.8rem;
    }
  }
  
  p {
    margin: 0;
    font-size: 1.5rem;
    font-weight: bold;
    color: #1f2937;
    
    ${media.mobile} {
      font-size: 1.25rem;
    }
  }
`;

export const WelcomeContainer = styled.div`
  text-align: center;
  padding: 3rem 2rem;
  
  ${media.mobile} {
    padding: 2rem 1rem;
  }
`;

export const FollowUpContainer = styled.div`
  margin-top: 2rem;
  
  h3 {
    color: #1f2937;
    margin-bottom: 1rem;
    
    ${media.mobile} {
      font-size: 1.1rem;
    }
  }
`;

// Responsive container for Plotly chart
export const PlotlyChartContainer = styled.div`
  width: 100%;
  min-width: 600px;
  max-width: 1000px;
  min-height: 600px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
`;

