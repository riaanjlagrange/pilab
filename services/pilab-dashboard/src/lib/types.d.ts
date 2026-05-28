export interface SystemStats {
  pilab_name: string;
  cpu_percent: number;
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
  title: string;
  user: string;
  progress: number;
  duration: number;
  thumb?: string;
  type: 'movie' | 'episode' | string;
  grandparent_title?: string;
}

export interface OnDeckItem {
  title: string;
  thumb?: string;
  type: 'movie' | 'episode' | string;
  grandparent_title?: string;
  year?: number;
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
  name: string;
  progress: number;
  speed_mb: number;
  eta: string;
  size_gb: number;
  state: string;
}

export interface QueueItem {
  id: number;
  title: string;
  status: string;
  progress: number;
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
