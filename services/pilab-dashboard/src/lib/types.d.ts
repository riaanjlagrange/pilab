// ─── Shared primitives ────────────────────────────────────────────────────────

export type SearchSource = 'radarr' | 'sonarr' | 'plex';
export type MediaType    = 'movie' | 'show' | 'episode' | 'series';

// ─── Search ───────────────────────────────────────────────────────────────────

export interface SearchResult {
  source:      SearchSource;
  type:        MediaType;
  title:       string;
  year?:       number;
  overview?:   string;
  tmdb_id?:    number;
  tvdb_id?:    number;
  imdb_id?:    string;
  poster_url?: string | null;
  fanart_url?: string | null;
  rating?:     number | null;
  status?:     string;
  network?:    string;
  in_plex?:    boolean;
  plex_link?:  string | null;
  in_radarr?:  boolean;
  radarr_id?:  number | null;
  in_sonarr?:  boolean;
  sonarr_id?:  number | null;
}

// ─── Profiles & requests ──────────────────────────────────────────────────────

export interface QualityProfile {
  id:   number;
  name: string;
}

export interface RootFolder {
  id:   number;
  path: string;
}

export interface ServiceProfiles {
  quality_profiles: QualityProfile[];
  root_folders:     RootFolder[];
}

export interface RequestPayload {
  quality_profile_id: number;
  root_folder:        string;
  tmdb_id?:           number;
  tvdb_id?:           number;
}

export interface RequestResult {
  ok:     boolean;
  id?:    number;
  error?: string;
}

// ─── Plex ─────────────────────────────────────────────────────────────────────

export interface PlexItem {
  type:          MediaType;
  title:         string;
  subtitle:      string;
  year?:         number;
  rating_key:    string;
  key:           string;
  thumb_url?:    string | null;
  art_url?:      string | null;
  plex_link:     string;
  progress_pct?: number | null;
}

export interface PlexSession extends PlexItem {
  user:  string;
  state: string;
}

export interface PlexMedia {
  all:              PlexItem[];
  movies:           PlexItem[];
  series:           PlexItem[];
  continueWatching: PlexItem[];
}

// ─── Radarr / Sonarr library items ────────────────────────────────────────────

export interface DownloadedMovie {
  id:          number;
  type:        'movie';
  title:       string;
  year?:       number;
  size_gb:     number;
  added:       string;
  tmdb_id?:    number;
  imdb_id?:    string;
  poster_url?: string | null;
  fanart_url?: string | null;
}

export interface DownloadedSeries {
  id:          number;
  type:        'series';
  title:       string;
  year?:       number;
  size_gb:     number;
  added:       string;
  episodes:    number;
  seasons:     number;
  tvdb_id?:    number;
  imdb_id?:    string;
  poster_url?: string | null;
  fanart_url?: string | null;
  status?:     string;
  network?:    string;
}

export interface TrendingMovie {
  id:          null;
  type:        'movie';
  title:       string;
  subtitle:    string;
  year?:       number;
  tmdb_id?:    number;
  imdb_id?:    string;
  poster_url?: string | null;
  fanart_url?: string | null;
  rating?:     number | null;
  owned:       boolean;
}

export interface TrendingSeries {
  id:          number;
  type:        'series';
  title:       string;
  subtitle:    string;
  year?:       number;
  tvdb_id?:    number;
  imdb_id?:    string;
  poster_url?: string | null;
  fanart_url?: string | null;
  episodes:    number;
  seasons:     number;
  status?:     string;
  network?:    string;
}

export interface RadarrMedia {
  downloaded: DownloadedMovie[];
  trending:   TrendingMovie[];
}

export interface SonarrMedia {
  downloaded: DownloadedSeries[];
  trending:   TrendingSeries[];
}

// ─── Normalized card type ─────────────────────────────────────────────────────

/**
 * Universal shape for MediaScrollCard.
 * `meta` carries SearchResult-compatible data so the detail modal can open.
 */
export interface CardMedia {
  title:         string;
  subtitle:      string;
  year?:         number;
  type:          'movie' | 'series' | 'episode' | 'show';
  poster_url?:   string | null;
  art_url?:      string | null;
  href?:         string | null;
  progress_pct?: number | null;
  badge?:        string | null;
  owned?:        boolean;
  meta?:         SearchResult;
}

// ─── System ───────────────────────────────────────────────────────────────────

export interface SystemStats {
  pilab_name:     string;
  cpu_percent:    number;
  cpu_temp:       number;
  ram_percent:    number;
  ram_used_gb:    number;
  ram_total_gb:   number;
  uptime_human:   string;
  uptime_seconds: number;
}

export interface DiskStats {
  free_gb:      number;
  used_gb:      number;
  total_gb:     number;
  percent_used: number;
}

export interface Container {
  name:           string;
  status:         'running' | 'exited' | 'paused' | 'restarting' | string;
  uptime_human:   string;
  uptime_seconds: number;
}

// ─── Downloads & queue ────────────────────────────────────────────────────────

export interface Download {
  id:       string;
  status:   'downloading' | 'metaDL' | 'forcedDL' | string;
  progress: number;
  speed_mb: number;
  eta:      string;
  size_gb:  number;
}

export interface QueueItem {
  id:           string;
  title:        string;
  status:       string;
  progress:     number;
  speed_mb:     number;
  eta:          string;
  size_gb:      number;
  completed_gb: number;
  seeds:        number;
  peers:        number;
  added_on:     number;
  category:     string;
  tags:         string;
}

export interface QueueData {
  movies: QueueItem[];
  series: QueueItem[];
}

export interface StatusData {
  disk:         DiskStats;
  movies:       DownloadedMovie[];
  series:       DownloadedSeries[];
  threshold_gb: number;
}

// ─── Settings ─────────────────────────────────────────────────────────────────

export interface Settings {
  pilabName:            string;
  diskThreshold:        number;
  checkIntervalMinutes: number;
  hiddenContainers:     string[];
  ntfyTopic:            string;
}

// ─── Alerts ───────────────────────────────────────────────────────────────────

export type AlertType = 'error' | 'warning' | 'info';

export interface Alert {
  id:         string;
  type:       AlertType;
  message:    string;
  link?:      string;
  linkLabel?: string;
}

// ─── Convenience unions ───────────────────────────────────────────────────────

export type LibraryItem  = DownloadedMovie | DownloadedSeries;
export type TrendingItem = TrendingMovie   | TrendingSeries;