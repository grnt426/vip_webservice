import { useState, useEffect } from 'react';
import { Container, Typography, CircularProgress, Box, Stack } from '@mui/material';
import GuildTile from '../components/GuildTile';
import { GuildData } from '../types/guild';

const GuildDashboard: React.FC = () => {
  const [guilds, setGuilds] = useState<GuildData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGuilds = async () => {
      try {
        const response = await fetch('http://localhost:8080/api/guilds');
        if (!response.ok) {
          throw new Error('Failed to fetch guild data');
        }
        const data = await response.json();
        setGuilds(data);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        setLoading(false);
      }
    };

    fetchGuilds();
  }, []);

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
        direction="row" 
        spacing={3} 
        useFlexGap 
        flexWrap="wrap"
        sx={{
          '& > *': {
            width: {
              xs: '100%',
              sm: 'calc(50% - 24px)',
              md: 'calc(33.333% - 24px)'
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