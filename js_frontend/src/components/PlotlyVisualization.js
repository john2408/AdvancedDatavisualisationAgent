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
  if (spec.data && Array.isArray(spec.data)) {
    plotlyData = spec.data;
  } else if (spec.data && spec.data.x && spec.data.y) {
    plotlyData = [{
      x: spec.data.x,
      y: spec.data.y,
      type: spec.type || 'bar',
      name: spec.data.name || '',
    }];
  } else {
    plotlyData = [{ x: [], y: [], type: spec.type || 'bar', name: '' }];
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