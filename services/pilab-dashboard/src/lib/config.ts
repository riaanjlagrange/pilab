import { env } from '$env/dynamic/public';

const PUBLIC_DOMAIN = env.PUBLIC_DOMAIN ?? '';

export const HOST = PUBLIC_DOMAIN;
export const API_BASE = `https://api.${PUBLIC_DOMAIN}`;

// ─── Container metadata ───────────────────────────────────────────────────────
export type ContainerCategory = 'media' | 'automation' | 'download' | 'network' | 'system' | 'app';

export interface ContainerMeta {
	label: string;
	icon: string;        // Tabler icon class (ti-*)
	category: ContainerCategory;
	description: string;
}

export const CONTAINER_META: Record<string, ContainerMeta> = {
	// Media
	plex: {
		label: 'Plex',
		icon: 'ti-movie',
		category: 'media',
		description: 'Media streaming server'
	},
	'seerr': {
		label: 'Seerr',
		icon: 'ti-eye',
		category: 'media',
		description: 'Media request management'
	},
	// Automation
	radarr: {
		label: 'Radarr',
		icon: 'ti-movie',
		category: 'automation',
		description: 'Movie collection manager'
	},
	sonarr: {
		label: 'Sonarr',
		icon: 'ti-device-tv',
		category: 'automation',
		description: 'TV series collection manager'
	},
	prowlarr: {
		label: 'Prowlarr',
		icon: 'ti-antenna',
		category: 'automation',
		description: 'Indexer manager / proxy'
	},
	// Download
	qbittorrent: {
		label: 'qBittorrent',
		icon: 'ti-download',
		category: 'download',
		description: 'BitTorrent client'
	},
	// Network
	pihole: {
		label: 'Pi-hole',
		icon: 'ti-shield',
		category: 'network',
		description: 'Network-wide ad blocking'
	},
	'nginxproxymanager': {
		label: 'Nginx Proxy Manager',
		icon: 'ti-server',
		category: 'network',
		description: 'Reverse proxy management'
	},
	npm: {
		label: 'Nginx Proxy Manager',
		icon: 'ti-server',
		category: 'network',
		description: 'Reverse proxy management'
	},
	// System
	wetty: {
		label: 'Wetty',
		icon: 'ti-terminal',
		category: 'system',
		description: 'Web terminal'
	},
	glances: {
		label: 'Glances',
		icon: 'ti-activity',
		category: 'system',
		description: 'System monitoring'
	},
	dozzle: {
		label: 'Dozzle',
		icon: 'ti-file-description',
		category: 'system',
		description: 'Docker log viewer'
	},
	watchtower: {
		label: 'Watchtower',
		icon: 'ti-refresh',
		category: 'system',
		description: 'Automatic container updates'
	},
	// App
	'homelab-api': {
		label: 'Homelab API',
		icon: 'ti-api',
		category: 'app',
		description: 'Flask backend API'
	},
	'homelab-dashboard': {
		label: 'Dashboard',
		icon: 'ti-layout-dashboard',
		category: 'app',
		description: 'pilab dashboard'
	},
	'homelab-storage-manager': {
		label: 'Storage Manager',
		icon: 'ti-database',
		category: 'app',
		description: 'Media storage manager'
	},
	filebrowser: {
		label: 'FileBrowser',
		icon: 'ti-folder',
		category: 'app',
		description: 'Web file manager'
	}
};

// ─── Container URLs ───────────────────────────────────────────────────────────
export const CONTAINER_URLS: Record<string, string> = {
	plex: `https://plex.${HOST}`,
	seerr: `https://seerr.${HOST}`,
	radarr: `https://radarr.${HOST}`,
	sonarr: `https://sonarr.${HOST}`,
	prowlarr: `https://prowlarr.${HOST}`,
	qbittorrent: `https://torrent.${HOST}`,
	pihole: `https://pihole.${HOST}/admin`,
	npm: `http://localhost:81`,
	wetty: `https://ssh.${HOST}`,
	glances: `https://stats.${HOST}`,
	dozzle: `https://logs.${HOST}`,
	'homelab-api': `https://api.${HOST}`,
	filebrowser: `https://files.${HOST}`
};

// ─── Category display order & labels ─────────────────────────────────────────
export const CATEGORY_ORDER: ContainerCategory[] = [
	'media',
	'automation',
	'download',
	'network',
	'system',
	'app'
];

export const CATEGORY_LABELS: Record<ContainerCategory, string> = {
	media: 'Media',
	automation: 'Automation',
	download: 'Downloads',
	network: 'Network',
	system: 'System',
	app: 'Applications'
};
