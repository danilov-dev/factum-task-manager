from pathlib import Path


def get_logging_config(base_dir: Path, debug: bool) -> dict:

    logs_dir = base_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{asctime} [{levelname}] {name} ({filename}:{lineno}) | {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '[{levelname}] {name}: {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'file_app': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': logs_dir / 'app.log',
                'maxBytes': 1024 * 1024 * 5,
                'backupCount': 5,
                'formatter': 'verbose',
                'encoding': 'utf-8',
            },
            'file_error': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': logs_dir / 'error.log',
                'maxBytes': 1024 * 1024 * 5,
                'backupCount': 3,
                'formatter': 'verbose',
                'encoding': 'utf-8',
            },
        },
        'loggers': {
            'apps': {
                'handlers': ['console', 'file_app', 'file_error'],
                'level': 'DEBUG' if debug else 'INFO',
                'propagate': False,
            },
        },
    }