import { BarChart } from '@mui/x-charts/BarChart';

const ChartsOverviewDemo: React.FC = () => {
  // Data will eventually be passed to this component from above...
  return (
    <BarChart
      series={[
        { data: [35, 44, 24, 34] },
        { data: [51, 6, 49, 30] },
        { data: [15, 25, 30, 50] },
        { data: [60, 50, 15, 25] },
      ]}
      height={290}
      xAxis={[{ data: ['Q1', 'Q2', 'Q3', 'Q4'] }]}
    />
  );
}

export default ChartsOverviewDemo;
