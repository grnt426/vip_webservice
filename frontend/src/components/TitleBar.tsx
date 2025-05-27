import { useState, useEffect } from 'react';
import { AppBar, Box, Toolbar, Typography, IconButton, useTheme, useMediaQuery } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import MenuIcon from '@mui/icons-material/Menu';
import { Menu, MenuItem } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';

interface TitleBarProps {
  onMobileMenuToggle?: () => void;
}

interface MenuOption {
  label: string;
  action?: string | (() => void);
  path?: string;
  requiresAuth?: boolean;
  hideWhenAuth?: boolean;
}

interface User {
  id: number;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  account_id: number;
  roles: string[];
}

const TitleBar: React.FC<TitleBarProps> = ({ onMobileMenuToggle }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [user, setUser] = useState<User | null>(null);

  const checkUserAuth = () => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Error parsing stored user data:', e);
        setUser(null);
      }
    } else {
      setUser(null);
    }
  };

  useEffect(() => {
    // Check for user data in localStorage on mount
    checkUserAuth();

    // Listen for storage events (from other tabs/windows)
    window.addEventListener('storage', checkUserAuth);

    // Listen for custom auth events (from same tab)
    window.addEventListener('auth-changed', checkUserAuth);

    return () => {
      window.removeEventListener('storage', checkUserAuth);
      window.removeEventListener('auth-changed', checkUserAuth);
    };
  }, []);

  const handleClickUserMenu = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    handleCloseUserMenu();
    navigate('/');
    // Dispatch custom event for auth change
    window.dispatchEvent(new Event('auth-changed'));
  };

  const menuOptions: MenuOption[] = [
    { label: 'Login', path: '/login', hideWhenAuth: true },
    { label: 'Register', path: '/register', hideWhenAuth: true },
    { label: 'Profile', path: '/profile', requiresAuth: true },
    { label: 'Settings', path: '/settings', requiresAuth: true },
    { 
      label: 'Logout', 
      action: handleLogout,
      requiresAuth: true 
    },
  ];

  // Filter menu options based on auth state
  const filteredMenuOptions = menuOptions.filter(option => {
    if (user) {
      return !option.hideWhenAuth;
    }
    return !option.requiresAuth;
  });

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

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {user && (
              <Typography variant="body2" sx={{ mr: 2, color: theme.palette.text.secondary }}>
                {user.username}
              </Typography>
            )}
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
          </Box>
          
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
            {filteredMenuOptions.map((option) => (
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
};

export default TitleBar;
