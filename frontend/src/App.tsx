import { useState } from 'react'
import { Box, Typography } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

import TitleBar from "./components/TitleBar";
import SideBar from "./components/SideBar";
import Footer from "./components/Footer";
import HomePage from "./pages/Home";
import GuildDashboard from "./pages/GuildDashboard";
import ExampleCardsPage from "./pages/ExampleCards";
import ExampleChartPage from "./pages/ExampleChart";
import ExampleDataGridPage from "./pages/ExampleDataGrid";
import AboutPage from "./pages/About";
import ContactPage from "./pages/Contact";

// See https://mui.com/material-ui/customization/palette/ for defining colors and themes
const vipGuildColor = {
  main: '#47A0CA',  // This is a VIP Guild color.
  light: '#5bbadc', // This is not a VIP Guild color, but a lighter shade of main.
  dark: '#397da3',  // This is not a VIP Guild color, but a darker shade of main.
  contrastText: '#fff', // White text to be displayed on main color background.
};
// Complementary color to #47A0CA (VIP Guild color) is #ca7047

const theme = createTheme({
  palette: {
    primary: vipGuildColor,
    // can also define secondary, error, warning, info, success palettes
  },
});

const App: React.FC = () => {
  const [content, setContent] = useState('GuildDashboard');  // Set GuildDashboard as default
  const renderContent = () => {
    switch (content) {
      case 'Home':
        return <HomePage />;
      case 'GuildDashboard':
        return <GuildDashboard />;
      case 'ExampleCards':
        return <ExampleCardsPage />;
      case 'ExampleChart':
        return <ExampleChartPage />;
      case 'ExampleDataGrid':
        return <ExampleDataGridPage />;
      case 'About':
        return <AboutPage />;
      case 'Contact':
        return <ContactPage />;
      default:
        return <Typography variant="h4">Page Not Found</Typography>;
    }
  };

  return (
    <>
      <ThemeProvider theme={theme}>
        <Box sx={{ display:"flex", flexDirection:"column" }}>
          <TitleBar />
          <Box sx={{ display: 'flex'}}>
            <SideBar onSelect={setContent} />
            <Box sx={{ flexGrow: 1, p:1 }}>
              {renderContent()}
              <Footer />
            </Box>
          </Box>
        </Box>
      </ThemeProvider>
    </>
  )
}

export default App
