import requests
import os
import json
import webbrowser
from datetime import datetime
from remove_mentions_from_tweet_message import *
import subprocess

def stackjoin_add(scraped_tweet):
    json_response_from_reply = scraped_tweet
    stackjoinadd_reporter = " [stackjoinadd_reporter: "+json_response_from_reply["user"]["username"]+" - ID "+str(json_response_from_reply["user"]["id"])
    cleaned_up_stackjoinadd_tweet_message = remove_mentions_from_tweet_message(json_response_from_reply["rawContent"])
    stackjoinadd_tweet_message = " - message: "+cleaned_up_stackjoinadd_tweet_message + "]"
    tweet_id_to_stackjoinadd = str(json_response_from_reply["inReplyToTweetId"])

    # extracting dollar_amount
    print('extracting dollar amount')
    dollar_amount = cleaned_up_stackjoinadd_tweet_message[cleaned_up_stackjoinadd_tweet_message.find("#stackjoinadd ")+14:]
    space_character_list = ["\n","\t"," "," "]
    space_character_positions = []
    for space_character in space_character_list:
        if dollar_amount.find(space_character) == -1:
            space_character_positions.append({"space_character":space_character,'position':100})
        else:
            space_character_positions.append({"space_character":space_character,'position':dollar_amount.find(space_character)})
    space_character_positions = sorted(space_character_positions, key=lambda d: d['position'])
    space_character = space_character_positions[0]["space_character"]

    if space_character_positions[0]["position"] != 100:
        dollar_amount = dollar_amount[:dollar_amount.find(space_character)]
    print(f"the dollar_amount is {dollar_amount}")

    scrape = subprocess.run(['snscrape','--jsonl','twitter-tweet', tweet_id_to_stackjoinadd], capture_output=True, text=True)
    json_response_from_tweet_to_stackjoinadd = json.loads("["+scrape.stdout.strip().replace("\n",",")+"]")
    # print(f"json_response_from_tweet_to_stackjoinadd is {json.dumps(json_response_from_tweet_to_stackjoinadd, indent=2)}")
    tweet_datetimeISO = json_response_from_tweet_to_stackjoinadd[0]["date"][:-6+len(scraped_tweet["date"])]
    
    return json_response_from_tweet_to_stackjoinadd[0], tweet_datetimeISO, stackjoinadd_reporter, stackjoinadd_tweet_message, dollar_amount
