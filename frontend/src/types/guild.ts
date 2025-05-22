export interface GuildEmblem {
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

export interface GuildData {
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