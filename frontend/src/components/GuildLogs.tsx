import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Stack,
  Tooltip,
  IconButton,
} from '@mui/material';
import { formatDistanceToNow } from 'date-fns';
import { Info as InfoIcon } from '@mui/icons-material';
import { splitAccountName } from '../utils/nameUtils.ts';

// Log type definitions
interface BaseGuildLog {
  id: number;
  time: string;
  type: string;
  user: string;
  guild_name?: string;  // Only present in global logs view
}

interface KickLog extends BaseGuildLog {
  type: 'kick';
  kicked_by: string;
}

interface InviteLog extends BaseGuildLog {
  type: 'invited';
  invited_by: string;
}

interface InviteDeclineLog extends BaseGuildLog {
  type: 'invite_declined';
  declined_by: string;
}

interface JoinLog extends BaseGuildLog {
  type: 'join';
}

interface RankChangeLog extends BaseGuildLog {
  type: 'rank_change';
  changed_by: string;
  old_rank: string;
  new_rank: string;
}

interface StashLog extends BaseGuildLog {
  type: 'stash';
  operation: string;
  item_id?: number;
  count?: number;
  coins?: number;
  item_name?: string;
}

interface TreasuryLog extends BaseGuildLog {
  type: 'treasury';
  item_id: number;
  count: number;
  item_name?: string;
}

interface MotdLog extends BaseGuildLog {
  type: 'motd';
  motd: string;
}

interface UpgradeLog extends BaseGuildLog {
  type: 'upgrade';
  action: string;
  upgrade_id: number;
  recipe_id?: number;
  count?: number;
  upgrade_name?: string;
}

interface InfluenceLog extends BaseGuildLog {
  type: 'influence';
  amount: number;
  activity: number;
}

interface MissionLog extends BaseGuildLog {
  type: 'mission';
  mission_name: string;
  status: string;
}

type GuildLog = KickLog | InviteLog | InviteDeclineLog | JoinLog | RankChangeLog | 
                StashLog | TreasuryLog | MotdLog | UpgradeLog | InfluenceLog | MissionLog;

interface GuildLogsProps {
  guildId?: string;  // Optional - if not provided, shows logs from all guilds
}

export default function GuildLogs({ guildId }: GuildLogsProps) {
  const [logs, setLogs] = useState<GuildLog[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [selectedType, setSelectedType] = useState<string>('');
  const [userFilter, setUserFilter] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const baseUrl = guildId ? `/api/guilds/${guildId}/logs` : '/api/logs';
      const params = new URLSearchParams({
        page: (page + 1).toString(),
        limit: rowsPerPage.toString(),
      });
      
      if (selectedType) params.append('type', selectedType);
      if (userFilter) params.append('user', userFilter);

      const response = await fetch(`${baseUrl}?${params}`);
      const data = await response.json();
      setLogs(data.logs);
      setTotal(data.total);
    } catch (error) {
      console.error('Error fetching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [guildId, page, rowsPerPage, selectedType, userFilter]);

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const formatLogMessage = (log: GuildLog): { message: string; tooltip?: string } => {
    const { displayName } = splitAccountName(log.user);
    
    switch (log.type) {
      case 'kick': {
        const { displayName: kickedByName } = splitAccountName(log.kicked_by);
        return {
          message: `${kickedByName} kicked ${displayName}`,
          tooltip: `Full names:\nKicked: ${log.user}\nBy: ${log.kicked_by}`
        };
      }
      case 'invited': {
        const { displayName: invitedByName } = splitAccountName(log.invited_by);
        return {
          message: `${invitedByName} invited ${displayName}`,
          tooltip: `Full names:\nInvited: ${log.user}\nBy: ${log.invited_by}`
        };
      }
      case 'invite_declined': {
        const { displayName: declinedByName } = splitAccountName(log.declined_by);
        return {
          message: `${declinedByName} declined invite for ${displayName}`,
          tooltip: `Full names:\nInvited: ${log.user}\nBy: ${log.declined_by}`
        };
      }
      case 'join':
        return {
          message: `${displayName} joined`,
          tooltip: `Full name: ${log.user}`
        };
      case 'rank_change': {
        const { displayName: changedByName } = splitAccountName(log.changed_by);
        return {
          message: `${changedByName} changed ${displayName}'s rank from ${log.old_rank} to ${log.new_rank}`,
          tooltip: `Full names:\nMember: ${log.user}\nBy: ${log.changed_by}`
        };
      }
      case 'stash': {
        if (log.coins) {
          const gold = Math.floor(log.coins / 10000);
          const silver = Math.floor((log.coins % 10000) / 100);
          const copper = log.coins % 100;
          return {
            message: `${displayName} ${log.operation}ed ${gold}g ${silver}s ${copper}c`,
            tooltip: `Full name: ${log.user}`
          };
        } else if (log.item_name) {
          return {
            message: `${displayName} ${log.operation}ed ${log.count}x ${log.item_name}`,
            tooltip: `Full name: ${log.user}\nItem ID: ${log.item_id}`
          };
        }
        return {
          message: `${displayName} performed a stash operation`,
          tooltip: `Full name: ${log.user}`
        };
      }
      case 'treasury': {
        return {
          message: `${displayName} deposited ${log.count}x ${log.item_name || `Item #${log.item_id}`}`,
          tooltip: `Full name: ${log.user}\nItem ID: ${log.item_id}`
        };
      }
      case 'motd':
        return {
          message: `${displayName} changed the Message of the Day`,
          tooltip: `Full name: ${log.user}\nNew MOTD: ${log.motd}`
        };
      case 'upgrade': {
        const itemName = log.upgrade_name || `Upgrade #${log.upgrade_id}`;
        switch (log.action) {
          case 'queued':
            return {
              message: `${displayName} queued ${itemName}`,
              tooltip: `Full name: ${log.user}\nUpgrade ID: ${log.upgrade_id}`
            };
          case 'cancelled':
            return {
              message: `${displayName} cancelled ${itemName}`,
              tooltip: `Full name: ${log.user}\nUpgrade ID: ${log.upgrade_id}`
            };
          case 'completed':
            return {
              message: `${itemName} was completed`,
              tooltip: `Upgrade ID: ${log.upgrade_id}`
            };
          case 'sped_up':
            return {
              message: `${displayName} sped up ${itemName}`,
              tooltip: `Full name: ${log.user}\nUpgrade ID: ${log.upgrade_id}`
            };
          default:
            return {
              message: `${displayName} performed an upgrade action: ${log.action}`,
              tooltip: `Full name: ${log.user}\nUpgrade ID: ${log.upgrade_id}`
            };
        }
      }
      case 'influence': {
        return {
          message: `${displayName} ${log.amount > 0 ? 'gained' : 'spent'} ${Math.abs(log.amount)} influence`,
          tooltip: `Full name: ${log.user}\nActivity: ${log.activity}`
        };
      }
      case 'mission': {
        return {
          message: `${displayName} ${log.status} mission: ${log.mission_name}`,
          tooltip: `Full name: ${log.user}`
        };
      }
      default:
        return {
          message: `Unknown log type`,
          tooltip: `Raw log data: ${JSON.stringify(log)}`
        };
    }
  };

  return (
    <Box>
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Filter by Type</InputLabel>
          <Select
            value={selectedType}
            label="Filter by Type"
            onChange={(e) => {
              setSelectedType(e.target.value);
              setPage(0);
            }}
          >
            <MenuItem value="">All Types</MenuItem>
            <MenuItem value="kick">Kicks</MenuItem>
            <MenuItem value="invited">Invites</MenuItem>
            <MenuItem value="invite_declined">Declined Invites</MenuItem>
            <MenuItem value="join">Joins</MenuItem>
            <MenuItem value="rank_change">Rank Changes</MenuItem>
            <MenuItem value="stash">Stash</MenuItem>
            <MenuItem value="treasury">Treasury</MenuItem>
            <MenuItem value="motd">MOTD</MenuItem>
            <MenuItem value="upgrade">Upgrades</MenuItem>
            <MenuItem value="influence">Influence</MenuItem>
            <MenuItem value="mission">Missions</MenuItem>
          </Select>
        </FormControl>
        <TextField
          size="small"
          label="Filter by User"
          value={userFilter}
          onChange={(e) => {
            setUserFilter(e.target.value);
            setPage(0);
          }}
        />
      </Stack>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              {!guildId && <TableCell>Guild</TableCell>}
              <TableCell>Event</TableCell>
              <TableCell align="right">Info</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={guildId ? 3 : 4} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : logs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={guildId ? 3 : 4} align="center">
                  No logs found
                </TableCell>
              </TableRow>
            ) : (
              logs.map((log) => {
                const { message, tooltip } = formatLogMessage(log);
                return (
                  <TableRow key={`${log.guild_name || ''}-${log.id}`}>
                    <TableCell>
                      {formatDistanceToNow(new Date(log.time), { addSuffix: true })}
                    </TableCell>
                    {!guildId && (
                      <TableCell>{log.guild_name}</TableCell>
                    )}
                    <TableCell>{message}</TableCell>
                    <TableCell align="right">
                      {tooltip && (
                        <Tooltip title={tooltip} placement="left">
                          <IconButton size="small">
                            <InfoIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        component="div"
        count={total}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[10, 25, 50, 100]}
      />
    </Box>
  );
} 