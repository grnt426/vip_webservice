import { Box, Drawer, Toolbar, List, ListItemButton, ListItemIcon, ListItemText, } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import InfoIcon from '@mui/icons-material/Info';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ContactMailIcon from '@mui/icons-material/ContactMail';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import TableChartIcon from '@mui/icons-material/TableChart';

interface SideBarProps {
  onSelect: (selected: string) => void;
}

const drawerWidth = 240;

// Need to data structure and iterate the sidebar menu eventually. We'll pass a json into this thing and it will build
// the sidebar.
const SideBar: React.FC<SideBarProps> = ({ onSelect }) => {
  const menuItems = [
    { text: 'Home', icon: <HomeIcon />, value: 'Home' },
    { text: 'Guild Dashboard', icon: <DashboardIcon />, value: 'GuildDashboard' },
    { text: 'Example Cards', icon: <ViewModuleIcon />, value: 'ExampleCards' },
    { text: 'Example Chart', icon: <ShowChartIcon />, value: 'ExampleChart' },
    { text: 'Example Data Grid', icon: <TableChartIcon />, value: 'ExampleDataGrid' },
    { text: 'About', icon: <InfoIcon />, value: 'About' },
    { text: 'Contact', icon: <ContactMailIcon />, value: 'Contact' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {menuItems.map((item) => (
            <ListItemButton
              key={item.text}
              onClick={() => onSelect(item.value)}
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
