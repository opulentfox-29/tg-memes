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


def log_download_video(log_vid: dict[...]) -> None:
    """Анимация скачивания видео."""
    if log_vid['status'] == 'downloading':
        try:
            print(f"\r[download video] {log_vid['_percent_str']} of x ETA {log_vid['_eta_str']}   ", end='')
        except KeyError:
            pass
    if log_vid['status'] == 'finished' and '_elapsed_str' in log_vid:
        print(f"\r[download video] {log_vid['_total_bytes_str']} finished in {log_vid['_elapsed_str']}     ")
    if '_elapsed_str' not in log_vid and log_vid['status'] == 'finished':
        print("[download video] File found in folder")
