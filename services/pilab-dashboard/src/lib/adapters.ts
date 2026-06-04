import type {
  PlexItem,
  TrendingMovie,
  TrendingSeries,
  DownloadedMovie,
  DownloadedSeries,
  CardMedia,
} from './types.d.ts';

export function fromPlexItem(item: PlexItem): CardMedia {
  return {
    title:        item.title,
    subtitle:     item.subtitle,
    year:         item.year,
    type:         item.type as CardMedia['type'],
    poster_url:   item.thumb_url,
    art_url:      item.art_url,
    href:         item.plex_link || null,
    progress_pct: item.progress_pct,
    badge:        null,
    owned:        true,
    meta: {
      source:     'plex',
      type:       item.type === 'episode' ? 'show' : item.type as 'movie' | 'show',
      title:      item.title,
      year:       item.year,
      poster_url: item.thumb_url,
      fanart_url: item.art_url,
      in_plex:    true,
      plex_link:  item.plex_link || null,
    },
  };
}

export function fromTrendingMovie(item: TrendingMovie): CardMedia {
  return {
    title:      item.title,
    subtitle:   item.subtitle ?? String(item.year ?? ''),
    year:       item.year,
    type:       'movie',
    poster_url: item.poster_url,
    art_url:    item.fanart_url,
    href:       null,
    badge:      item.owned ? 'Downloaded' : null,
    owned:      item.owned,
    meta: {
      source:     'radarr',
      type:       'movie',
      title:      item.title,
      year:       item.year,
      tmdb_id:    item.tmdb_id,
      imdb_id:    item.imdb_id,
      poster_url: item.poster_url,
      fanart_url: item.fanart_url,
      rating:     item.rating,
      in_radarr:  item.owned,
      in_plex:    false,
    },
  };
}

export function fromTrendingSeries(item: TrendingSeries): CardMedia {
  return {
    title:      item.title,
    subtitle:   item.subtitle,
    year:       item.year,
    type:       'series',
    poster_url: item.poster_url,
    art_url:    item.fanart_url,
    href:       null,
    badge:      item.status === 'continuing' ? 'Ongoing' : null,
    owned:      true,
    meta: {
      source:     'sonarr',
      type:       'show',
      title:      item.title,
      year:       item.year,
      tvdb_id:    item.tvdb_id,
      imdb_id:    item.imdb_id,
      poster_url: item.poster_url,
      fanart_url: item.fanart_url,
      status:     item.status,
      network:    item.network,
      in_sonarr:  true,
      sonarr_id:  item.id,
      in_plex:    false,
    },
  };
}

export function fromDownloadedMovie(item: DownloadedMovie): CardMedia {
  return {
    title:      item.title,
    subtitle:   String(item.year ?? ''),
    year:       item.year,
    type:       'movie',
    poster_url: item.poster_url,
    art_url:    item.fanart_url,
    href:       null,
    badge:      `${item.size_gb} GB`,
    owned:      true,
    meta: {
      source:    'radarr',
      type:      'movie',
      title:     item.title,
      year:      item.year,
      tmdb_id:   item.tmdb_id,
      imdb_id:   item.imdb_id,
      poster_url: item.poster_url,
      fanart_url: item.fanart_url,
      in_radarr:  true,
      radarr_id:  item.id,
      in_plex:    false,
    },
  };
}

export function fromDownloadedSeries(item: DownloadedSeries): CardMedia {
  return {
    title:      item.title,
    subtitle:   `${item.seasons}s · ${item.episodes}ep`,
    year:       item.year,
    type:       'series',
    poster_url: item.poster_url,
    art_url:    item.fanart_url,
    href:       null,
    badge:      `${item.size_gb} GB`,
    owned:      true,
    meta: {
      source:     'sonarr',
      type:       'show',
      title:      item.title,
      year:       item.year,
      tvdb_id:    item.tvdb_id,
      imdb_id:    item.imdb_id,
      poster_url: item.poster_url,
      fanart_url: item.fanart_url,
      status:     item.status,
      network:    item.network,
      in_sonarr:  true,
      sonarr_id:  item.id,
      in_plex:    false,
    },
  };
}