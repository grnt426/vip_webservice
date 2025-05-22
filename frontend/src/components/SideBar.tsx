import { Box, Drawer, Toolbar, List, ListItemButton, ListItemIcon, ListItemText, useTheme } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ListAltIcon from '@mui/icons-material/ListAlt';
import InfoIcon from '@mui/icons-material/Info';
import ContactMailIcon from '@mui/icons-material/ContactMail';
import PeopleIcon from '@mui/icons-material/People';

interface SideBarProps {
  onSelect: (selected: string) => void;
}

const drawerWidth = 240;

// Need to data structure and iterate the sidebar menu eventually. We'll pass a json into this thing and it will build
// the sidebar.
const SideBar: React.FC<SideBarProps> = ({ onSelect }) => {
  const theme = useTheme();
  
  const menuItems = [
    { text: 'Home', icon: <HomeIcon />, value: 'Home' },
    { text: 'Guild Dashboard', icon: <DashboardIcon />, value: 'GuildDashboard' },
    { text: 'Guild Members', icon: <PeopleIcon />, value: 'GuildMembers' },
    { text: 'Guild Logs', icon: <ListAltIcon />, value: 'GuildLogs' },
    { text: 'About', icon: <InfoIcon />, value: 'About' },
    { text: 'Contact', icon: <ContactMailIcon />, value: 'Contact' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { 
          width: drawerWidth, 
          boxSizing: 'border-box',
          background: `linear-gradient(180deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
          borderRight: `1px solid ${theme.palette.primary.main}20`,
        },
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {menuItems.map((item) => (
            <ListItemButton
              key={item.text}
              onClick={() => onSelect(item.value)}
              sx={{
                my: 0.5,
                mx: 1,
                borderRadius: 1,
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
                },
                '& .MuiListItemText-primary': {
                  color: theme.palette.text.primary,
                  transition: 'color 0.2s',
                },
              }}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          ))}
        </List>
      </Box>
    </Drawer>
  );
}

export default SideBar;
