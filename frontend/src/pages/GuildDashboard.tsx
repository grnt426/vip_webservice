import { Box, Container, Typography, CircularProgress, Stack } from '@mui/material';
import GuildTile from '../components/GuildTile';
import { useGuilds } from '../hooks/useGuilds';

const GuildDashboard: React.FC = () => {
  const { guilds, loading, error } = useGuilds();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Typography color="error" align="center">
        Error: {error}
      </Typography>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Guild Dashboard
      </Typography>
      <Stack 
        spacing={4}
        sx={{
          '& > *': {
            width: {
              xs: '100%',
              // Only show two guilds per row on very wide screens
              '2xl': 'calc(50% - 32px)'
            }
          }
        }}
      >
        {guilds.map((guild) => (
          <Box key={guild.id}>
            <GuildTile guild={guild} />
          </Box>
        ))}
      </Stack>
    </Container>
  );
};

export default GuildDashboard; 