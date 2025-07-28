import styled from 'styled-components';

// Responsive breakpoints
export const breakpoints = {
  mobile: '768px',
  tablet: '1024px',
  desktop: '1440px'
};

// Media query helpers
export const media = {
  mobile: `@media (max-width: ${breakpoints.mobile})`,
  tablet: `@media (max-width: ${breakpoints.tablet})`,
  desktop: `@media (min-width: ${breakpoints.desktop})`
};

// Responsive Grid System
export const ResponsiveContainer = styled.div`
  display: grid;
  grid-template-columns: 400px 1fr;
  height: 100vh;
  font-family: 'Arial', sans-serif;
  background-color: #f8fafc;
  
  ${media.mobile} {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
    height: 100vh;
  }
`;

export const ResponsiveSidebar = styled.div`
  background-color: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  height: 100vh;
  
  ${media.mobile} {
    height: auto;
    max-height: 40vh;
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
  }
`;

export const ResponsiveMainPanel = styled.div`
  display: flex;
  flex-direction: column;
  padding: 1rem 2rem;
  overflow-y: auto;
  min-height: 0;
  
  ${media.mobile} {
    padding: 1rem;
    height: 60vh;
    overflow-y: auto;
  }
  
  ${media.tablet} {
    padding: 1.5rem;
  }
`;

export const ResponsiveMetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
  
  ${media.mobile} {
    grid-template-columns: 1fr;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }
`;

export const ResponsiveWelcomeButtons = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
  flex-wrap: wrap;
  
  ${media.mobile} {
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 1.5rem;
  }
`;

export const ResponsiveFollowUpGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.5rem;
  margin-top: 1rem;
  
  ${media.mobile} {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
`;

export const ResponsiveTableContainer = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  margin: 1rem 0;
  overflow: hidden;
  
  table {
    width: 100%;
    border-collapse: collapse;
    
    th, td {
      padding: 0.75rem;
      text-align: left;
      border-bottom: 1px solid #e2e8f0;
    }
    
    th {
      background-color: #f8fafc;
      font-weight: bold;
      color: #1f2937;
      position: sticky;
      top: 0;
      z-index: 1;
    }
    
    td {
      color: #4b5563;
    }
    
    ${media.mobile} {
      th, td {
        padding: 0.5rem;
        font-size: 0.9rem;
      }
    }
  }
  
  ${media.mobile} {
    overflow-x: auto;
    
    table {
      min-width: 600px;
    }
  }
`;

export const ResponsiveChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  overflow-y: auto;
  min-height: 0;
  
  ${media.mobile} {
    max-height: 25vh;
    padding: 0.75rem;
  }
`;

export const ResponsiveInputContainer = styled.div`
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
  background-color: #ffffff;
  position: sticky;
  bottom: 0;
  
  ${media.mobile} {
    padding: 0.75rem;
  }
`;

export const ResponsiveInputWrapper = styled.div`
  display: flex;
  gap: 0.5rem;
  align-items: center;
  
  ${media.mobile} {
    flex-direction: column;
    gap: 0.75rem;
    
    input {
      width: 100%;
    }
    
    div {
      display: flex;
      gap: 0.5rem;
      width: 100%;
      
      button {
        flex: 1;
      }
    }
  }
`;

// Responsive Typography
export const ResponsiveHeading = styled.h1`
  font-size: 2rem;
  color: #1f2937;
  margin-bottom: 1rem;
  
  ${media.mobile} {
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
  }
  
  ${media.tablet} {
    font-size: 1.75rem;
  }
`;

export const ResponsiveSubheading = styled.h2`
  font-size: 1.5rem;
  color: #1f2937;
  margin-bottom: 1rem;
  text-align: center;
  
  ${media.mobile} {
    font-size: 1.25rem;
    margin-bottom: 0.75rem;
  }
`;

export const ResponsiveText = styled.p`
  font-size: 1.1rem;
  color: #6b7280;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto 2rem auto;
  text-align: center;
  
  ${media.mobile} {
    font-size: 1rem;
    margin: 0 auto 1.5rem auto;
    padding: 0 1rem;
  }
`;

// Responsive Cards and Components
export const ResponsiveCard = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  
  ${media.mobile} {
    padding: 1rem;
  }
`;

export const ResponsiveButton = styled.button`
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  background-color: ${props => props.variant === 'primary' ? '#3b82f6' : '#6b7280'};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${props => props.variant === 'primary' ? '#2563eb' : '#4b5563'};
    transform: translateY(-1px);
  }
  
  &:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
    transform: none;
  }
  
  ${media.mobile} {
    padding: 0.875rem 1rem;
    font-size: 0.9rem;
    width: 100%;
  }
`;

export const ResponsiveFollowUpButton = styled(ResponsiveButton)`
  background-color: #f59e0b;
  color: #000000;
  font-size: 0.85rem;
  padding: 0.5rem 1rem;
  
  &:hover {
    background-color: #d97706;
  }
  
  ${media.mobile} {
    padding: 0.75rem 1rem;
    width: 100%;
    margin: 0;
  }
`;

// Loading States
export const ResponsiveLoadingSpinner = styled.div`
  text-align: center;
  padding: 2rem;
  color: #6b7280;
  
  ${media.mobile} {
    padding: 1.5rem;
    font-size: 0.9rem;
  }
`;

// Layout Utilities
export const HideOnMobile = styled.div`
  ${media.mobile} {
    display: none;
  }
`;

export const ShowOnMobile = styled.div`
  display: none;
  
  ${media.mobile} {
    display: block;
  }
`;

export const ResponsiveFlexContainer = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
  
  ${media.mobile} {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
`;
