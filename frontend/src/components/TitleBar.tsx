import { useState } from 'react';
import { AppBar, Box, Toolbar, Typography, IconButton, useTheme, useMediaQuery } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import MenuIcon from '@mui/icons-material/Menu';
import { Menu, MenuItem } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

interface TitleBarProps {
  onMobileMenuToggle?: () => void;
}

interface MenuOption {
  label: string;
  action?: string | (() => void);
  path?: string;
}

const TitleBar: React.FC<TitleBarProps> = ({ onMobileMenuToggle }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleClickUserMenu = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorEl(null);
  };

  const menuOptions: MenuOption[] = [
    { label: 'Register', path: '/register' },
    { label: 'Profile', action: () => console.log('Profile clicked') },
    { label: 'Settings', action: () => console.log('Settings clicked') },
    { label: 'Logout', action: () => console.log('Logout clicked') },
  ];

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
            aria-label="user account menu"
            onClick={handleClickUserMenu}
          >
            <AccountCircleIcon />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleCloseUserMenu}
            PaperProps={{
              sx: {
                backgroundColor: theme.palette.background.paper,
                borderRadius: 1,
                border: `1px solid ${theme.palette.primary.main}20`,
                boxShadow: `0 4px 20px ${theme.palette.primary.main}20`,
              }
            }}
          >
            {menuOptions.map((option) => (
              <MenuItem 
                key={option.label}
                onClick={() => {
                  if (typeof option.action === 'function') {
                    option.action();
                  }
                  handleCloseUserMenu();
                }}
                component={option.path ? RouterLink : 'li'}
                to={option.path}
                sx={{
                  '&:hover': {
                    backgroundColor: `${theme.palette.primary.main}20`,
                    color: theme.palette.primary.main,
                  },
                }}
              >
                {option.label}
              </MenuItem>
            ))}
          </Menu>
        </Toolbar>
      </AppBar>
    </Box>
  );
}

export default TitleBar;
