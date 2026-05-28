import { env } from '$env/dynamic/public';

const PUBLIC_HOST = env.PUBLIC_HOST || 'localhost';

export const HOST = PUBLIC_HOST;
export const API_BASE = `http://${PUBLIC_HOST}:5050`;

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
	'pilab-api': {
		label: 'Pilab API',
		icon: 'ti-api',
		category: 'app',
		description: 'Flask backend API'
	},
	'pilab-db': {
		label: 'Pilab DB',
		icon: 'ti-database',
		category: 'app',
		description: 'PostgreSQL database for Pilab'
	},
	'pilab-dashboard': {
		label: 'Dashboard',
		icon: 'ti-layout-dashboard',
		category: 'app',
		description: 'pilab dashboard'
	},
	filebrowser: {
		label: 'FileBrowser',
		icon: 'ti-folder',
		category: 'app',
		description: 'Web file manager'
	},
	'wg-easy': {
		label: 'WG Easy',
		icon: 'ti-lock',
		category: 'app',
		description: 'WireGuard VPN management'
	}
};

// ─── Container URLs ───────────────────────────────────────────────────────────
export const CONTAINER_URLS: Record<string, string> = {
	plex: `http://${HOST}:32400/web`,
	seerr: `http://${HOST}:5055`,
	radarr: `http://${HOST}:7878`,
	sonarr: `http://${HOST}:8989`,
	prowlarr: `http://${HOST}:9696`,
	qbittorrent: `http://${HOST}:8080`,
	pihole: `http://${HOST}:8888/admin`,
	nginxproxymanager: `http://${HOST}:81`,
	wetty: `http://${HOST}:3000`,
	glances: `http://${HOST}:61208`,
	dozzle: `http://${HOST}:9999`,
	'pilab-api': `http://${HOST}:5050`,
	'pilab-db': `http://${HOST}:5432`,
	filebrowser: `http://${HOST}:8181`,
	'wg-easy': `http://${HOST}:51821`
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
