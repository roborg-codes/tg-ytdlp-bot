from posix import listdir
from yt_dlp import YoutubeDL
from typing import List, Dict, Union
from os import path, mkdir, remove

from __init__ import logger


class YTDLPDownloader():
    def __init__(
            self,
            tmp_dir: str = "/tmp/yt_dlp_bot_files",
            ytdlp_params: Dict = {
                'quiet': False,
                # 'paths': '',
                'ignoreerrors': True,
                'writethumbnail': False, # for now, need to convert this image separately
                'keepvideo': False,
                'age_limit': 21,
                # 'postprocessors': None,
                # 'progresshooks': None,
                'logger': logger,
                'geo_bypass': True,
            }
        ) -> None:

        self.tmp_dir: str = tmp_dir
        self.ytdpl_params: Dict = ytdlp_params
        self.ytdpl_params['outtmpl'] = f'{tmp_dir}/%(title)s.%(ext)s'
        if not path.exists(tmp_dir):
            mkdir(tmp_dir)


    def __enter__(self):
        logger.info(f"Entered {__name__} context")
        return self


    def __exit__(self, *args):
        args # suppress pyright warning
        self.clear_downloads()
        logger.info(f"Exited {__name__} context")



    def list_downloads(self) -> List[str]:
        return [path.join(self.tmp_dir, fname) for fname in listdir(self.tmp_dir)]


    def clear_downloads(self) -> None:
        if not path.exists(self.tmp_dir):
            return
        [remove(file) for file in self.list_downloads()]


    def process_entry(self, info: Dict, dest: Dict):
        '''
        Try to predict what characters would get sanitized by ytdlp.
        '''
        fname: str = path.join(
            self.tmp_dir,
            ".".join(
                [
                    info['title'].replace("|", "_").replace("?", "").replace("*", "_").replace("/", "_"),
                    info['ext']
                ]
            )
        )

        performer: str = info['performer'] if 'performer' in info else info['channel']
        duration: int = info['duration']
        title: str = info['title']
        dest[fname] = {
            'duration': duration,
            'performer': performer,
            'title': title
        }

    def download(self, url_list: List[str]) -> Dict:
        with YoutubeDL(self.ytdpl_params) as d:
            # d.download(url_list) implied in following listcomp
            metadata: List = [d.extract_info(url, process=True) for url in url_list]
            downloads: Dict = {}

            # from pprint import PrettyPrinter
            # pp = PrettyPrinter(indent=4)
            # pp.pprint(metadata)

            for info in metadata:
                if info is None: continue # supress pyright warnings/errors

                if '_type' in info and info['_type'] == 'playlist':
                    [self.process_entry(entry_info, dest=downloads) for entry_info in info['entries']]
                    continue
                else:
                    self.process_entry(info, downloads)

            return downloads


    def download_videos(self, url_list: List[str]) -> Dict[str,Union[str,int]]:
        self.ytdpl_params.update(
            {'format': '(mp4,mkv)'}
        )
        return self.download(url_list)


    def download_audios(self, url_list: List[str]) -> Dict[str,Union[str,int]]:
        self.ytdpl_params.update(
            {'format': '(mp3,m4a)'}
        )
        return self.download(url_list)
