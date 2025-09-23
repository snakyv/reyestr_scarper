BOT_NAME = "court_registry"

SPIDER_MODULES = ["court_registry.spiders"]
NEWSPIDER_MODULE = "court_registry.spiders"

FEED_EXPORT_ENCODING = "utf-8"

DOWNLOAD_DELAY = 1.0
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 8.0

MAX_PAGES = 3

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
LOG_LEVEL = "INFO"
