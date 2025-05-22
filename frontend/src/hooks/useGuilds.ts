import { useState, useEffect, useCallback } from 'react';

interface GuildMember {
  name: string;
  full_name: string;
  rank: string;
  joined: string | null;
  wvw_member: boolean;
}

interface GuildRank {
  id: string;
  order: number;
  permissions: string[];
  icon: string | null;
}

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

export interface Guild {
  id: string;
  name: string;
  short_name: string;
  tag: string;
  level: number;
  motd: string;
  influence: number;
  aetherium: number;
  resonance: number;
  favor: number;
  emblem: GuildEmblem;
  members: GuildMember[];
  ranks: GuildRank[];
  last_updated: string | null;
  last_log_id: number;
}

export function useGuilds() {
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGuilds = useCallback(async (forceRefresh: boolean = false) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/guilds${forceRefresh ? '?force_refresh=true' : ''}`);
      if (!response.ok) {
        throw new Error('Failed to fetch guild data');
      }
      const data = await response.json();
      setGuilds(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGuilds();
  }, [fetchGuilds]);

  return {
    guilds,
    loading,
    error,
    refreshGuilds: (forceRefresh: boolean = true) => fetchGuilds(forceRefresh)
  };
} 