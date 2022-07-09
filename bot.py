from os import getenv
from os import environ

from dataclasses import dataclass
from enum import Enum, unique
from io import BufferedReader
from string import Template
from typing import Dict, List, Union

from dotenv import load_dotenv
import requests

from __init__ import logger

load_dotenv()
BOT_TOKEN=getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.fatal(f"Bot token not found.")
    logger.fatal(f"Variables in current environment: {environ}")
    exit(1)


@unique
class APIMethod(Enum):
    GET_ME = 'getMe'
    GET_UPDATES = 'getUpdates'
    SEND_AUDIO = 'sendAudio'
    SEND_VIDEO = 'sendVideo'
    SEND_MESSAGE = 'sendMessage'


class Update():
    def __init__(self, update: Dict) -> None:
        self.update_id: int = update['update_id']

        self.chat_id: Union[str,int] = update['message']['chat']['id']

        self.message_id: int = update['message']['message_id']

        self.message: Dict = update['message']

        self.username: str = update['message']['from']['username']

        self.firstname: str = update['message']['from']['first_name']

        self.message_text: str = update['message']['text'] if 'text' in update['message'] else ''

        if 'entities' in update['message']:
            self.entities: List = update['message']['entities']
            self.message_map: Dict[str,List] = Update.map_message(self.message_text, self.entities)
        else:
            self.entities: List = []
            self.message_map: Dict[str,List] = {'':[]}

        logger.info("Update for current constructed")


    @staticmethod
    def map_message(text: str, entities: List[Dict]) -> Dict[str,List]:
        '''
            map_message returns a map of message
        '''
        # EXAMPLE:
        # 'text': '/do_thing https://example.com/'
        # 'entitites': [
        #       {
        #           'offset': 0,
        #           'length': 10,
        #           'type': 'bot_command'
        #       },
        #       {
        #           'offset': 0,
        #           'length': 43,
        #           'type': 'url'
        #       }
        #  ]
        # -> {
        #   'bot_command': ['do_thing'],
        #   'url': ['https://example.com']
        # }
        map: Dict = {}
        for entity in entities:
            ent_type: str = entity['type']
            offset: int = entity['offset']

            # end index for slicing, which is offset + length
            length: int = entity['length'] + offset

            if ent_type in map:
                map[ent_type].append(text[offset:length])
            else:
                map.update({
                    ent_type: [text[offset:length]]
                })

        logger.info("Updade mapped")
        return map


@dataclass
class Payload():

    chat_id: Union[str,int]
    text: str
    caption: Union[str,None] = None
    parse_mode: Union[str,None] = None
    disable_web_page_view: bool = False
    disable_notification: bool = False
    reply_to_message_id: Union[int,None] = None
    allow_sending_without_reply: bool = True

    def construct(self) -> Dict:
        '''
            construct is a method for constructing payloads to send to telegram API.
            This may be useful if you want to reuse and modify the payload without extra calls.
            TODO: reply_markup, entities
        '''
        logger.info("Constructing payload")
        return {
            'chat_id': self.chat_id,
            'text': self.text,
            'disable_web_page_view': self.disable_web_page_view,
            'disable_notification': self.disable_notification,
            'allow_sending_without_reply': self.allow_sending_without_reply,
            'parse_mode': self.parse_mode,
            'reply_to_message_id': self.reply_to_message_id
        }


class Bot():

    polling_delay: int = 5

    def __init__(self, token: str = BOT_TOKEN, api_url: str = "https://api.telegram.org/bot") -> None:
        self.token: str = token
        self.api_url: Template = Template(f"{api_url}" + "${token}/${method}")
        self.offset: int = 0


    def construct_api_request(self, method: APIMethod) -> str:
        return self.api_url.substitute(
            api_url=self.api_url,
            token=self.token,
            method=method.value
    )


    def make_request(self, method: APIMethod, data: Dict, files: Dict={}) -> Dict:
        try:
            return requests.get(
                url=self.construct_api_request(method),
                data=data,
                files=files
            ).json()
        except requests.exceptions.ConnectionError as e:
            logger.error(e)
            data['text'] = "Could not upload file :("
            return requests.get(
                url=self.construct_api_request(APIMethod.SEND_MESSAGE),
                data=data
            ).json()
        except Exception as e:
            logger.error(e)
            return {}


    def ping_home(self) -> bool:
        logger.info(f"Validating API token...")
        r = self.make_request(APIMethod.GET_ME, data={})
        if not r['ok']:
            logger.error(f"Response {r['ok']} {r['error_code']} -- {r['description']}")
            if r['error_code'] == 404:
                logger.error(f"API token probably invalid.")
            return False
        logger.info("Response from server OK.")
        return True


    def get_updates(self) -> List[Update]:
        resp: Dict = self.make_request(
            APIMethod.GET_UPDATES,
            data={'offset': self.offset}
        )
        logger.debug(f"Response is {resp}")
        if resp['ok'] and resp['result']:
            logger.info(f"Updates response OK.")
            updates: List = resp['result']
            self.offset = updates[-1]['update_id'] + 1
            return [Update(update) for update in updates]
        elif not resp['ok'] and resp['error_code'] and resp['description']:
            logger.error(f"Response {resp['error_code']} -- {resp['description']}")
            return self.get_updates()
        else:
            logger.info(f"No results recieved...")
            return []


class TgYtdlBot(Bot):
    def __init__(self, token: str, api_url: str = "https://api.telegram.org/bot") -> None:
        super().__init__(token=token, api_url=api_url)
        if not self.ping_home():
            exit(1)
        logger.info("Bot initialized successfully.")


    def answer_message(self, payload: Dict) -> None:
        self.make_request(APIMethod.SEND_MESSAGE, data=payload)


    def send_file(self, method: APIMethod, payload: Dict, file: BufferedReader, metadata: Dict) -> None:
        if method == APIMethod.SEND_AUDIO:
            file_type: str = 'audio'
        elif method == APIMethod.SEND_VIDEO:
            file_type: str = 'video'
        else:
            return

        payload['title'] = metadata['title']
        payload['duration'] = metadata['duration']
        payload['performer'] = metadata['performer']
        logger.info(f"Payload ready: {payload}. Sending {file_type}...")

        self.make_request(
            method,
            data=payload,
            files={file_type: file.read()}
        )
