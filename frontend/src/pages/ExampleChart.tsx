import { Box } from '@mui/material';

import ChartsOverviewDemo from './components/Chart';

// In the future, get data here and pass it to the Charts.

const ExampleChartPage: React.FC = () => {
  return (
    <Box display='flex' flexWrap='wrap'>
      <ChartsOverviewDemo />
    </Box>

  )
  };

export default ExampleChartPage;