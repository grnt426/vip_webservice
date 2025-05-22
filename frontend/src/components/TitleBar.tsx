import { useState } from 'react';
import { AppBar, Box, Toolbar, Typography, IconButton } from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import { Menu, MenuItem } from '@mui/material';

const TitleBar: React.FC = () => {

  // Menu button.
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleSelect = (option: string) => {
    console.log(`Selected: ${option}`); // Do some action eventually.
    handleClose();
  };

  return (
    <Box sx={{ flexGrow: 1, height: '4rem' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h5" component="div" sx={{ flexGrow: 1 }}>
            VIP Guild Client Dashboard
          </Typography>

          <IconButton
            size="large"
            color="inherit"
            aria-label="menu"
            onClick={handleClick}
          >
            <SettingsIcon />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={() => handleSelect('Profile')}>Profile</MenuItem>
            <MenuItem onClick={() => handleSelect('Settings')}>Settings</MenuItem>
            <MenuItem onClick={() => handleSelect('Logout')}>Logout</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
    </Box>
  );
}

export default TitleBar;
