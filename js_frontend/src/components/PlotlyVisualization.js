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
  min-width: 700px;
  max-width: 1000px;
  min-height: 500px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  position: relative;
  box-sizing: border-box;
`;


const PlotlyVisualizationComp = ({ plotSpec, title, isLoading = false }) => {
  // Loading state
  if (isLoading) {
    return (
      <VisualizationContainer>
        <VizHeader>
          <h3>🎨 Creating Visualization...</h3>
        </VizHeader>
        <VizContent>
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6b7280' }}>
            <div>Loading...</div>
          </div>
        </VizContent>
      </VisualizationContainer>
    );
  }

  if (!plotSpec) {
    return (
      <VisualizationContainer>
        <VizHeader>
          <h3>⚠️ No Visualization Data</h3>
        </VizHeader>
        <VizContent>
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6b7280' }}>
            No data to visualize
          </div>
        </VizContent>
      </VisualizationContainer>
    );
  }

  // Accept both backend and Plotly formats
  let spec = plotSpec;
  if (typeof plotSpec === 'string') {
    try { spec = JSON.parse(plotSpec); } catch { spec = {}; }
  } else if (plotSpec.plot_spec) {
    try { spec = typeof plotSpec.plot_spec === 'string' ? JSON.parse(plotSpec.plot_spec) : plotSpec.plot_spec; } catch { spec = {}; }
  }

  // Convert to Plotly format if needed
  let plotlyData = [];
  
  // Debug: Log the spec structure
  console.log('🐛 PlotlyVisualizationComp spec:', spec);
  console.log('🐛 spec.data:', spec.data);
  console.log('🐛 spec.type:', spec.type);
  console.log('🐛 spec.data.x exists?', spec.data && spec.data.x);
  console.log('🐛 spec.data.y exists?', spec.data && spec.data.y);
  console.log('🐛 Array.isArray(spec.data)?', Array.isArray(spec.data));
  
  if (spec.data && Array.isArray(spec.data)) {
    // Already in Plotly format
    plotlyData = spec.data;
    console.log('✅ Path 1: Using array format data:', plotlyData);
  } else if (spec.data && spec.data.x && spec.data.y) {
    // Backend format: data.x and data.y are arrays
    plotlyData = [{
      x: spec.data.x,
      y: spec.data.y,
      type: spec.type || 'bar',
      name: spec.data.name || '',
      marker: { color: spec.data.color || '#3b82f6' }
    }];
    console.log('✅ Path 2: Converted backend format to Plotly:', plotlyData);
  } else if (spec.x && spec.y) {
    // Alternative format: x and y directly on spec
    plotlyData = [{
      x: spec.x,
      y: spec.y,
      type: spec.type || 'bar',
      name: spec.name || '',
      marker: { color: spec.color || '#3b82f6' }
    }];
    console.log('✅ Path 3: Using direct x/y format:', plotlyData);
  } else {
    // Fallback: empty data
    plotlyData = [{ x: [], y: [], type: spec.type || 'bar', name: '' }];
    console.log('⚠️ Path 4: Using fallback empty data');
    console.log('🔍 spec keys:', Object.keys(spec || {}));
    console.log('🔍 spec.data keys:', Object.keys(spec.data || {}));
  }

  const plotlyLayout = {
    title: title || spec.layout?.title || 'Data Visualization',
    autosize: true,
    showlegend: plotlyData.length > 1,
    margin: { l: 60, r: 40, t: 80, b: 60 },
    font: { color: '#1f2937', family: 'Arial, sans-serif' },
    paper_bgcolor: '#ffffff',
    plot_bgcolor: '#ffffff',
    xaxis: {
      title: spec.layout?.xaxis?.title || '',
      showgrid: true,
      gridcolor: '#e5e7eb',
      tickangle: plotlyData[0]?.x?.length > 5 ? -45 : 0
    },
    yaxis: {
      title: spec.layout?.yaxis?.title || 'Value',
      showgrid: true,
      gridcolor: '#e5e7eb'
    }
    // No fixed height here; let container control it
  };

  const plotlyConfig = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
    toImageButtonOptions: {
      format: 'png',
      filename: 'visualization',
      height: 500,
      width: 800,
      scale: 1
    }
  };

  return (
    <VisualizationContainer>
      <VizHeader>
        <h3>✨ {title || 'Data Visualization'}</h3>
      </VizHeader>
      <VizContent>
        {/* Debug section - remove in production */}
        <div style={{ background: '#f0f9ff', padding: '0.5rem', margin: '0.5rem 0', fontSize: '0.8rem', border: '1px solid #0ea5e9' }}>
          <strong>🐛 DEBUG:</strong> Data points: {plotlyData[0]?.x?.length || 0}, 
          X: {JSON.stringify(plotlyData[0]?.x)}, 
          Y: {JSON.stringify(plotlyData[0]?.y)}
        </div>
        
        <Plot
          data={plotlyData}
          layout={plotlyLayout}
          config={plotlyConfig}
          style={{ width: '100%', height: '100%' }}
          useResizeHandler={true}
        />
      </VizContent>
    </VisualizationContainer>
  );
};

export default PlotlyVisualizationComp;