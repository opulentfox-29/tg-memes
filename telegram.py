import time

import youtube_dl
import telebot
from telebot.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument

import logger as log
from exceptions import *
from extractors import extractor_url, extractor_info


class TG:
    def __init__(self, token, chat_id, text, link_post, media_urls):
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id
        self.text = text
        self.link_post = link_post
        self.media_urls = media_urls
        self.err_text = ''
    
    def send_post(self) -> None:
        """Отправка поста в тг."""
        self._media_to_bin()
        num_try = 0
        
        while num_try <= 3:
            num_try += 1
            self._create_media_group()
            media = self.media_group
            text = self.text
            if self.err_text:
                text = f"{self.err_text}{text}\n\n{self.link_post}"
            
            try:
                if media:
                    self.bot.send_media_group(self.chat_id, media)
                else:
                    self.bot.send_message(self.chat_id, text)
                log.log("send message")
                self._media_close()
                return
            except telebot.apihelper.ApiTelegramException as err:
                err = str(err)
                if 'Error code: 429' in err:
                    self._err429(err)
                    continue
                elif 'Entity Too Large' in err:
                    self._err413()
                    break
                elif 'MEDIA_CAPTION_TOO_LONG' in err:
                    self._err_caption_too_long()
                    break
                else:
                    log.error("[TG ERROR SEND] " + str(err))
                    time.sleep(3)
        
        self._media_close()
        try:
            text = "FAILED SEND POST\n" + text + f"\n\n{self.link_post}"
            self.bot.send_message(self.chat_id, text)
        except Exception as err:
            log.error("[TG ERROR TEXT SEND] " + str(err))
            self.bot.send_message(self.chat_id, f"FAILED SEND TEXT POST\n{str(err)}\n\n{self.link_post}")

    def _create_media_group(self) -> None:
        text = self.text
        first_media = True
        media_group = []
        opened_media = []
        media_bytes_dict = self.media_bytes_dict
        
        for media_bytes in media_bytes_dict:
            if media_bytes_dict[media_bytes] == 'photo':
                self._append_media_photo(media_group, media_bytes, first_media, text)
                first_media = False
            elif media_bytes_dict[media_bytes] == 'gif':
                self._append_media_gif(media_group, media_bytes, first_media, text)
                first_media = False
            else:
                video_num = media_bytes_dict[media_bytes]
                try:
                    media_file = open(f'data/temp/vid{video_num}.mp4', 'rb')
                    opened_media.append(media_file)
                    self._append_media_video(media_group, media_file, first_media, text, video_num)
                except Exception:
                    pass
                first_media = False

        self.opened_media = opened_media
        self.media_group = media_group
        
    def _media_to_bin(self) -> None:
        """Получение бинарного медия."""
        media_contents = self.media_urls
        video_num = 0
        media_bytes_dict = {}
        for media_content in media_contents:
            if media_contents[media_content] == 'photo':
                media_bytes_dict[media_content] = media_contents[media_content]
            elif media_contents[media_content] == 'gif':
                media_bytes_dict[media_content] = media_contents[media_content]
            elif media_contents[media_content] == 'video':
                extract_url = extractor_url(media_content)
                if not extract_url:
                    extract_url = media_content
                video_num += 1
                self._download_videos(extract_url, video_num)
                media_bytes_dict[media_content] = video_num
            else:
                print(media_content, media_contents[media_content])
                log.error(f"[ERROR] - не видео и не фото {self.link_post}")
                self.err_text = f"{self.err_text} не видео и не фото\n"
        self.media_bytes_dict = media_bytes_dict
        
    def _append_media_photo(self, media_group: list[telebot, ...], photo: bin,
                            first_media: bool, text: str) -> None:
        """Добавление фото к медиа группе."""
        if first_media:
            media_group.append(InputMediaPhoto(photo, caption=text))
        else:
            media_group.append(InputMediaPhoto(photo))

    def _append_media_gif(self, media_group: list[telebot, ...], gif: bin,
                          first_media: bool, text: str) -> None:
        """Добавление гифки к медиа группе."""
        if first_media:
            media_group.append(InputMediaDocument(gif, caption=text))
        else:
            media_group.append(InputMediaDocument(gif))

    def _append_media_video(self, media_group: list[telebot, ...], video_file: bin,
                            first_media: bool, text: str, video_num: int) -> None:
        """Добавление видео к медиа группе."""
        extract_info = extractor_info(f'data/temp/vid{video_num}.mp4')
        if first_media:
            media_group.append(
                InputMediaVideo(
                    video_file,
                    supports_streaming=True,
                    duration=extract_info['duration'],
                    width=extract_info['width'],
                    height=extract_info['height'],
                    caption=text
                )
            )
        else: 
            media_group.append(
                InputMediaVideo(
                    video_file,
                    supports_streaming=True,
                    duration=extract_info['duration'],
                    width=extract_info['width'],
                    height=extract_info['height']
                )
            )
        
    def _download_videos(self, extract_url: str, video_num: int) -> None:
        """Скачивание видео."""
        ydl_opts = {
            'outtmpl': f'data/temp/vid{video_num}.mp4', 
            'max-filesize': '47MiB',
            "quiet": True,  # выключить встроенные логи
            "progress_hooks": [log.log_download_video]  # свои логи
        }
        
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(extract_url, download=True)
                
        except YtdlTotalBytesException as ex:
            self.err_text = f"{self.err_text}YtdlTotalBytesException {ex}\n"
        except KeyboardInterrupt as ex:
            self.err_text = f"{self.err_text}SKIP DOWNLOAD VIDEO\n"
            log.warning(f"SKIP DOWNLOAD VIDEO {ex}")
        except Exception as ex:
            self.err_text = f"{self.err_text}{ex}\n"
            log.error(f"FAILED DOWNLOAD VIDEO {ex}")
        
    def _media_close(self) -> None:
        """Закрывает медиа файлы."""
        for media_file in self.opened_media:
            media_file.close()
        
    def _err429(self, err: str) -> None:
        """Error code 429, Error: Too many requests: retry after."""
        retry_after = int(str(err).split()[-1])
        log.warning(f"[TG SEND] Слишком много запросов. Подождите {retry_after} секунд(ы).")
        time.sleep(retry_after)
        
    def _err413(self) -> None:
        """Error code: 413. Description: Request Entity Too Large"""
        log.warning(f"[TG SEND] Слишком большая медиа.")
        
    def _err_caption_too_long(self) -> None:
        """Error code: 400. Description: Bad Request: MEDIA_CAPTION_TOO_LONG"""
        log.warning(f"[TG SEND] Слишком много текста.")
