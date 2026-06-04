import { API_BASE as DEFAULT_API_BASE } from './config';
import { CONTAINER_META, HOST } from './config';
import type {
  SystemStats,
  DiskStats,
  Container,
  StatusData,
  Download,
  QueueData,
  Settings,
  SearchResult,
  ServiceProfiles,
  RequestPayload,
  RequestResult,
  PlexMedia,
  PlexSession,
  RadarrMedia,
  SonarrMedia,
} from './types.d.ts';

const currentApiBase = DEFAULT_API_BASE;

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${currentApiBase}${path}`);
  if (!res.ok) throw new Error(`API ${path} → ${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  console.log(`[API POST] ${currentApiBase}${path}`, body);
  const res = await fetch(`${currentApiBase}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  console.log(`[API POST] Response:`, res.status, res.statusText);
  if (!res.ok) throw new Error(`API POST ${path} → ${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

// ─── Plex ─────────────────────────────────────────────────────────────────────

/** Full Plex library — movies, series, continueWatching, all */
export const fetchPlexMedia = () => get<PlexMedia>('/api/plex/media');

/** Currently active Plex sessions */
export const fetchPlexActive = () => get<PlexSession[]>('/api/plex/active');

/** Search the Plex library */
export const searchPlex = async (q: string): Promise<SearchResult[]> => {
  try {
    return await get<SearchResult[]>(`/api/plex/search?q=${encodeURIComponent(q)}`);
  } catch {
    return [];
  }
};

// ─── Radarr ───────────────────────────────────────────────────────────────────

/** Downloaded movies + trending discover feed */
export const fetchRadarrMedia = () => get<RadarrMedia>('/api/radarr/media');

/** Search Radarr movie lookup */
export const searchRadarr = async (q: string): Promise<SearchResult[]> => {
  try {
    return await get<SearchResult[]>(`/api/radarr/search?q=${encodeURIComponent(q)}`);
  } catch {
    return [];
  }
};

/** Quality profiles and root folders */
export const getRadarrProfiles = async (): Promise<ServiceProfiles> => {
  try {
    return await get<ServiceProfiles>('/api/radarr/profiles');
  } catch {
    return { quality_profiles: [], root_folders: [] };
  }
};

/** Add a movie to Radarr */
export const requestMovie = (payload: RequestPayload) =>
  post<RequestResult>('/api/radarr/request', payload);

/** Delete a movie from Radarr (and disk) */
export const deleteMovie = (id: number) =>
  post<{ ok: boolean; error?: string }>('/api/radarr/delete', { id });

// ─── Sonarr ───────────────────────────────────────────────────────────────────

/** Downloaded series + recently-added (trending) feed */
export const fetchSonarrMedia = () => get<SonarrMedia>('/api/sonarr/media');

/** Search Sonarr series lookup */
export const searchSonarr = async (q: string): Promise<SearchResult[]> => {
  try {
    return await get<SearchResult[]>(`/api/sonarr/search?q=${encodeURIComponent(q)}`);
  } catch {
    return [];
  }
};

/** Quality profiles and root folders */
export const getSonarrProfiles = async (): Promise<ServiceProfiles> => {
  try {
    return await get<ServiceProfiles>('/api/sonarr/profiles');
  } catch {
    return { quality_profiles: [], root_folders: [] };
  }
};

/** Add a series to Sonarr */
export const requestShow = (payload: RequestPayload) =>
  post<RequestResult>('/api/sonarr/request', payload);

/** Delete a series from Sonarr (and disk) */
export const deleteSeries = (id: number) =>
  post<{ ok: boolean; error?: string }>('/api/sonarr/delete', { id });

// ─── System ───────────────────────────────────────────────────────────────────

/** CPU, RAM, uptime, hostname */
export const fetchSystem = () => get<SystemStats>('/api/system');

/** Disk free/used/total/threshold */
export const fetchDisk = () => get<DiskStats>('/api/disk');

/** All Docker containers with status + uptime */
export const fetchContainers = (all = false) =>
  get<Container[]>(`/api/containers${all ? '?all=true' : ''}`);

/** Combined disk + media (for storage page) */
export const fetchStatus = () => get<StatusData>('/api/status');

/** Active downloads from qBittorrent */
export const fetchDownloads = () => get<Download[]>('/api/downloads');

/** Download queue from Radarr and Sonarr */
export const fetchQueue = () => get<QueueData>('/api/queue');

/** Fetch current settings */
export const fetchSettings = () => get<Settings>('/api/settings');

/** Save settings */
export const saveSettings = (settings: Settings) =>
  post<{ success: boolean }>('/api/settings', settings);

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Format bytes → human-readable string (e.g. "1.23 TB") */
export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}

/** Returns Tailwind colour class based on value + thresholds */
export function statusColor(value: number, warn = 70, danger = 85): string {
  if (value >= danger) return 'text-red-400';
  if (value >= warn)   return 'text-yellow-400';
  return 'text-green-400';
}

/** Returns Tailwind bg-colour for progress bars */
export function barColor(value: number, warn = 70, danger = 85): string {
  if (value >= danger) return 'bg-red-400';
  if (value >= warn)   return 'bg-yellow-400';
  return 'bg-green-400';
}

export { CONTAINER_META, HOST };

export function buildContainerUrl(containerName: string, host: string): string {
  const urlMap: Record<string, (h: string) => string> = {
    plex:                 (h) => `https://plex.${h}`,
    seerr:                (h) => `https://seerr.${h}`,
    radarr:               (h) => `https://radarr.${h}`,
    sonarr:               (h) => `https://sonarr.${h}`,
    prowlarr:             (h) => `https://prowlarr.${h}`,
    qbittorrent:          (h) => `https://torrent.${h}`,
    pihole:               (h) => `https://pihole.${h}/admin`,
    npm:                  ()  => `http://localhost:81`,
    nginxproxymanager:    (h) => `http://npm.${h}`,
    wetty:                (h) => `https://ssh.${h}`,
    glances:              (h) => `https://glances.${h}`,
    dozzle:               (h) => `https://logs.${h}`,
    'homelab-api':        (h) => `https://api.${h}`,
    filebrowser:          (h) => `https://files.${h}`,
  };
  return urlMap[containerName]?.(host) || '#';
}