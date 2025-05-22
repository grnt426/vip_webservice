import { Box } from '@mui/material';

import DataGridDemo from './components/DataGrid';

// In the future, get data here and pass it to the DataGrid.

const ExampleDataGridPage: React.FC = () => {
  return (
    <Box display='flex' flexWrap='wrap'>
      <DataGridDemo />
    </Box>
  )
  };

export default ExampleDataGridPage;