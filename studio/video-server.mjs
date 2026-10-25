// Entry point độc lập. Không sửa dữ liệu của ứng dụng Studio gốc.
process.env.STUDIO_APP='video';
process.env.STUDIO_PORT ||= '3211';
process.env.STUDIO_DATA_DIR ||= '.video-studio-data';
await import('./server.mjs');
