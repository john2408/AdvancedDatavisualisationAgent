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
  
  @media (max-width: 768px) {
    padding: 0.5rem;
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
    return null;
  }

  try {
    // Parse plot specification if it's a string
    const spec = typeof plotSpec === 'string' ? JSON.parse(plotSpec) : plotSpec;
    const { type, data, layout } = spec;
    
    // Prepare Plotly data based on chart type
    let plotlyData = [];
    
    switch (type) {
      case 'bar':
        plotlyData = [{
          x: data.x || [],
          y: data.y || [],
          type: 'bar',
          marker: { 
            color: data.color || '#3b82f6',
            line: { width: 1, color: '#1f2937' }
          },
          hovertemplate: '<b>%{x}</b><br>Value: %{y}<extra></extra>',
          name: data.name || ''
        }];
        break;
        
      case 'pie':
        plotlyData = [{
          labels: data.labels || [],
          values: data.values || [],
          type: 'pie',
          hole: 0.3, // Donut style
          textinfo: 'label+percent',
          textposition: 'outside',
          hovertemplate: '<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percent}<extra></extra>',
          marker: {
            colors: data.colors || ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'],
            line: { width: 2, color: '#ffffff' }
          }
        }];
        break;
        
      case 'line':
        plotlyData = [{
          x: data.x || [],
          y: data.y || [],
          type: 'scatter',
          mode: 'lines+markers',
          line: { 
            color: data.color || '#3b82f6',
            width: 3
          },
          marker: {
            color: data.color || '#3b82f6',
            size: 6,
            line: { width: 1, color: '#ffffff' }
          },
          hovertemplate: '<b>%{x}</b><br>Value: %{y}<extra></extra>',
          name: data.name || ''
        }];
        break;
        
      case 'scatter':
        plotlyData = [{
          x: data.x || [],
          y: data.y || [],
          type: 'scatter',
          mode: 'markers',
          marker: {
            color: data.color || data.colors || '#3b82f6',
            size: data.size || 8,
            line: { width: 1, color: '#1f2937' },
            opacity: 0.7
          },
          hovertemplate: '<b>X: %{x}</b><br>Y: %{y}<extra></extra>',
          name: data.name || ''
        }];
        break;
        
      case 'histogram':
        plotlyData = [{
          x: data.x || [],
          type: 'histogram',
          marker: { 
            color: data.color || '#3b82f6',
            line: { width: 1, color: '#1f2937' }
          },
          hovertemplate: 'Range: %{x}<br>Count: %{y}<extra></extra>',
          name: data.name || ''
        }];
        break;
        
      case 'box':
        plotlyData = [{
          y: data.y || [],
          x: data.x || [],
          type: 'box',
          marker: { color: data.color || '#3b82f6' },
          line: { color: '#1f2937' },
          name: data.name || ''
        }];
        break;
        
      case 'heatmap':
        plotlyData = [{
          z: data.z || [],
          x: data.x || [],
          y: data.y || [],
          type: 'heatmap',
          colorscale: data.colorscale || 'Viridis',
          hovertemplate: 'X: %{x}<br>Y: %{y}<br>Value: %{z}<extra></extra>'
        }];
        break;
        
      default:
        throw new Error(`Unsupported chart type: ${type}`);
    }

    // Enhanced layout with responsive design
    const plotlyLayout = {
      title: {
        text: title || layout?.title || '',
        font: { 
          size: 18, 
          color: '#1f2937',
          family: 'Arial, sans-serif'
        },
        x: 0.5,
        xanchor: 'center'
      },
      font: { 
        family: 'Arial, sans-serif',
        color: '#1f2937'
      },
      paper_bgcolor: '#ffffff',
      plot_bgcolor: '#ffffff',
      margin: { 
        l: 60, 
        r: 40, 
        t: 60, 
        b: 60 
      },
      autosize: true,
      showlegend: type !== 'pie',
      legend: {
        orientation: 'h',
        y: -0.2,
        x: 0.5,
        xanchor: 'center'
      },
      xaxis: {
        title: layout?.xaxis?.title || '',
        gridcolor: '#f1f5f9',
        linecolor: '#d1d5db',
        tickfont: { color: '#4b5563' },
        titlefont: { color: '#1f2937' }
      },
      yaxis: {
        title: layout?.yaxis?.title || '',
        gridcolor: '#f1f5f9',
        linecolor: '#d1d5db',
        tickfont: { color: '#4b5563' },
        titlefont: { color: '#1f2937' }
      },
      hovermode: 'closest',
      ...layout
    };

    // Configuration for responsive behavior
    const plotlyConfig = {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: [
        'pan2d',
        'lasso2d',
        'select2d',
        'autoScale2d',
        'hoverClosestCartesian',
        'hoverCompareCartesian',
        'toggleSpikelines'
      ],
      displaylogo: false,
      toImageButtonOptions: {
        format: 'png',
        filename: 'chart',
        height: 600,
        width: 800,
        scale: 2
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
            style={{ 
              width: '100%', 
              height: '100%',
              minHeight: '400px'
            }}
            useResizeHandler={true}
          />
        </VizContent>
      </VisualizationContainer>
    );
    
  } catch (error) {
    console.error('Error rendering Plotly visualization:', error);
    return (
      <VisualizationContainer>
        <VizHeader>
          <h3>❌ Visualization Error</h3>
        </VizHeader>
        <ErrorMessage>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⚠️</div>
          <div>Unable to render visualization</div>
          <div style={{ fontSize: '0.8rem', marginTop: '0.5rem', color: '#6b7280' }}>
            {error.message}
          </div>
        </ErrorMessage>
      </VisualizationContainer>
    );
  }
};

export default PlotlyVisualization;
