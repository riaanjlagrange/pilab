export interface SystemStats {
  pilab_name: string;
  cpu_percent: number;
  cpu_temp: number;
  ram_percent: number;
  ram_used_gb: number;
  ram_total_gb: number;
  uptime_human: string;
  uptime_seconds: number;
}

export interface DiskStats {
  free_gb: number;
  used_gb: number;
  total_gb: number;
  percent_used: number;
}

export interface Container {
  name: string;
  status: 'running' | 'exited' | 'paused' | 'restarting' | string;
  uptime_human: string;
  uptime_seconds: number;
}

export interface NowPlayingItem {
  type: 'movie' | 'episode' | string;
  title: string;
  user: string;
  state: string;
  show?: string;
  episode?: string;
  progress_pct?: number;
  thumb_url?: string | null;
  plex_link?: string | null;
}

export interface OnDeckItem {
  type: 'movie' | 'episode' | string;
  title: string;
  subtitle: string;
  year?: number;
  rating_key: string;
  key: string;
  thumb_url?: string | null;
  art_url?: string | null;
  plex_link: string;
  progress_pct?: number;
}

export interface PlexData {
  now_playing: NowPlayingItem[];
  on_deck: OnDeckItem[];
}
export interface MovieItem {
  id: number;
  title: string;
  type: 'movie';
  year: number;
  size_gb: number;
  added: string;
}

export interface SeriesItem {
  id: number;
  title: string;
  type: 'series';
  year: number;
  size_gb: number;
  episodes: number;
  added: string;
}

export type MediaItem = (MovieItem | SeriesItem) & { status?: string };

export interface MediaData {
  movies: MovieItem[];
  series: SeriesItem[];
}

export interface StatusData {
  disk: DiskStats;
  movies: MovieItem[];
  series: SeriesItem[];
  threshold_gb: number;
}

export interface Download {
  id: string;
  status: 'downloading' | 'metaDL' | 'forcedDL' | string;
  progress: number;
  speed_mb: number;
  eta: string;
  size_gb: number;
}

export interface QueueItem {
  id: string;
  title: string;
  status: string;
  progress: number;
  speed_mb: number;
  eta: string;
  size_gb: number;
  completed_gb: number;
  seeds: number;
  peers: number;
  added_on: number;
  category: string;
  tags: string;
}

export interface QueueData {
  movies: QueueItem[];
  series: QueueItem[];
}

export type AlertType = 'error' | 'warning' | 'info';

export interface Alert {
  id: string;
  type: AlertType;
  message: string;
  link?: string;
  linkLabel?: string;
}

export interface Settings {
  pilabName: string;
  diskThreshold: number;
  checkIntervalMinutes: number;
  hiddenContainers: string[];
  ntfyTopic: string;
}
