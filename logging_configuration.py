import logging
import logging.config
import sys
from pathlib import Path
import datetime


def set_logging(result_dir_path: str = "results"):
    results_dir = Path(result_dir_path)
    results_dir.mkdir(exist_ok=True)

    logging.config.dictConfig({
        "version": 1,
        "formatters": {
            "named": {
                "format": "%(levelname)-8s %(message)s"
            },
            "unnamed": {
                "format": "%(message)s"
            }
        },
        "handlers": {
            "console-named": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "named"
            },
            "file-named": {
                "class": "logging.FileHandler",
                "filename": results_dir / f"results_{datetime.datetime.now().strftime('%d-%m-%H-%M-%S')}.txt",
                "formatter": "unnamed"
            }
        },
        "loggers": {
            "evaluate_performance_gmap_logger": {
                "level": "DEBUG",
                "handlers": ["console-named", "file-named"]
            },
            "evaluate_performance_compute_diffusion_distance_logger": {
                "level": "DEBUG",
                "handlers": ["console-named", "file-named"]
            },
            "gmap_logger": {
                "level": "INFO",
                "handlers": ["console-named"]
            }
        },
    })
