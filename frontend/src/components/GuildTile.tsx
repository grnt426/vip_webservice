import { Card, CardContent, Typography, Box, LinearProgress } from '@mui/material';

interface GuildEmblem {
  background: {
    id: number;
    colors: number[];
  };
  foreground: {
    id: number;
    colors: number[];
  };
  flags: string[];
}

interface GuildData {
  id: string;
  name: string;
  tag: string;
  level: number;
  motd: string;
  influence: number;
  aetherium: number;
  resonance: number;
  favor: number;
  emblem: GuildEmblem;
}

interface GuildTileProps {
  guild: GuildData;
}

const GuildTile: React.FC<GuildTileProps> = ({ guild }) => {
  // Helper function to calculate percentage for progress bars
  const calculatePercentage = (value: number, max: number) => (value / max) * 100;

  return (
    <Card sx={{ 
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      '&:hover': {
        boxShadow: 6,
        transform: 'scale(1.02)',
        transition: 'all 0.2s ease-in-out'
      }
    }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="h5" gutterBottom>
          {guild.name} [{guild.tag}]
        </Typography>
        
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Level {guild.level}
        </Typography>

        <Typography variant="body2" sx={{ 
          fontStyle: 'italic',
          mb: 2,
          height: '3em',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical'
        }}>
          "{guild.motd}"
        </Typography>

        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" gutterBottom>
            Influence: {guild.influence}
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={calculatePercentage(guild.influence, 100000)}
            sx={{ mb: 1 }}
          />

          <Typography variant="body2" gutterBottom>
            Aetherium: {guild.aetherium}
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={calculatePercentage(guild.aetherium, 20000)}
            sx={{ mb: 1 }}
          />

          <Typography variant="body2" gutterBottom>
            Resonance: {guild.resonance}
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={calculatePercentage(guild.resonance, 2000)}
            sx={{ mb: 1 }}
          />

          <Typography variant="body2" gutterBottom>
            Favor: {guild.favor}
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={calculatePercentage(guild.favor, 1000)}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default GuildTile; 