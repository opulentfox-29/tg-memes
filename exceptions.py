class TooLargeVideo(Exception):
    def __init__(self, size: float):
        self.text = f"Видео слишком большое ({size} MB)."
