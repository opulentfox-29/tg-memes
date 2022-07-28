import time

import telebot
from telebot.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument

import logger as log


class TG:
    def __init__(self, token, chat_id, vk):
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id
        self.text = vk.post_text
        self.link_post = vk.link_post
        self.media_bytes_dict = vk.media_bytes_dict
        self.err_text = vk.err_text
    
    def send_post(self) -> None:
        """Отправка поста в тг."""
        text = self.text
        if self.err_text:
            text = f"{self.err_text}{text}\n{self.link_post}"

        num_try = 0
        while num_try < 3:
            num_try += 1
            self._create_media_group()
            media = self.media_group
            
            try:
                if media:
                    self.bot.send_media_group(self.chat_id, media)
                else:
                    self.bot.send_message(self.chat_id, text)
                log.log("send message")
                return
            except telebot.apihelper.ApiTelegramException as err:
                err = str(err)
                if 'Error code: 429' in err:
                    self._err429_retry_after(err)
                elif 'Entity Too Large' in err:
                    self._err413_media_too_large()
                    break
                elif 'MEDIA_CAPTION_TOO_LONG' in err:
                    self._err_caption_too_long()
                    text = f"[TG ERROR] СЛИШКОМ МНОГО ТЕКСТА\n" + text + f"\n\n{self.link_post}"
                    break
                else:
                    log.error("[TG ERROR SEND] " + str(err))
                    text = f"FAILED SEND POST ({err})\n" + text + f"\n\n{self.link_post}"
                    time.sleep(3)

        try:
            self.bot.send_message(self.chat_id, text)
            log.log("send message")
        except Exception as err:
            log.error("[TG ERROR TEXT SEND] " + str(err))
            self.bot.send_message(self.chat_id, f"FAILED SEND TEXT POST\n{str(err)}\n\n{self.link_post}")

    def _create_media_group(self) -> None:
        text = self.text
        first_media = True
        media_group = []
        media_bytes_dict = self.media_bytes_dict
        
        for media_bytes in media_bytes_dict:
            if media_bytes_dict[media_bytes]['type'] == 'photo':
                self._append_media_photo(media_group, media_bytes, first_media, text)
            elif media_bytes_dict[media_bytes]['type'] == 'gif':
                self._append_media_gif(media_group, media_bytes, first_media, text)
            elif media_bytes_dict[media_bytes]['type'] == 'video':
                self._append_media_video(media_group, media_bytes, first_media,
                                         text, media_bytes_dict[media_bytes]['data'])
            first_media = False

        self.media_group = media_group

    def _append_media_photo(self, media_group: list[telebot, ...], photo: bin,
                            first_media: bool, text: str) -> None:
        """Добавление фото к медиа группе."""
        if not first_media:
            text = None
        media_group.append(InputMediaPhoto(photo, caption=text))

    def _append_media_gif(self, media_group: list[telebot, ...], gif: bin,
                          first_media: bool, text: str) -> None:
        """Добавление гифки к медиа группе."""
        if not first_media:
            text = None
        media_group.append(InputMediaDocument(gif, caption=text))

    def _append_media_video(self, media_group: list[telebot, ...], video_file: bin,
                            first_media: bool, text: str, extract_info) -> None:
        """Добавление видео к медиа группе."""
        if not first_media:
            text = None

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
        
    def _err429_retry_after(self, err: str) -> None:
        """Error code 429, Error: Too many requests: retry after."""
        retry_after = int(str(err).split()[-1])
        log.warning(f"[TG SEND] Слишком много запросов. Подождите {retry_after} секунд(ы).")
        time.sleep(retry_after)
        
    def _err413_media_too_large(self) -> None:
        """Error code: 413. Description: Request Entity Too Large"""
        log.warning(f"[TG SEND] Слишком большая медиа.")
        
    def _err_caption_too_long(self) -> None:
        """Error code: 400. Description: Bad Request: MEDIA_CAPTION_TOO_LONG"""
        log.warning(f"[TG SEND] Слишком много текста.")
