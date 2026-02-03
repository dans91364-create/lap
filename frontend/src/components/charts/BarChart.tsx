import { BarChart as RechartsBar, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface BarChartProps {
  data: Array<{ name: string; value: number }>;
  color?: string;
  height?: number;
  xAxisLabel?: string;
  yAxisLabel?: string;
}

const BarChart = ({ 
  data, 
  color = '#3b82f6', 
  height = 300,
  xAxisLabel,
  yAxisLabel
}: BarChartProps) => {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsBar data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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
        <Bar dataKey="value" fill={color} />
      </RechartsBar>
    </ResponsiveContainer>
  );
};

export default BarChart;
