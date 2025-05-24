import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Typography,
  Pagination,
  useTheme,
  IconButton,
  Tooltip,
  SelectChangeEvent,
  Chip,
  Collapse,
  CircularProgress,
  useMediaQuery,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { useItems } from '../hooks/useItems';
import { GW2Item, Rarity } from '../types/gw2-items';

const RarityColors: Record<Rarity, string> = {
  Junk: '#AAA',
  Basic: '#000',  // Back to black for accuracy
  Fine: '#62A4DA',
  Masterwork: '#1a9306',
  Rare: '#fcd00b',
  Exotic: '#ffa405',
  Ascended: '#fb3e8d',
  Legendary: '#856088',
};

// Add styles for each rarity
const RarityStyles: Record<Rarity, React.CSSProperties> = {
  Junk: {},
  Basic: {
    textShadow: '0 0 2px #fff',  // White glow for black text
  },
  Fine: {},
  Masterwork: {},
  Rare: {
    textShadow: '0 0 4px rgba(252, 208, 11, 0.3)',  // Subtle yellow glow
  },
  Exotic: {
    textShadow: '0 0 4px rgba(255, 164, 5, 0.3)',   // Subtle orange glow
  },
  Ascended: {
    textShadow: '0 0 4px rgba(251, 62, 141, 0.3)',  // Subtle pink glow
  },
  Legendary: {
    textShadow: '0 0 6px rgba(133, 96, 136, 0.5)',  // More pronounced purple glow
  },
};

interface BaseGuildLog {
  // Required fields for all log types
  id: number;
  time: string;
  type: string;
  user: string;
  guild_name?: string;
  guild_tag?: string;
}

interface StashLog extends BaseGuildLog {
  type: 'stash';
  operation?: 'deposit' | 'withdraw';
  item_id?: number;
  count?: number;
  coins?: number;
  item_name?: string;
}

interface InvitedLog extends BaseGuildLog {
  type: 'invited';
  invited_by?: string;
}

interface TreasuryLog extends BaseGuildLog {
  type: 'treasury';
  item_id?: number;
  count?: number;
  item_name?: string;
}

interface MotdLog extends BaseGuildLog {
  type: 'motd';
  motd?: string;
}

interface UpgradeLog extends BaseGuildLog {
  type: 'upgrade';
  action?: string;
  upgrade_id?: number;
  item_id?: number;
  recipe_id?: number;
  count?: number;
  upgrade_name?: string;
}

interface JoinLog extends BaseGuildLog {
  type: 'join';
}

interface KickLog extends BaseGuildLog {
  type: 'kick';
  kicked_by?: string;
}

interface RankChangeLog extends BaseGuildLog {
  type: 'rank_change';
  old_rank?: string;
  new_rank?: string;
}

interface InfluenceLog extends BaseGuildLog {
  type: 'influence';
  activity?: string; // e.g., "daily_login", "gifted"
  participants?: number;
  total_participants?: string[]; // Should be array of strings if deserialized correctly
}

interface MissionLog extends BaseGuildLog {
  type: 'mission';
  state?: string; // e.g., "start", "success", "fail"
  influence?: number; // Influence awarded
}

interface InviteDeclineLog extends BaseGuildLog {
  type: 'invite_declined';
  declined_by?: string;
}

type GuildLog = StashLog | InvitedLog | TreasuryLog | MotdLog | UpgradeLog | JoinLog | KickLog | RankChangeLog |
                InfluenceLog | MissionLog | InviteDeclineLog;

const LOG_TYPES = [
  'stash',
  'treasury',
  'motd',
  'upgrade',
  'invited',
  'join',
  'kick',
  'rank_change',
  'influence',
  'mission',
  'invite_declined'
] as const;

type LogType = typeof LOG_TYPES[number];

interface LogRowProps {
  log: GuildLog;
  theme: any;
  itemDetailsMap: Record<number, GW2Item>;
  isLoadingItemDetails: boolean;
}

const LogRow: React.FC<LogRowProps> = ({ log, theme, itemDetailsMap, isLoadingItemDetails }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const formatGuildDisplay = (log: GuildLog): string => {
    if (!log.guild_name) return 'Unknown Guild';
    return log.guild_name;
  };

  const renderItemName = (itemId?: number, defaultName: string = 'Unknown item') => {
    if (!itemId) return defaultName;
    
    const item = itemDetailsMap[itemId];
    if (item) {
      return (
        <Tooltip title={item.description || ''}>
          <Typography
            component="span"
            sx={{
              color: RarityColors[item.rarity],
              cursor: 'help',
              ...RarityStyles[item.rarity],  // Apply rarity-specific styles
            }}
          >
            {item.name}
          </Typography>
        </Tooltip>
      );
    }
    
    if (isLoadingItemDetails) {
      return (
        <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
          <CircularProgress size={12} />
          <span>Loading item...</span>
        </Box>
      );
    }
    
    return `Item #${itemId}`;
  };

  const renderLogSummary = (log: GuildLog): React.ReactNode => {
    switch (log.type) {
      case 'stash':
        if (log.coins) { return `${log.operation || 'Unknown op.'} ${log.coins.toLocaleString()} coins`; }
        return (<span>{log.operation || 'Unknown op.'} {log.count || 0} x {renderItemName(log.item_id, log.item_name || 'Unknown item')}</span>);
      case 'treasury':
        return (<span>{log.count || 0} x {renderItemName(log.item_id, log.item_name || 'Unknown item')}</span>);
      case 'motd':
        return `Changed MOTD`;
      case 'upgrade':
        let upgradeIdentifier: React.ReactNode = log.upgrade_name;
        if (!upgradeIdentifier && log.item_id) {
          upgradeIdentifier = renderItemName(log.item_id);
        } else if (!upgradeIdentifier && log.upgrade_id) {
          upgradeIdentifier = `#${log.upgrade_id}`;
        } else if (!upgradeIdentifier) {
          upgradeIdentifier = 'Unknown upgrade';
        }
        return `${log.action || 'Unknown action'} upgrade: ${typeof upgradeIdentifier === 'string' ? upgradeIdentifier : ''}`;
      case 'invited': return `Invited by ${log.invited_by || 'Unknown'}`;
      case 'join': return 'Joined the guild';
      case 'kick': return `${log.user} was kicked by ${log.kicked_by || 'Unknown'}`;
      case 'rank_change': return `Rank changed from ${log.old_rank || 'Unknown'} to ${log.new_rank || 'Unknown'}`;
      case 'influence':
        const influenceActivity = log.activity === 'daily_login' ? 'Daily Login' : log.activity;
        return `Influence: ${influenceActivity || 'Unknown'} (${log.participants || 0} participants)`;
      case 'mission':
        return `Mission ${log.state || 'event'}${log.influence ? ` (Influence: ${log.influence})` : ''}`;
      case 'invite_declined':
        return `Invite declined by ${log.declined_by || 'Unknown'}`;
      default:
        const unknownLog = log as any;
        return `Unknown action: ${unknownLog.type}`;
    }
  };

  const detailedInfoContent = useMemo(() => {
    switch (log.type) {
      case 'stash':
        if (log.operation === 'deposit' || log.operation === 'withdraw') {
            return null; 
        }
        return (
          <Box sx={{ pl: { xs: 2, sm: 4 }, py: 1 }}>
            <Typography variant="body2" component="div">
              <strong>Operation:</strong> {log.operation || 'Unknown'}
              {log.coins ? (
                <Box component="span" sx={{ ml: 2 }}><strong>Coins:</strong> {log.coins.toLocaleString()}</Box>
              ) : (
                <>
                  {log.item_id && (<Box component="span" sx={{ ml: 2 }}><strong>Item:</strong> {renderItemName(log.item_id)}</Box>)}
                  {log.count !== undefined && (<Box component="span" sx={{ ml: 2 }}><strong>Count:</strong> {log.count}</Box>)}
                </>
              )}
            </Typography>
          </Box>
        );
      case 'motd':
        return (
          <Box sx={{ pl: { xs: 2, sm: 4 }, py: 1 }}>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{log.motd || 'Empty MOTD'}</Typography>
          </Box>
        );
      case 'influence':
        return (
          <Box sx={{ pl: { xs: 2, sm: 4 }, py: 1 }}>
            <Typography variant="body2" component="div">
              <strong>Activity:</strong> {log.activity === 'daily_login' ? 'Daily Login' : log.activity || 'Unknown'}<br />
              <strong>Participants involved:</strong> {log.participants || 'N/A'}<br />
              {log.total_participants && log.total_participants.length > 0 && (
                <><strong>Participant List:</strong> {log.total_participants.join(', ')}
                </>
              )}
            </Typography>
          </Box>
        );
      case 'mission':
        return (
          <Box sx={{ pl: { xs: 2, sm: 4 }, py: 1 }}>
            <Typography variant="body2" component="div">
              <strong>State:</strong> {log.state || 'Unknown'}<br />
              {log.influence !== undefined && <><strong>Influence Awarded:</strong> {log.influence}</>}
            </Typography>
          </Box>
        );
      case 'invite_declined': // No extra details beyond summary needed for this one for now.
        return null;
      default:
        return null;
    }
  }, [log, itemDetailsMap, isLoadingItemDetails]);

  const hasDetails = detailedInfoContent !== null;

  const cellSx = { py: { xs: 0.5, sm: 1 }, px: { xs: 1, sm: 2 } };
  const expandCellSx = { width: { xs: '36px', sm: '48px' }, p: {xs: 0.25, sm: 0.5 }, ...cellSx, textAlign: 'center' };

  return (
    <>
      <TableRow 
        sx={{ 
          '&:hover': { bgcolor: theme.palette.action.hover },
          cursor: 'pointer'
        }}
      >
        <TableCell sx={expandCellSx}>
          {hasDetails && (
            <IconButton
              aria-label="expand row"
              size={isMobile ? "small" : "medium"}
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
            </IconButton>
          )}
        </TableCell>
        <TableCell sx={cellSx}>{new Date(log.time).toLocaleString()}</TableCell>
        <TableCell sx={cellSx}>
          <Chip 
            label={formatGuildDisplay(log)}
            size="small"
            sx={{ 
              backgroundColor: theme.palette.primary.main + '20',
              color: theme.palette.primary.main
            }}
          />
        </TableCell>
        <TableCell sx={cellSx}>
          <Typography 
            component="span" 
            sx={{ 
              textTransform: 'capitalize',
              color: theme.palette.secondary.main
            }}
          >
            {log.type}
          </Typography>
        </TableCell>
        <TableCell sx={cellSx}>{log.user}</TableCell>
        <TableCell sx={cellSx}>{renderLogSummary(log)}</TableCell>
      </TableRow>
      {hasDetails && (
        <TableRow>
          <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
            <Collapse in={isExpanded} timeout="auto" unmountOnExit>
              {detailedInfoContent}
            </Collapse>
          </TableCell>
        </TableRow>
      )}
    </>
  );
};

const GuildLogsPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [logs, setLogs] = useState<GuildLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchUser, setSearchUser] = useState('');
  const [selectedType, setSelectedType] = useState<LogType | ''>('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const [itemDetailsMap, setItemDetailsMap] = useState<Record<number, GW2Item>>({});
  const [isLoadingItemDetails, setIsLoadingItemDetails] = useState(false);
  const { getItems } = useItems();

  // Ref to track the JSON stringified representation of item IDs currently being fetched.
  const activeFetchKeyRef = useRef<string | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const queryParams = new URLSearchParams({
        page: page.toString(),
        limit: '100',
      });

      if (searchUser) {
        queryParams.append('user', searchUser);
      }
      if (selectedType) {
        queryParams.append('type', selectedType);
      }

      const response = await fetch(`/api/logs?${queryParams}`);
      if (!response.ok) {
        throw new Error('Failed to fetch guild logs');
      }

      const data = await response.json();
      setLogs(data.logs);
      setTotalPages(Math.ceil(data.total / 100));
      // When new logs are loaded, any ongoing item fetch for previous logs is no longer relevant in the same way.
      // We can clear the key. A new key will be generated by the item fetching effect if needed.
      activeFetchKeyRef.current = null; 
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, searchUser, selectedType]);

  useEffect(() => {
    if (logs && logs.length > 0) {
      const uniqueItemIds: number[] = [];
      logs.forEach((log: GuildLog) => {
        let itemId: number | undefined = undefined;
        if ((log.type === 'stash' || log.type === 'treasury') && 'item_id' in log && log.item_id) {
          itemId = log.item_id;
        } else if (log.type === 'upgrade' && 'item_id' in log && log.item_id) {
          itemId = log.item_id;
        }
        if (itemId && !uniqueItemIds.includes(itemId)) {
          uniqueItemIds.push(itemId);
        }
      });

      if (uniqueItemIds.length > 0) {
        const idsToFetch = uniqueItemIds.filter(id => !itemDetailsMap[id]);
        
        if (idsToFetch.length > 0) {
          idsToFetch.sort((a, b) => a - b); // Ensure stable order for the key
          const currentFetchKey = JSON.stringify(idsToFetch);

          if (activeFetchKeyRef.current === currentFetchKey) {
            // This exact set of IDs is already being fetched, so do nothing.
            return;
          }

          activeFetchKeyRef.current = currentFetchKey; // Mark this set of IDs as being fetched.
          setIsLoadingItemDetails(true);

          getItems(idsToFetch)
            .then(fetchedItems => {
              setItemDetailsMap(prevMap => {
                const newMap = { ...prevMap };
                fetchedItems.forEach(item => {
                  if (item) {
                    newMap[item.id] = item;
                  }
                });
                return newMap;
              });
            })
            .catch(itemError => {
              console.error("Failed to fetch item details in bulk:", itemError);
              // If this specific fetch failed, clear the key so it can be retried.
              if (activeFetchKeyRef.current === currentFetchKey) {
                activeFetchKeyRef.current = null;
              }
            })
            .finally(() => {
              setIsLoadingItemDetails(false);
              // Optionally, if we want to allow re-fetch of the *same key* only after it completes (even if successful),
              // we could clear activeFetchKeyRef.current here, but it might lead to quick re-fetches if logs haven't changed.
              // For now, leaving it set means this exact set won't re-fetch until logs change and produce a *different* set of missing IDs.
              // Or if fetchLogs clears it.
            });
        } else {
          // No new items to fetch for the current logs, clear the active fetch key.
          activeFetchKeyRef.current = null;
        }
      }
    } else {
      // No logs, so no items to fetch. Clear any active fetch key.
      activeFetchKeyRef.current = null;
    }
  }, [logs, getItems, itemDetailsMap]); // itemDetailsMap is needed for the filter logic.

  const handleUserSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchUser(event.target.value);
    setPage(1);
  };

  const handleTypeChange = (event: SelectChangeEvent<LogType | ''>) => {
    setSelectedType(event.target.value as LogType | '');
    setPage(1);
  };

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  return (
    <Box sx={{ p: {xs: 1, sm: 2, md: 3} }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Guild Activity Logs
      </Typography>

      <Box sx={{ 
        mb: { xs: 1.5, sm: 2, md: 3 },
        display: 'flex',
        flexDirection: { xs: 'column', sm: 'row' },
        gap: 1.5,
        alignItems: { xs: 'stretch', sm: 'center' }
      }}>
        <TextField
          label="Search by User"
          variant="outlined"
          size="small"
          value={searchUser}
          onChange={handleUserSearch}
          sx={{ flexGrow: {sm: 1}, minWidth: {xs: 'auto', sm: 150} }}
        />
        
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'nowrap'}}>
          <FormControl size="small" sx={{ minWidth: {xs: 'calc(100% - 60px)', sm: 180}, flexGrow:1 }}>
            <InputLabel>Filter by Type</InputLabel>
            <Select value={selectedType} label="Filter by Type" onChange={handleTypeChange}>
              <MenuItem value="">All Types</MenuItem>
              {LOG_TYPES.map((type) => {
                let displayName = type.charAt(0).toUpperCase() + type.slice(1);
                if (type === 'motd') displayName = 'MOTD';
                if (type === 'rank_change') displayName = 'Rank Change';
                if (type === 'invite_declined') displayName = 'Invite Declined';
                // Add more custom display names if needed (e.g., for 'influence', 'mission')
                return (
                  <MenuItem key={type} value={type}>
                    {displayName}
                  </MenuItem>
                );
              })}
            </Select>
          </FormControl>
          <Tooltip title="Refresh Logs">
            <IconButton onClick={() => fetchLogs()} color="primary" sx={{p:1}}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <TableContainer 
        component={Paper} 
        sx={{ mb: 2, maxHeight: 'calc(100vh - 280px)', overflow: 'auto' }}
      >
        <Table stickyHeader size={isMobile ? "small" : "medium"}>
          <TableHead>
            <TableRow>
              <TableCell sx={{ width: { xs: '36px', sm: '48px' }, p: {xs: 0.25, sm: 0.5 }, textAlign: 'center' }} />
              <TableCell sx={{ py: { xs: 0.5, sm: 1 }, px: { xs: 1, sm: 2 } }}>Time</TableCell>
              <TableCell sx={{ py: { xs: 0.5, sm: 1 }, px: { xs: 1, sm: 2 } }}>Guild</TableCell>
              <TableCell sx={{ py: { xs: 0.5, sm: 1 }, px: { xs: 1, sm: 2 } }}>Type</TableCell>
              <TableCell sx={{ py: { xs: 0.5, sm: 1 }, px: { xs: 1, sm: 2 } }}>User</TableCell>
              <TableCell sx={{ py: { xs: 0.5, sm: 1 }, px: { xs: 1, sm: 2 } }}>Summary</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={6} align="center">Loading...</TableCell></TableRow>
            ) : logs.length === 0 ? (
              <TableRow><TableCell colSpan={6} align="center">No logs found</TableCell></TableRow>
            ) : (
              logs.map((log) => (
                <LogRow 
                  key={`${log.id}-${log.time}`} 
                  log={log} 
                  theme={theme}
                  itemDetailsMap={itemDetailsMap}
                  isLoadingItemDetails={isLoadingItemDetails}
                />
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
        <Pagination
          count={totalPages}
          page={page}
          onChange={handlePageChange}
          color="primary"
          showFirstButton
          showLastButton
        />
      </Box>
    </Box>
  );
};

export default GuildLogsPage; 