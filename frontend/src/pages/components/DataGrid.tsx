import * as React from 'react';
import { DataGrid, GridRowsProp, GridColDef } from '@mui/x-data-grid';
import { Box, Typography } from '@mui/material';

const rows: GridRowsProp = [
  { id: 1, name: 'Free', description: 'Community version' },
  { id: 2, name: 'Pro', description: 'Commercial version with extra features' },
  { id: 3, name: 'Premium', description: 'All features unlocked' },
];

const columns: GridColDef[] = [
  { field: 'name', headerName: 'Edition', width: 150 },
  { field: 'description', headerName: 'Description', width: 300 },
];

const DataGridDemo: React.FC = () => {
  return (
    <Box sx={{ width: '100%', p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Product Versions
      </Typography>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSizeOptions={[5]}
        initialState={{
          pagination: { paginationModel: { pageSize: 5, page: 0 } },
        }}
      />
    </Box>
  );
};

export default DataGridDemo;
