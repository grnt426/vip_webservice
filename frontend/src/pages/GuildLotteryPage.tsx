import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  useTheme,
  CircularProgress,
  Button,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import CasinoIcon from '@mui/icons-material/Casino';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import LockIcon from '@mui/icons-material/Lock';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';
import { fetchWithAuth } from '../utils/api';

interface LotteryWinner {
  id: number;
  account_id: number;
  guild_id: string;
  week_number: number;
  year: number;
  prize_amount: number;
  paid_out: boolean;
  created_at: string;
  paid_at: string | null;
  account?: {
    current_account_name: string;
  };
}

interface LotteryStats {
  current_pot: number;
  current_entries_count: number;
  past_winners: LotteryWinner[];
}

const COPPER_TO_GOLD = 10000; // 1 gold = 10000 copper

const formatGold = (copper: number): string => {
  const gold = Math.floor(copper / COPPER_TO_GOLD);
  const remainingCopper = copper % COPPER_TO_GOLD;
  const silver = Math.floor(remainingCopper / 100);
  const copper_remainder = remainingCopper % 100;
  
  return `${gold}g ${silver}s ${copper_remainder}c`;
};

const GuildLotteryPage: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(true);

  const { data: lotteryStats, isLoading, error, isError } = useQuery<LotteryStats>({
    queryKey: ['lotteryStats'],
    queryFn: async () => {
      try {
        const response = await fetchWithAuth('/api/lottery/stats');
        
        if (!response.ok) {
          throw new Error('Failed to fetch lottery stats');
        }
        
        return response.json();
      } catch (err) {
        if ((err as Error).message === 'Not authenticated' || (err as Error).message === 'Unauthorized') {
          setIsAuthenticated(false);
        }
        throw err;
      }
    },
    refetchInterval: (query) => {
      // Only refetch if the last request was successful
      if (query.state.error) {
        const errorMessage = (query.state.error as Error).message;
        if (errorMessage === 'Unauthorized' || errorMessage === 'Not authenticated') {
          return false; // Don't refetch on auth errors
        }
      }
      return 60000; // Refresh every minute for successful requests
    },
    retry: (failureCount, error) => {
      // Don't retry on auth errors
      if ((error as Error).message === 'Unauthorized' || (error as Error).message === 'Not authenticated') {
        return false;
      }
      return failureCount < 1;
    },
  });

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setIsAuthenticated(false);
    }
  }, []);

  if (!isAuthenticated) {
    return (
      <Box
        sx={{
          minHeight: '400px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            textAlign: 'center',
            maxWidth: 400,
            background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.primary.dark}22 100%)`,
          }}
        >
          <LockIcon sx={{ fontSize: 48, color: theme.palette.text.secondary, mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Authentication Required
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            You must be logged in to view the lottery.
          </Typography>
          <Button
            variant="contained"
            onClick={() => navigate('/login')}
            sx={{ mr: 2 }}
          >
            Login
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate('/register')}
          >
            Register
          </Button>
        </Paper>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (isError && error.message !== 'Unauthorized') {
    return (
      <Box p={3}>
        <Typography color="error">Error loading lottery data</Typography>
      </Box>
    );
  }

  const jackpot = Math.floor((lotteryStats?.current_pot || 0) * 0.9); // 90% of pot
  const recentWinners = lotteryStats?.past_winners.slice(0, 4) || [];

  return (
    <Box p={3}>
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4,
          background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.primary.dark}22 100%)`,
        }}
      >
        {/* Header */}
        <Box display="flex" alignItems="center" mb={4}>
          <CasinoIcon sx={{ fontSize: 40, mr: 2, color: theme.palette.primary.main }} />
          <Typography variant="h4" component="h1">
            Guild Lottery
          </Typography>
        </Box>

        {/* Current Jackpot */}
        <Card 
          elevation={6}
          sx={{
            mb: 4,
            background: `linear-gradient(135deg, ${theme.palette.primary.main}22 0%, ${theme.palette.primary.dark}33 100%)`,
            border: `1px solid ${theme.palette.primary.main}33`,
          }}
        >
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ color: theme.palette.primary.main }}>
              Current Jackpot
            </Typography>
            <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
              {formatGold(jackpot)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              From {lotteryStats?.current_entries_count || 0} total entries this week
            </Typography>
          </CardContent>
        </Card>

        {/* Recent Winners */}
        <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 2 }}>
          <Box display="flex" alignItems="center">
            <EmojiEventsIcon sx={{ mr: 1 }} />
            Recent Winners
          </Box>
        </Typography>
        
        <Box sx={{ flexGrow: 1 }}>
          <Grid container spacing={2}>
            {recentWinners.map((winner: LotteryWinner) => (
              <Box key={winner.id} sx={{ width: { xs: '100%', sm: '50%' }, p: 1 }}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Week {winner.week_number}, {winner.year}
                    </Typography>
                    <Typography variant="h6" component="div">
                      {winner.account?.current_account_name || 'Unknown Player'}
                    </Typography>
                    <Typography variant="body1" color="primary">
                      Won: {formatGold(winner.prize_amount)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {format(new Date(winner.created_at), 'MMM d, yyyy')}
                    </Typography>
                  </CardContent>
                </Card>
              </Box>
            ))}
            {recentWinners.length === 0 && (
              <Box sx={{ width: '100%', p: 1 }}>
                <Typography variant="body1" color="text.secondary" textAlign="center">
                  No recent winners
                </Typography>
              </Box>
            )}
          </Grid>
        </Box>
      </Paper>
    </Box>
  );
};

export default GuildLotteryPage; 