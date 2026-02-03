import { LineChart as RechartsLine, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

interface LineChartProps {
  data: Array<{ name: string; value: number }>;
  color?: string;
  height?: number;
  showAverage?: boolean;
  xAxisLabel?: string;
  yAxisLabel?: string;
}

const LineChart = ({ 
  data, 
  color = '#3b82f6', 
  height = 300,
  showAverage = false,
  xAxisLabel,
  yAxisLabel
}: LineChartProps) => {
  const average = showAverage 
    ? data.reduce((sum, item) => sum + item.value, 0) / data.length 
    : 0;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsLine data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="name" 
          label={xAxisLabel ? { value: xAxisLabel, position: 'insideBottom', offset: -5 } : undefined}
        />
        <YAxis 
          label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: 'insideLeft' } : undefined}
        />
        <Tooltip formatter={(value: number) => value.toLocaleString('pt-BR')} />
        <Legend />
        <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} />
        {showAverage && (
          <ReferenceLine 
            y={average} 
            stroke="#ef4444" 
            strokeDasharray="3 3" 
            label="Média" 
          />
        )}
      </RechartsLine>
    </ResponsiveContainer>
  );
};

export default LineChart;
