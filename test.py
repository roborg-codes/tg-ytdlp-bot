#!/bin/env python

import unittest

from os import path, listdir
from yt_dlp import YoutubeDL

from __init__ import logger
import logging
from downloader import YTDLPDownloader
from typing import Dict


class TestDownloader(unittest.TestCase):
    def test_download(self):
        '''
        Test that the downloader is working correctly.
        '''
        target_urls = ["https://youtu.be/zuuObGsB0No"]
        target_title = "Joy Division - Love Will Tear Us Apart [OFFICIAL MUSIC VIDEO]"
        with YTDLPDownloader() as downloader:
            media = downloader.download(target_urls)
            _key = list(media)[0]

            self.assertIsInstance(media, Dict)
            self.assertTrue(_key.startswith("/tmp/yt_dlp_bot_files"))
            self.assertEqual(media[_key]['title'], target_title)


    def test_cleanup(self):
        '''
        Test creating and removing files in temp dir.
        '''
        default_path = "/tmp/yt_dlp_bot_files/"
        target_urls = ["https://youtu.be/zuuObGsB0No"]
        with YTDLPDownloader() as downloader:
            _ = downloader.download(target_urls)

        self.assertTrue(path.exists(default_path))
        self.assertTrue(path.isdir(default_path))

        with YTDLPDownloader() as downloader:
            downloader.clear_downloads()

        self.assertFalse(listdir(default_path))
        self.assertTrue(path.exists(default_path))
        self.assertTrue(path.isdir(default_path))


    def test_processing(self):
        target_url = "https://youtu.be/zuuObGsB0No"
        target_duration = 210
        target_title = "Joy Division - Love Will Tear Us Apart [OFFICIAL MUSIC VIDEO]"
        target_performer = "Joy Division"
        result = {}
        with YoutubeDL() as d:
            data = d.extract_info(target_url, process=True)
        with YTDLPDownloader() as downloader:
            downloader.process_entry(data, result) # type: ignore

        _fname = list(result)[0]
        self.assertEqual(result[_fname]['duration'], target_duration)   # type: ignore
        self.assertEqual(result[_fname]['title'], target_title)         # type: ignore
        self.assertEqual(result[_fname]['performer'], target_performer) # type: ignore




if __name__ == "__main__":
    logger.setLevel(logging.WARNING)
    unittest.main(verbosity=2)
