import React from 'react';
import styled from 'styled-components';
import Plot from 'react-plotly.js';

const VisualizationContainer = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  margin: 1rem 0;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
`;

const VizHeader = styled.div`
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background-color: #f8fafc;
  
  h3 {
    margin: 0;
    color: #1f2937;
    font-size: 1.1rem;
  }
`;

const VizContent = styled.div`
  padding: 1rem;
  min-height: 450px;
  height: auto;
  width: 100%;
  
  @media (max-width: 768px) {
    padding: 0.5rem;
    min-height: 350px;
  }
`;

const ErrorMessage = styled.div`
  padding: 2rem;
  text-align: center;
  color: #ef4444;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  margin: 1rem;
`;

const PlotlyVisualization = ({ plotSpec, title, isLoading = false }) => {
  console.log('🔍 PlotlyVisualization received:', { 
    plotSpec: typeof plotSpec === 'string' ? plotSpec.substring(0, 200) + '...' : plotSpec, 
    title, 
    isLoading 
  });

  if (isLoading) {
    return (
      <VisualizationContainer>
        <VizHeader>
          <h3>🎨 Creating Visualization...</h3>
        </VizHeader>
        <VizContent>
          <div style={{ 
            height: '300px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: '#6b7280'
          }}>
            <div>
              <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📊</div>
              <div>Generating your visualization...</div>
            </div>
          </div>
        </VizContent>
      </VisualizationContainer>
    );
  }

  if (!plotSpec) {
    console.log('⚠️ PlotlyVisualization: No plotSpec provided');
    return null;
  }

  try {
    // Parse the backend plot specification
    let spec;
    if (typeof plotSpec === 'string') {
      spec = JSON.parse(plotSpec);
    } else if (plotSpec.plot_spec) {
      spec = typeof plotSpec.plot_spec === 'string' ? JSON.parse(plotSpec.plot_spec) : plotSpec.plot_spec;
    } else {
      spec = plotSpec;
    }
    
    console.log('✅ Parsed spec:', { type: spec.type, hasData: !!spec.data, hasLayout: !!spec.layout });

    // Simple data conversion - directly use the backend format
    const plotlyData = [{
      x: spec.data.x || [],
      y: spec.data.y || [],
      type: spec.type || 'bar',
      marker: { 
        color: '#3b82f6',
        line: { width: 1, color: '#1f2937' }
      },
      name: ''
    }];

    // Simple layout - keep it minimal like your sample
    const plotlyLayout = {
      title: title || spec.layout?.title || 'Data Visualization',
      autosize: true,
      font: { 
        family: 'Arial, sans-serif',
        color: '#1f2937'
      },
      paper_bgcolor: '#ffffff',
      plot_bgcolor: '#ffffff',
      showlegend: false,
      margin: { l: 60, r: 40, t: 80, b: 60 }
    };

    // Minimal config like your sample
    const plotlyConfig = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false
    };
    
    console.log('📊 Final data:', plotlyData);
    console.log('🎨 Final layout:', plotlyLayout.title);

    return (
      <VisualizationContainer>
        <VizHeader>
          <h3>✨ {title || 'Data Visualization'}</h3>
        </VizHeader>
        
        {/* Debug section */}
        <div style={{ 
          background: '#f0f9ff', 
          padding: '0.5rem', 
          margin: '0 1rem', 
          fontSize: '0.8rem',
          borderLeft: '3px solid #0ea5e9'
        }}>
          <strong>🐛 PLOTLY DEBUG:</strong>
          <div>Data: x({plotlyData[0].x.length}) y({plotlyData[0].y.length}) type({plotlyData[0].type})</div>
          <div>Title: {plotlyLayout.title}</div>
        </div>
        
        <VizContent>
          <Plot
            data={plotlyData}
            layout={plotlyLayout}
            config={plotlyConfig}
            style={{ 
              width: '100%', 
              height: '400px'
            }}
            useResizeHandler={true}
            onError={(error) => {
              console.error('📊 Plotly render error:', error);
            }}
            onInitialized={(figure, graphDiv) => {
              console.log('📊 Plotly initialized successfully');
            }}
          />
        </VizContent>
      </VisualizationContainer>
    );
      
  } catch (error) {
    console.error('💥 Error rendering Plotly visualization:', error);
    console.error('📋 plotSpec was:', plotSpec);
    
    return (
      <VisualizationContainer>
        <VizHeader>
          <h3>❌ Visualization Error</h3>
        </VizHeader>
        <ErrorMessage>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⚠️</div>
          <div><strong>Unable to render visualization</strong></div>
          <div style={{ fontSize: '0.9rem', marginTop: '0.5rem', color: '#6b7280' }}>
            {error.message}
          </div>
        </ErrorMessage>
      </VisualizationContainer>
    );
  }
};

export default PlotlyVisualization;