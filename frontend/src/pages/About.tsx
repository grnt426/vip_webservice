import { useState } from 'react';
import { Box, Typography, Button } from '@mui/material';

const AboutPage: React.FC = () => {

  const [count, setCount] = useState(0);
  return (
    <>
    <Box display='flex' flexDirection='column'>
      <Typography variant="h6">About Us</Typography>
      <Typography variant="body1">Some text here.</Typography>
      <Box>
        <Button variant="contained" onClick={() => setCount((count) => (count >= 5) ? 0 : count + 1)}> Click Me {count}</Button>
      </Box>
    </Box>
    </>
  );
};

export default AboutPage;