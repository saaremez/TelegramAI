import telebot
from utils import search_download_youtube_video
from loguru import logger

from yt_dlp import YoutubeDL


class Bot:

    def __init__(self, token):
        self.bot = telebot.TeleBot(token, threaded=False)
        self.bot.set_update_listener(self._bot_internal_handler)

        self.current_msg = None

    def _bot_internal_handler(self, messages):
        """Bot internal messages handler"""
        for message in messages:
            self.current_msg = message
            self.handle_message(message)

    def start(self):
        """Start polling msgs from users, this function never returns"""
        logger.info(f'{self.__class__.__name__} is up and listening to new messages....')
        logger.info('Telegram Bot information')
        logger.info(self.bot.get_me())

        self.bot.infinity_polling()

    def send_text(self, text):
        self.bot.send_message(self.current_msg.chat.id, text)

    def send_text_with_quote(self, text, message_id):
        self.bot.send_message(self.current_msg.chat.id, text, reply_to_message_id=message_id)

    def is_current_msg_photo(self):
        return self.current_msg.content_type == 'photo'

    def download_user_photo(self, quality=0):
        """
        Downloads photos sent to the Bot to `photos` directory (should be existed)
        :param quality: integer representing the file quality. Allowed values are [0, 1, 2, 3]
        :return:
        """
        if self.current_msg.content_type != 'photo':
            raise RuntimeError(f'Message content of type \'photo\' expected, but got {self.current_msg["content_type"]}')

        file_info = self.bot.get_file(self.current_msg.photo[quality].file_id)
        data = self.bot.download_file(file_info.file_path)

        # TODO save `data` as a photo in `file_info.file_path` path

    def handle_message(self, message):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {message}')
        self.send_text(f'Your original message: {message.text}')


class QuoteBot(Bot):
    pass


class YoutubeBot(Bot):
    def search_download_youtube_video(video_name, num_results=1):
        """
        This function downloads the first num_results search results from Youtube
        :param video_name: string of the video name
        :param num_results: integer representing how many videos to download
        :return: list of paths to your downloaded video files
        """
        results = []
        with YoutubeDL() as ydl:
            videos = ydl.extract_info(f"ytsearch{num_results}:{video_name}", download=True)['entries']

            for video in videos:
                results.append({
                    'filename': ydl.prepare_filename(video),
                    'video_id': video['id'],
                    'title': video['title'],
                    'url': video['webpage_url']
                })

        return results




if __name__ == '__main__':
    with open('.telegramToken') as f:
        _token = f.read()

    my_bot = Bot(_token)
    my_bot.start()
