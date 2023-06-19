# from apscheduler.schedulers.background import BackgroundScheduler
# import os
# os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

from apscheduler.schedulers.blocking import BlockingScheduler
import time
import subprocess
import sys
import json
from upload_to_voidcat_and_return_url import *
import requests
from mp4_to_gif import *
from store_stackjoin import *
from stackjoin_add import *
from send_tweet import *
   
def scrape_and_post():
    with open('hashtag.txt','r') as f:
        hashtag = f.read()
    print('running scrape_and_post. Analyzing last 5 scraped tweets - #'+hashtag)
    scrape = subprocess.run(['snscrape','--jsonl','-n','5','twitter-hashtag', hashtag], capture_output=True, text=True)

    json_from_scraper_output = json.loads("["+scrape.stdout.strip().replace("\n",",")+"]")
    with open('tweets.json','r+') as f:
        stored_json = json.load(f)
        for scraped_tweet in json_from_scraper_output:
            new_tweet = True
            while new_tweet == True:
                for stored_tweet in stored_json:
                    if scraped_tweet["id"] == stored_tweet["id"]:
                        # print('tweet already scraped')
                        new_tweet = False
                if new_tweet == True:
                    print("new tweet found. Tweet id "+str(scraped_tweet["id"]))

                    # running store_stackjoin on scraped tweet
                    if "#stackjoinadd" in scraped_tweet["rawContent"]:
                        # run stackjoinadd
                        json_response_from_stackjoinadd = stackjoin_add(scraped_tweet)
                        store_stackjoin(json_response_from_stackjoinadd[0],json_response_from_stackjoinadd[1],stackjoinadd_reporter=json_response_from_stackjoinadd[2], stackjoinadd_tweet_message=json_response_from_stackjoinadd[3], stackjoin_tweets_or_blocks = "stackjoin_tweets", block_height_or_tweet_id=str(json_response_from_stackjoinadd[0]["id"]), dollar_amount=json_response_from_stackjoinadd[4])
                        dollar_amount = json_response_from_stackjoinadd[4]

                    elif "#stackjoin" in scraped_tweet["rawContent"]:
                        store_stackjoin(scraped_tweet, scraped_tweet["date"][:-6+len(scraped_tweet["date"])])


                    stored_json.append(scraped_tweet)
                    f.seek(0)
                    f.write(json.dumps(stored_json, indent=2))

                    print("tweeting response")
                    print("preparing dollar amount")
                    dollar_amount_for_tweet_text = ""
                    try:
                        dollar_amount = float(dollar_amount.replace("$",""))
                    except:
                        dollar_amount = 0.0
                    if dollar_amount != 0.0 and dollar_amount != "":
                        dollar_amount_for_tweet_text = f"${dollar_amount:.2f} "
                    tweet_message = f"☑️ {dollar_amount_for_tweet_text}Stackjoin Recorded to the Mempool ☑️"
                    # tweepy_send_tweet(tweet_message, scraped_tweet["id"], scraped_tweet)
                    send_tweet(tweet_message, scraped_tweet["id"], scraped_tweet["user"]["username"])

                    new_tweet = False
                # print('exited while loop')
    # switching next check to other hashtag
    if hashtag == "stackjoin":
        with open('hashtag.txt','w') as f:
            f.write("stackjoinadd")
    else:
        with open('hashtag.txt','w') as f:
            f.write("stackjoin")
              
def siggy_scrape():
    with open('tweets.json','w') as f:
        pass

    with open('hashtag.txt','w') as f:
        f.write("stackjoin")
    # if NOSTR_PRIVATE_KEY == "test":
    #     NOSTR_PRIVATE_KEY = PrivateKey.from_nsec("nsec16pejvh2hdkf4rzrpejk93tmvuhaf8pv7eqenevk576492zqy6pfqguu985")

    scrape = subprocess.run(['snscrape','--jsonl','-n','5','twitter-hashtag',"stackjoin"], capture_output=True, text=True)
    json_from_scraper_output = json.loads("["+scrape.stdout.strip().replace("\n",",")+"]")
    scrape = subprocess.run(['snscrape','--jsonl','-n','5','twitter-hashtag',"stackjoinadd"], capture_output=True, text=True)
    json_from_stackjoinadd_scraper_output = json.loads("["+scrape.stdout.strip().replace("\n",",")+"]")
    for tweet in json_from_stackjoinadd_scraper_output:
        json_from_scraper_output.append(tweet)
    # json_from_scraper_output = json.loads("["+scrape.stdout.strip().replace("\n",",")+"]")
    json_from_scraper_output.reverse()
    with open('tweets.json','w') as f:
        f.write(json.dumps(json_from_scraper_output, indent=2))

    # scheduler = BackgroundScheduler()
    scheduler = BlockingScheduler()
    scheduler.add_job(scrape_and_post, 'interval', seconds=30)
    print('\nstarting scheduler')
    scheduler.start()

if __name__ == "__main__":
    subprocess.check_call([sys.executable, "-m", "pip", "install", "git+https://github.com/JustAnotherArchivist/snscrape.git"])
    siggy_scrape()