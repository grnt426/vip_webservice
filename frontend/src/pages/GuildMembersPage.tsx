import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  IconButton,
  Tooltip,
  SelectChangeEvent,
  CircularProgress,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useGuilds } from '../hooks/useGuilds';

const GuildMembersPage: React.FC = () => {
  const { guilds, loading, error, refreshGuilds } = useGuilds();
  const [selectedGuild, setSelectedGuild] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRank, setSelectedRank] = useState<string>('');

  const currentGuild = guilds.find(g => g.id === selectedGuild);
  
  const filteredMembers = currentGuild?.members.filter(member => {
    const nameMatch = member.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                     member.full_name.toLowerCase().includes(searchTerm.toLowerCase());
    const rankMatch = !selectedRank || member.rank === selectedRank;
    return nameMatch && rankMatch;
  }) || [];

  // Sort members by rank order first, then by name
  const sortedMembers = [...filteredMembers].sort((a, b) => {
    // Special case: "invited" rank should always be last
    if (a.rank === 'invited' && b.rank !== 'invited') return 1;
    if (b.rank === 'invited' && a.rank !== 'invited') return -1;
    if (a.rank === 'invited' && b.rank === 'invited') return a.name.localeCompare(b.name);

    const rankA = currentGuild?.ranks.find(r => r.id === a.rank)?.order || 0;
    const rankB = currentGuild?.ranks.find(r => r.id === b.rank)?.order || 0;
    if (rankA !== rankB) return rankA - rankB;
    return a.name.localeCompare(b.name);
  });

  const handleGuildChange = (event: SelectChangeEvent<string>) => {
    setSelectedGuild(event.target.value);
    setSelectedRank('');
    setSearchTerm('');
  };

  const handleRankChange = (event: SelectChangeEvent<string>) => {
    setSelectedRank(event.target.value);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  // Set initial selected guild if none selected
  if (!selectedGuild && guilds.length > 0) {
    setSelectedGuild(guilds[0].id);
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Guild Members
      </Typography>

      {/* Controls */}
      <Box sx={{ 
        mb: 3,
        display: 'flex',
        flexDirection: { xs: 'column', sm: 'row' },
        gap: 2,
        alignItems: { xs: 'stretch', sm: 'center' }
      }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Select Guild</InputLabel>
          <Select
            value={selectedGuild}
            label="Select Guild"
            onChange={handleGuildChange}
          >
            {guilds.map((guild) => (
              <MenuItem key={guild.id} value={guild.id}>
                {guild.short_name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Filter by Rank</InputLabel>
          <Select
            value={selectedRank}
            label="Filter by Rank"
            onChange={handleRankChange}
          >
            <MenuItem value="">All Ranks</MenuItem>
            {currentGuild?.ranks
              .sort((a, b) => a.order - b.order)
              .map((rank) => (
                <MenuItem key={rank.id} value={rank.id}>
                  {rank.id}
                </MenuItem>
              ))}
            <MenuItem value="invited">Invited</MenuItem>
          </Select>
        </FormControl>

        <TextField
          label="Search Members"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={handleSearchChange}
          sx={{ minWidth: 200 }}
        />

        <Tooltip title="Refresh Data">
          <IconButton 
            onClick={() => refreshGuilds(true)} 
            color="primary"
            disabled={loading}
          >
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Error message */}
      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {/* Members table */}
      <TableContainer 
        component={Paper}
        sx={{ 
          mb: 2,
          maxHeight: 'calc(100vh - 300px)',
          overflow: 'auto'
        }}
      >
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Account Name</TableCell>
              <TableCell>Rank</TableCell>
              <TableCell>Joined</TableCell>
              <TableCell>WvW Member</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  <CircularProgress size={24} sx={{ my: 2 }} />
                </TableCell>
              </TableRow>
            ) : sortedMembers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  No members found
                </TableCell>
              </TableRow>
            ) : (
              sortedMembers.map((member) => (
                <TableRow key={member.full_name}>
                  <TableCell>
                    <Tooltip title={member.full_name} placement="right">
                      <span>{member.name}</span>
                    </Tooltip>
                  </TableCell>
                  <TableCell>{member.rank}</TableCell>
                  <TableCell>
                    {member.joined 
                      ? new Date(member.joined).toLocaleDateString()
                      : 'Unknown'
                    }
                  </TableCell>
                  <TableCell>
                    {member.wvw_member ? 'Yes' : 'No'}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Summary */}
      <Typography variant="body2" color="text.secondary">
        Showing {sortedMembers.length} members
        {searchTerm || selectedRank ? ' (filtered)' : ''}
      </Typography>
    </Box>
  );
};

export default GuildMembersPage; 