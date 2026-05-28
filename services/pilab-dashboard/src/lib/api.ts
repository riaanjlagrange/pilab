import { API_BASE as DEFAULT_API_BASE} from './config';
import { CONTAINER_META, HOST } from './config';
import type {
	SystemStats,
	DiskStats,
	Container,
	PlexData,
	MediaData,
	StatusData,
	Download,
	QueueData,
	Settings
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
		body: JSON.stringify(body)
	});
	console.log(`[API POST] Response:`, res.status, res.statusText);
	if (!res.ok) throw new Error(`API POST ${path} → ${res.status} ${res.statusText}`);
	return res.json() as Promise<T>;
}

// ─── Endpoints ────────────────────────────────────────────────────────────────

/** CPU, RAM, uptime, hostname (Glances v4) */
export const fetchSystem = () => get<SystemStats>('/api/system');

/** Disk free/used/total/threshold */
export const fetchDisk = () => get<DiskStats>('/api/disk');

/** All Docker containers with status + uptime
 * @param all - If true, fetch all containers (no hidden filter). If false or omitted, apply hidden filter.
 */
export const fetchContainers = (all = false) => get<Container[]>(`/api/containers${all ? '?all=true' : ''}`);

/** Plex now_playing + on_deck */
export const fetchPlex = () => get<PlexData>('/api/plex');

/** Movies + series from Radarr/Sonarr */
export const fetchMedia = () => get<MediaData>('/api/media');

/** Combined disk + media (for storage page) */
export const fetchStatus = () => get<StatusData>('/api/status');

/** Active downloads from qBittorrent */
export const fetchDownloads = () => get<Download[]>('/api/downloads');

/** Download queue from Radarr and Sonarr */
export const fetchQueue = () => get<QueueData>('/api/queue');

/** Delete a movie or series by id + type */
export const deleteMedia = (id: number, type: 'movie' | 'series') =>
	post<{ success: boolean; message: string }>('/api/delete', { id, type });

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
	if (value >= warn) return 'text-yellow-400';
	return 'text-green-400';
}

/** Returns Tailwind bg-colour for progress bars */
export function barColor(value: number, warn = 70, danger = 85): string {
	if (value >= danger) return 'bg-red-400';
	if (value >= warn) return 'bg-yellow-400';
	return 'bg-green-400';
}

export { CONTAINER_META, HOST };

export function buildContainerUrl(containerName: string, host: string): string {
	const urlMap: Record<string, (h: string) => string> = {
		plex: (h) => `https://plex.${h}`,
		seerr: (h) => `https://seerr.${h}`,
		radarr: (h) => `https://radarr.${h}`,
		sonarr: (h) => `https://sonarr.${h}`,
		prowlarr: (h) => `https://prowlarr.${h}`,
		qbittorrent: (h) => `https://torrent.${h}`,
		pihole: (h) => `https://pihole.${h}/admin`,
		npm: () => `http://localhost:81`,
		nginxproxymanager: (h) => `http://npm.${h}`,
		wetty: (h) => `https://ssh.${h}`,
		glances: (h) => `https://glances.${h}`,
		dozzle: (h) => `https://logs.${h}`,
		'homelab-api': (h) => `https://api.${h}`,
		filebrowser: (h) => `https://files.${h}`
	};
	return urlMap[containerName]?.(host) || '#';
}
