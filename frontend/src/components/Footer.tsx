import { Box, Typography } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        textAlign: 'center',
        py: 2,
        mt: 'auto',
      }}
    >
      <Typography variant="body2" color="textSecondary">
        © {new Date().getFullYear()} VIP Guild. Dashboard Footer Text here
      </Typography>
    </Box>
  );
};

export default Footer;