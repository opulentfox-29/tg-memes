class YtdlTotalBytesException(Exception):
    def __init__(self, ex):
        import logger as log
        log.error(f"[ERROR] {ex}")
