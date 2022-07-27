from colorama import init
from colorama import Fore, Style
init()


def log(text: str) -> None:
    """Логирование."""
    print(text)


def warning(text: str) -> None:
    """Предупреждение."""
    print(Fore.YELLOW + text + Style.RESET_ALL)


def error(text: str) -> None:
    """Сообщение об ошибке."""
    print(Fore.RED + text + Style.RESET_ALL)


def download_video(download_bytes: int, vid_len: float, finished: bool = False):
    """Анимация скачивания видео."""
    download_mb = round(download_bytes / 1024 / 1024, 1)
    if finished:
        print(f'\r[download video] {download_mb} MB. finished.{" "*10}')
    else:
        print(f'\r[download video] {download_mb} MB. out of {vid_len} MB.', end='')