from typing import List, Dict, AnyStr
import logging
import re
import hashlib

import datetime
import json

from mastoBot.configManager import ConfigAccessor
from mastoBot.mastoBot import MastoBot, handleMastodonExceptions
from redis.commands.json.path import Path

class MyBot(MastoBot):
    @handleMastodonExceptions
    def processMention(self, mention: Dict):
        pass
    
    @handleMastodonExceptions
    def processReblog(self, reblog: Dict):
        pass
    
    @handleMastodonExceptions
    def processFavourite(self, favourite: Dict):
        pass 
    
    @handleMastodonExceptions
    def processFollow(self, follow: Dict):
        pass 
    
    @handleMastodonExceptions
    def processPoll(self, poll: Dict):
        pass
    
    @handleMastodonExceptions
    def processFollowRequest(self, follow_request: Dict):
        pass
    
    @handleMastodonExceptions
    def processUpdate(self, update: Dict) -> None:
        pass
    
    def localStoreMerge(self, key: str, id: str, new_data: Dict):
        current = self.r.json().get(f"{key}:{id}") or {}
        current.update(new_data)
        self.r.json().set(f"{key}:{id}", Path.root_path(), current, decode_keys=True)

def toSerializableDict(data: Dict) -> Dict:
    json_data = json.dumps(data, default=serialize_datetime)
    new_data = json.loads(json_data)
    return new_data

def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

if __name__ == "__main__":
    config = ConfigAccessor("config.yml")
    credentials = ConfigAccessor("credentials.yml")
    
    bot = MyBot(credentials=credentials, config=config)
    bot_id = bot.getMe().get('id')
    
    followers = []
    result = bot._api.account_followers(bot_id)
    
    while result:
        followers.extend(result)
        result = bot._api.fetch_next(result)
    
    for follower in followers:
        new_data = toSerializableDict(follower)
        
        new_data.setdefault("banned", False)
        
        bot.localStoreMerge("user", follower.get('id'), new_data)