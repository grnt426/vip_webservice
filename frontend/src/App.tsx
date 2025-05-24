import { useState } from 'react'
import { Box, Typography, CssBaseline, useMediaQuery } from '@mui/material';
import { createTheme, ThemeProvider, useTheme } from '@mui/material/styles';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toolbar } from '@mui/material';

import TitleBar from "./components/TitleBar";
import SideBar from "./components/SideBar";
import Footer from "./components/Footer";
import HomePage from "./pages/Home";
import GuildDashboard from "./pages/GuildDashboard";
import GuildLogsPage from "./pages/GuildLogsPage";
import GuildMembersPage from "./pages/GuildMembersPage";
import AboutPage from "./pages/About";
import ContactPage from "./pages/Contact";
import RegistrationPage from './pages/RegistrationPage';

const appTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#ff4d4d', // Vibrant red
      light: '#ff8080',
      dark: '#cc0000',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#9c27b0', // Purple
      light: '#d05ce3',
      dark: '#6a0080',
      contrastText: '#ffffff',
    },
    background: {
      default: '#1a1a1a', // Very dark gray
      paper: '#2d2d2d', // Slightly lighter dark gray
    },
    error: {
      main: '#ff3d00', // Orange-red
    },
    warning: {
      main: '#ff9100', // Orange
    },
    info: {
      main: '#b388ff', // Light purple
    },
    success: {
      main: '#ff6e40', // Coral orange
    },
    text: {
      primary: '#ffffff',
      secondary: '#cccccc',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(145deg, #2d2d2d 0%, #1a1a1a 100%)',
          borderRadius: '12px',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 100%)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: 'linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%)',
          borderRight: '1px solid #333333',
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 5,
          height: 8,
        },
        bar: {
          borderRadius: 5,
        },
      },
    },
  },
});

const App: React.FC = () => {
  const [content, setContent] = useState('GuildDashboard');  // Set GuildDashboard as default
  const theme = useTheme(); // Use the theme from ThemeProvider for useMediaQuery
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const renderContent = () => {
    switch (content) {
      case 'Home':
        return <HomePage />;
      case 'GuildDashboard':
        return <GuildDashboard />;
      case 'GuildMembers':
        return <GuildMembersPage />;
      case 'GuildLogs':
        return <GuildLogsPage />;
      case 'About':
        return <AboutPage />;
      case 'Contact':
        return <ContactPage />;
      case 'Registration':
        return <RegistrationPage />;
      default:
        return <Typography variant="h4">Page Not Found</Typography>;
    }
  };

  return (
    <Router>
      <ThemeProvider theme={appTheme}>
        <CssBaseline />
        <Box sx={{ display:"flex", flexDirection:"column", minHeight: '100vh', bgcolor: 'background.default' }}>
          <TitleBar onMobileMenuToggle={isMobile ? handleDrawerToggle : undefined} />
          <Box sx={{ display: 'flex', flex: 1, mt: isMobile ? 0 : `64px` /* Account for fixed AppBar height */ }}>
            <SideBar 
              onSelect={(selectedPage) => {
                setContent(selectedPage);
                if (isMobile) {
                  setMobileOpen(false);
                }
              }}
              mobileOpen={mobileOpen} 
              onMobileClose={handleDrawerToggle} 
            />
            <Box 
              component="main" // Semantic main content area
              sx={{ 
                flexGrow: 1, 
                p: 3, 
                // ml: isMobile ? 0 : `240px` // This might not be needed if SideBar handles its own display correctly
                width: isMobile ? '100%' : `calc(100% - 240px)` // Ensure content takes remaining width
              }}
            >
              <Toolbar />
              <Routes>
                <Route path="/" element={renderContent()} />
                <Route path="/register" element={<RegistrationPage />} />
              </Routes>
              <Footer />
            </Box>
          </Box>
        </Box>
      </ThemeProvider>
    </Router>
  )
}

export default App
