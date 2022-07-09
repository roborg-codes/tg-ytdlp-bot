#!/bin/env python3

import os
from posix import listdir
from sys import exit
from time import sleep
from typing import Dict, List

from dotenv import load_dotenv

from __init__ import logger
from bot import APIMethod, Bot, Payload, TgYtdlBot, Update
from downloader import YTDLPDownloader


load_dotenv()
BOT_TOKEN=os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.fatal(f"Bot token not found.")
    exit(1)
AUTHORIZED_USER=os.getenv('AUTHORIZED_USER')
if not AUTHORIZED_USER:
    logger.fatal(f"No authorized user found.")
    exit(1)


def process_request(bot: TgYtdlBot, method: APIMethod, payload: Payload, url_list: List[str]):
    with YTDLPDownloader() as dler:
        downloads: Dict = dler.download_audios(url_list)
        logger.info("Download complete.")
        for item, metadata in downloads.items():
            # if not isinstance(metadata, Dict): return
            logger.info(f"Processing {item} with {metadata=}")
            if not os.path.exists(item):
                # TODO:
                # ytdlp sanitizer is crazy and tries too hard to change filenames
                # need to figure out how to match downloaded files!
                logger.fatal(f"{item} item does not exist.")
                raise IOError(
                    f"Last contents of tmp dir: {listdir('/tmp/yt_dlp_bot_files')}"
                )

            with open(item, 'rb') as file:
                bot.send_file(
                    method,
                    payload=payload.construct(),
                    file=file,
                    metadata=metadata # type: ignore
                )
            logger.info(f"File {os.path.basename(item)} sent.")


def run_bot(bot: TgYtdlBot) -> None:
    logger.info("Polling updates...")
    updates: List[Update] = bot.get_updates()
    if not updates:
        logger.info("No updates recieved...")
        return

    logger.info("Processing updates")
    for update in updates:
        if update.username != AUTHORIZED_USER:
            continue
        if 'url' not in update.message_map:
            continue

        payload: Payload = Payload(
            chat_id=update.chat_id,
            text='',
            reply_to_message_id=update.message_id
        )
        urls: List[str] = update.message_map['url']

        logger.info(f"Downloading {urls}...")
        process_request(
            bot,
            method=APIMethod.SEND_AUDIO,
            payload=payload,
            url_list=urls
        )


def main() -> None:
    bot: Bot = TgYtdlBot(BOT_TOKEN)
    while True:
        try:
            run_bot(bot)
        except Exception as e:
            logger.error(e)
        finally:
            logger.info(f"Sleeping for {bot.polling_delay}s")
            sleep(bot.polling_delay)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print(e)
        exit(0)
