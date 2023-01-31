class TooLargeVideo(Exception):
    def __init__(self, size: float):
        self.text = f"[TG ERROR] Видео слишком большое ({size} MB)."
