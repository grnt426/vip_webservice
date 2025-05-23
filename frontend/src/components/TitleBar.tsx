import { useState } from 'react';
import { AppBar, Box, Toolbar, Typography, IconButton, useTheme, useMediaQuery } from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import MenuIcon from '@mui/icons-material/Menu';
import { Menu, MenuItem } from '@mui/material';

interface TitleBarProps {
  onMobileMenuToggle?: () => void;
}

const TitleBar: React.FC<TitleBarProps> = ({ onMobileMenuToggle }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleClickSettings = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCloseSettings = () => {
    setAnchorEl(null);
  };

  const handleSelectSetting = (option: string) => {
    console.log(`Selected: ${option}`);
    handleCloseSettings();
  };

  return (
    <Box sx={{ flexGrow: 1, height: '4rem' }}>
      <AppBar 
        position="fixed" 
        elevation={0}
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          background: `linear-gradient(90deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
          borderBottom: `1px solid ${theme.palette.primary.main}20`,
        }}
      >
        <Toolbar>
          {isMobile && onMobileMenuToggle && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={onMobileMenuToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography 
            variant="h5" 
            component="div" 
            sx={{ 
              flexGrow: 1,
              background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontWeight: 'bold'
            }}
          >
            VIP Guild Client Dashboard
          </Typography>

          <IconButton
            size="large"
            sx={{
              color: theme.palette.text.secondary,
              '&:hover': {
                color: theme.palette.primary.main,
                backgroundColor: `${theme.palette.primary.main}20`,
              },
            }}
            aria-label="settings"
            onClick={handleClickSettings}
          >
            <SettingsIcon />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleCloseSettings}
            PaperProps={{
              sx: {
                backgroundColor: theme.palette.background.paper,
                borderRadius: 1,
                border: `1px solid ${theme.palette.primary.main}20`,
                boxShadow: `0 4px 20px ${theme.palette.primary.main}20`,
              }
            }}
          >
            {['Profile', 'Settings', 'Logout'].map((option) => (
              <MenuItem 
                key={option}
                onClick={() => handleSelectSetting(option)}
                sx={{
                  '&:hover': {
                    backgroundColor: `${theme.palette.primary.main}20`,
                    color: theme.palette.primary.main,
                  },
                }}
              >
                {option}
              </MenuItem>
            ))}
          </Menu>
        </Toolbar>
      </AppBar>
    </Box>
  );
}

export default TitleBar;
