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
  width: 100%;
  height: 500px;
  display: flex;
  flex-direction: column;
`;

const TestPlotlyVisualization = ({ plotSpec, title, isLoading = false }) => {
  console.log('🔍 PlotlyVisualization received:', { 
    plotSpecType: typeof plotSpec,
    title, 
    isLoading,
    plotSpecPreview: typeof plotSpec === 'string' ? plotSpec.substring(0, 100) + '...' : plotSpec
  });

  if (isLoading) {
    return (
      <VisualizationContainer>
        <VizHeader>
          <h3>🎨 Creating Visualization...</h3>
        </VizHeader>
        <VizContent>
          <div style={{ 
            height: '100%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: '#6b7280'
          }}>
            <div>Loading...</div>
          </div>
        </VizContent>
      </VisualizationContainer>
    );
  }

  if (!plotSpec) {
    console.log('⚠️ PlotlyVisualization: No plotSpec provided');
    return (
      <VisualizationContainer>
        <VizHeader>
          <h3>⚠️ No Visualization Data</h3>
        </VizHeader>
        <VizContent>
          <div style={{ 
            height: '100%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: '#6b7280'
          }}>
            No data to visualize
          </div>
        </VizContent>
      </VisualizationContainer>
    );
  }

  try {
    // Extract the actual plot specification
    let spec;
    
    // Handle different input formats
    if (typeof plotSpec === 'string') {
      console.log('📝 Parsing plotSpec string');
      spec = JSON.parse(plotSpec);
    } else if (plotSpec.plot_spec) {
      console.log('📦 Extracting from wrapper format');
      spec = typeof plotSpec.plot_spec === 'string' ? JSON.parse(plotSpec.plot_spec) : plotSpec.plot_spec;
    } else {
      console.log('📋 Using direct spec object');
      spec = plotSpec;
    }
    
    console.log('✅ Parsed spec:', { 
      type: spec.type, 
      hasData: !!spec.data, 
      hasLayout: !!spec.layout,
      dataKeys: spec.data ? Object.keys(spec.data) : [],
      xLength: spec.data?.x?.length || 0,
      yLength: spec.data?.y?.length || 0
    });

    // Create Plotly data - simplified approach based on your sample
    const plotlyData = [{
      x: spec.data.x || [],
      y: spec.data.y || [],
      type: spec.type || 'bar',
      marker: { 
        color: '#3b82f6'
      },
      name: spec.data.name || ''
    }];

    // Create Plotly layout - minimal like your sample
    const plotlyLayout = {
      title: title || spec.layout?.title || 'Data Visualization',
      autosize: true,
      showlegend: false,
      margin: { l: 60, r: 40, t: 80, b: 60 },
      font: { color: '#1f2937' },
      paper_bgcolor: '#ffffff',
      plot_bgcolor: '#ffffff'
    };

    // Minimal config like your sample
    const plotlyConfig = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false
    };
    
    console.log('📊 Final data:', { 
      dataLength: plotlyData.length,
      firstTrace: {
        x: plotlyData[0].x.slice(0, 3),
        y: plotlyData[0].y.slice(0, 3),
        type: plotlyData[0].type
      }
    });

    return (
      <VisualizationContainer>
        <VizHeader>
          <h3>✨ {title || 'Data Visualization'}</h3>
        </VizHeader>
        
        {/* Debug info */}
        <div style={{ 
          background: '#f0f9ff', 
          padding: '0.5rem', 
          margin: '0 1rem', 
          fontSize: '0.8rem',
          borderLeft: '3px solid #0ea5e9'
        }}>
          <strong>🐛 PLOTLY DEBUG:</strong> 
          x({plotlyData[0].x.length}) y({plotlyData[0].y.length}) type({plotlyData[0].type})
          <br />Title: {plotlyLayout.title}
          <br />Data sample: x=[{plotlyData[0].x.slice(0, 2).join(', ')}...] y=[{plotlyData[0].y.slice(0, 2).join(', ')}...]
        </div>
        
        <VizContent>
          <div style={{ width: '100%', height: '100%' }}>
            <Plot
              data={plotlyData}
              layout={plotlyLayout}
              config={plotlyConfig}
              style={{ 
                width: '100%', 
                height: '100%'
              }}
              useResizeHandler={true}
              onError={(error) => {
                console.error('📊 Plotly render error:', error);
              }}
              onInitialized={(figure, graphDiv) => {
                console.log('📊 Plotly initialized successfully', { 
                  figureData: figure.data?.length || 0,
                  graphDivId: graphDiv?.id || 'none'
                });
              }}
            />
          </div>
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
        <VizContent>
          <div style={{ 
            height: '100%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            flexDirection: 'column',
            color: '#ef4444',
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '0.5rem',
            padding: '2rem'
          }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⚠️</div>
            <div><strong>Unable to render visualization</strong></div>
            <div style={{ fontSize: '0.9rem', marginTop: '0.5rem', color: '#6b7280' }}>
              {error.message}
            </div>
            <details style={{ marginTop: '1rem', fontSize: '0.8rem' }}>
              <summary style={{ cursor: 'pointer' }}>Debug Info</summary>
              <pre style={{ 
                background: '#f9fafb', 
                padding: '0.5rem', 
                borderRadius: '0.25rem',
                marginTop: '0.5rem',
                overflow: 'auto',
                maxHeight: '200px',
                textAlign: 'left'
              }}>
                {JSON.stringify(plotSpec, null, 2)}
              </pre>
            </details>
          </div>
        </VizContent>
      </VisualizationContainer>
    );
  }
};

export default TestPlotlyVisualization;