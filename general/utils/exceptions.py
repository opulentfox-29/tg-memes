class TooLargeVideo(Exception):
    def __init__(self, size: float):
        self.text = f"[get video] Видео слишком большое ({size} MB)."
