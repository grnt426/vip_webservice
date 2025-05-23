import { Box, Drawer, Toolbar, List, ListItemButton, ListItemIcon, ListItemText, useTheme, useMediaQuery } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ListAltIcon from '@mui/icons-material/ListAlt';
import InfoIcon from '@mui/icons-material/Info';
import ContactMailIcon from '@mui/icons-material/ContactMail';
import PeopleIcon from '@mui/icons-material/People';
import React from 'react';

interface SideBarProps {
  onSelect: (selected: string) => void;
  mobileOpen: boolean;      // New prop from App.tsx
  onMobileClose: () => void; // New prop from App.tsx (was handleDrawerToggle in App.tsx)
}

const drawerWidth = 240;
// const collapsedDrawerWidth = 56; // Removed as it's not used with the temporary drawer approach

const SideBar: React.FC<SideBarProps> = ({ onSelect, mobileOpen, onMobileClose }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const menuItems = [
    { text: 'Home', icon: <HomeIcon />, value: 'Home' },
    { text: 'Guild Dashboard', icon: <DashboardIcon />, value: 'GuildDashboard' },
    { text: 'Guild Members', icon: <PeopleIcon />, value: 'GuildMembers' },
    { text: 'Guild Logs', icon: <ListAltIcon />, value: 'GuildLogs' },
    { text: 'About', icon: <InfoIcon />, value: 'About' },
    { text: 'Contact', icon: <ContactMailIcon />, value: 'Contact' },
  ];

  const drawerContent = (
    <>
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {menuItems.map((item) => (
            <ListItemButton
              key={item.text}
              onClick={() => {
                onSelect(item.value);
                // No need to explicitly close here if onSelect in App.tsx handles it for mobile
              }}
              sx={{
                my: 0.5,
                mx: 1,
                borderRadius: 1,
                // Removed justifyContent styling related to a potential collapsed state not currently used for mobile
                '&:hover': {
                  backgroundColor: `${theme.palette.primary.main}20`,
                  '& .MuiListItemIcon-root': {
                    color: theme.palette.primary.main,
                  },
                  '& .MuiListItemText-primary': {
                    color: theme.palette.primary.main,
                  },
                },
                '& .MuiListItemIcon-root': {
                  color: theme.palette.text.secondary,
                  transition: 'color 0.2s',
                  minWidth: 0,
                  mr: 3, // Standard margin when text is visible
                },
                '& .MuiListItemText-primary': {
                  color: theme.palette.text.primary,
                  transition: 'color 0.2s',
                  // Text is now always visible when drawerContent is rendered for temporary mobile drawer
                },
              }}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              {/* Text is always rendered here now because the temporary drawer is either fully open or not present */}
              <ListItemText primary={item.text} />
            </ListItemButton>
          ))}
        </List>
      </Box>
    </>
  );

  if (isMobile) {
    return (
      <Drawer
        variant="temporary"
        open={mobileOpen} // Controlled by prop from App.tsx
        onClose={onMobileClose} // Controlled by prop from App.tsx
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { 
            boxSizing: 'border-box', 
            width: drawerWidth,
            background: `linear-gradient(180deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
            borderRight: `1px solid ${theme.palette.primary.main}20`,
          },
        }}
      >
        {drawerContent}
      </Drawer>
    );
  }

  // Desktop Drawer
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        display: { xs: 'none', sm: 'block' }, // Hide on xs, show on sm and up
        [`& .MuiDrawer-paper`]: { 
          width: drawerWidth, 
          boxSizing: 'border-box',
          background: `linear-gradient(180deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
          borderRight: `1px solid ${theme.palette.primary.main}20`,
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
}

export default SideBar;
