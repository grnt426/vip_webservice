import { Box, Typography, useTheme, Link } from '@mui/material';
import { FaDiscord } from 'react-icons/fa';

const Footer = () => {
  const theme = useTheme();

  return (
    <Box
      component="footer"
      sx={{
        textAlign: 'center',
        py: 3,
        mt: 'auto',
        borderTop: `1px solid ${theme.palette.primary.main}20`,
        background: `linear-gradient(0deg, ${theme.palette.background.paper} 0%, transparent 100%)`,
      }}
    >
      <Link 
        href="https://discord.gg/gw2vipcommunity"
        target="_blank"
        rel="noopener noreferrer"
        sx={{ 
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 1,
          color: '#7289DA',
          textDecoration: 'none',
          '&:hover': {
            textDecoration: 'underline'
          }
        }}
      >
        <FaDiscord size={24} />
        <Typography variant="body2">
          Join our Discord
        </Typography>
      </Link>
    </Box>
  );
};

export default Footer;