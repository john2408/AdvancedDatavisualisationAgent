import React from 'react';
import PlotlyVisualizationComp from '../components/PlotlyVisualization';
import { PlotlyChartContainer } from '../styles/enhancedComponents';

export default function fallbackViz() {
  return (
    <PlotlyChartContainer>
      <PlotlyVisualizationComp
        plotSpec={{
          data: [
            {
              type: 'bar',
              x: ['AUDI', 'BMW', 'MERCEDES-BENZ'],
              y: [120, 150, 100],
              marker: { color: '#3b82f6' }
            }
          ],
          layout: {
            title: 'Number of Vehicles Registered by Car Manufacturers',
            xaxis: { title: 'manufacturer' },
            yaxis: { title: 'count' },
            barmode: 'group',
            showlegend: false,
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            font: { color: '#2E2E2E', family: 'Arial, sans-serif' },
            responsive: true
          }
        }}
        title={'Dummy Visualization'}
        isLoading={false}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
      />
    </PlotlyChartContainer>
  );
}
