import { Card, CardContent, Typography, Box, LinearProgress, useTheme, Link } from '@mui/material';
import { FaDiscord } from 'react-icons/fa';
import { parseMotd, formatTime } from '../utils/motdParser';

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

interface GuildTileProps {
  guild: {
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
  };
}

const getShortGuildName = (fullName: string): string => {
  // Extract the last word from the guild name
  const words = fullName.split(' ');
  return words[words.length - 1];
};

const GuildTile: React.FC<GuildTileProps> = ({ guild }) => {
  const theme = useTheme();
  
  const parsedMotd = parseMotd(guild.motd);
  const shortName = getShortGuildName(guild.name);
  
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  
  // Group events by day
  const eventsByDay = days.reduce((acc, day) => {
    acc[day] = parsedMotd.schedule.filter(event => event.day === day);
    return acc;
  }, {} as Record<string, typeof parsedMotd.schedule>);

  // Helper function to calculate percentage for progress bars
  const calculatePercentage = (value: number, max: number) => Math.min(100, (value / max) * 100);

  // Resource configurations with dynamic maximums
  const resources = [
    {
      name: 'Influence',
      value: guild.influence,
      max: Math.max(100000, guild.influence),
      color: theme.palette.primary.main
    },
    {
      name: 'Aetherium',
      value: guild.aetherium,
      max: Math.max(20000, guild.aetherium),
      color: theme.palette.secondary.main
    },
    {
      name: 'Resonance',
      value: guild.resonance,
      max: Math.max(2000, guild.resonance),
      color: theme.palette.warning.main
    },
    {
      name: 'Favor',
      value: guild.favor,
      max: Math.max(1000, guild.favor),
      color: theme.palette.info.main
    }
  ];

  return (
    <Card sx={{ 
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      overflow: 'hidden',
      '&:hover': {
        boxShadow: `0 0 20px ${theme.palette.primary.main}40`,
        transform: 'scale(1.01)',
        transition: 'all 0.3s ease-in-out'
      }
    }}>
      <CardContent sx={{ 
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        p: 2
      }}>
        {/* Header Row */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: `1px solid ${theme.palette.divider}`
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box>
              <Typography variant="h6" sx={{
                color: theme.palette.primary.main,
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}>
                {shortName} <Typography component="span" sx={{ color: theme.palette.text.secondary }}>[{guild.tag}]</Typography>
              </Typography>
              <Typography variant="body2" sx={{ color: theme.palette.secondary.main }}>
                Level {guild.level}
              </Typography>
            </Box>
            {parsedMotd.discordUrl && (
              <Link 
                href={parsedMotd.discordUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                sx={{ 
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  color: '#7289DA',
                  textDecoration: 'none',
                  '&:hover': {
                    textDecoration: 'underline'
                  }
                }}
              >
                <FaDiscord size={24} />
                Join Discord
              </Link>
            )}
          </Box>
          
          {/* Resources */}
          <Box sx={{ 
            display: 'flex', 
            gap: 3,
            alignItems: 'center'
          }}>
            {resources.map((resource) => (
              <Box key={resource.name} sx={{ minWidth: 120 }}>
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mb: 0.5
                }}>
                  <Typography variant="body2" sx={{ color: resource.color }}>
                    {resource.name}
                  </Typography>
                  <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
                    {resource.value.toLocaleString()}
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={calculatePercentage(resource.value, resource.max)}
                  sx={{ 
                    height: 4,
                    backgroundColor: `${resource.color}20`,
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: resource.color,
                    }
                  }}
                />
              </Box>
            ))}
          </Box>
        </Box>

        {/* Weekly Schedule */}
        <Box sx={{ 
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          gap: 1
        }}>
          {days.map((day) => (
            <Box 
              key={day}
              sx={{
                flex: 1,
                p: 1,
                borderRadius: 1,
                bgcolor: theme.palette.background.paper,
                border: `1px solid ${theme.palette.divider}`,
                minWidth: { sm: '120px' }
              }}
            >
              <Typography variant="subtitle2" sx={{ 
                color: theme.palette.primary.main,
                borderBottom: `1px solid ${theme.palette.divider}`,
                pb: 0.5,
                mb: 1
              }}>
                {day}
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                {eventsByDay[day]?.map((event, index) => (
                  <Box key={index} sx={{
                    p: 0.5,
                    borderRadius: 0.5,
                    bgcolor: `${theme.palette.primary.main}10`,
                  }}>
                    <Typography variant="caption" sx={{ color: theme.palette.primary.main }}>
                      {formatTime(event.time)}
                    </Typography>
                    <Typography variant="body2" sx={{ 
                      fontSize: '0.8rem',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {event.event}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default GuildTile; 