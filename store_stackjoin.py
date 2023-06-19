# import json
# import io
# from get_tweet_gif_url import *
# from jinja2 import Template
# import boto3
# from tvdl.tvdl_launcher import twitter_video_dl_launcher
import requests
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from pyairtable import Table
import os
from remove_mentions_from_tweet_message import *
from mp4_to_gif import *
from upload_to_voidcat_and_return_url import *

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BEARER_TOKEN = os.environ.get("AIRTABLE_BEARER_TOKEN")

def store_stackjoin(scraped_tweet, tweet_datetimeISO, stackjoinadd_reporter = "0", stackjoinadd_tweet_message = "", block_height_or_tweet_id="", stackjoin_tweets_or_blocks = "stackjoin_tweets", dollar_amount=""):
    print("running store_stackjoin function")
    tweet_id = str(scraped_tweet["id"])
    author_id = str(scraped_tweet["user"]["id"])
    # removing mentions from tweet message
    tweet_message = remove_mentions_from_tweet_message(scraped_tweet["rawContent"])

    if tweet_datetimeISO == None:
        tweet_datetimeISO = datetime.utcnow().isoformat()
        tweet_datetimeISO = tweet_datetimeISO[0:tweet_datetimeISO.find(".")]
        tweet_timestamp = str(f"{datetime.timestamp(datetime.now().replace(microsecond=0)):.0f}")
    else:
        tweet_timestamp = datetime.strptime(tweet_datetimeISO,'%Y-%m-%dT%H:%M:%S')
        tweet_timestamp = int(datetime.timestamp(tweet_timestamp))
    author_handle = scraped_tweet["user"]["username"]
    print(f"the author handle is {author_handle}")
    image_url_dict = []
    img_src_dict = []
    airtable_image_files_dict = []
    airtable_gif_files_dict = []

    if scraped_tweet["media"] != None:
        print("has image")
        for index, media_file in enumerate(scraped_tweet["media"]):
            if media_file["_type"] == "snscrape.modules.twitter.Photo":
                filetype = media_file["fullUrl"]
                filetype = filetype[filetype.find("?format=")+8:]
                filetype = filetype[:filetype.find("&")]

                # downloaded_media = requests.get(media_file["fullUrl"])
                image_url = media_file["fullUrl"]
                image_preview_url = media_file["fullUrl"]

            elif media_file["_type"] == "snscrape.modules.twitter.Gif":
                filetype = media_file["variants"][0]["url"]
                filetype = filetype[filetype.rfind(".")+1:]

                downloaded_media = requests.get(media_file["variants"][0]["url"])

                with open("temp."+filetype,'wb') as temp_media_file:
                    temp_media_file.write(downloaded_media.content)

                mp4_to_gif("temp.mp4", "temp.gif")
                filetype = "gif"
                
                # downloaded_media = requests.get(media_file["variants"][0]["url"])
                image_url = upload_to_voidcat_and_return_url("temp."+filetype, filetype)
                image_preview_url = media_file["thumbnailUrl"]

            elif media_file["_type"] == "snscrape.modules.twitter.Video":
                temporary_variant_list = media_file["variants"]
                for index, variant in enumerate(temporary_variant_list):
                    if variant["bitrate"] == None:
                        temporary_variant_list.pop(index)
                temporary_variant_list = sorted(temporary_variant_list, key=lambda d: d['bitrate'], reverse=True)

                filetype = temporary_variant_list[0]["url"]
                filetype = filetype[:filetype.find("?tag=")]
                filetype = filetype[filetype.rfind(".")+1:]

                # downloaded_media = requests.get(temporary_variant_list[0]["url"])
                image_url = temporary_variant_list[0]["url"]
                image_preview_url = media_file["thumbnailUrl"]

            # trying to skip the s3 process altogether
            #saving tweet images to s3
            # if item['type'] == "animated_gif":
            #     filename = str(index+1)+"_gif"
            # else:
            #     filename = str(index+1)+"_image"
            # image_filetype = image_url.rsplit('/', 1)[1].rsplit('.', 1)[1]
            # image_preview_filetype = image_preview_url.rsplit('/', 1)[1].rsplit('.', 1)[1]
            # s3_upload = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            # s3_image_path = 'stackjoin_tweet_images/'+tweet_id+"/"+filename+"."+image_filetype
            # s3_image_preview_path = 'stackjoin_tweet_images/'+tweet_id+"/"+filename+"_thumbnail."+image_preview_filetype
            
            # uploading stackjoin image previews to S3 bucket
            # print(f"the image preview URL is {image_preview_url}")
            # r = requests.get(image_preview_url, allow_redirects=True)
            # s3_upload.Object('pleblira',s3_image_preview_path).put(Body=io.BytesIO(r.content), ACL="public-read",ContentType='image/jpeg')

            # uploading stackjoin images to S3 bucket
            # print(f"the image URL is {image_url}")
            # r = requests.get(image_url, allow_redirects=True)
            # s3_upload.Object('pleblira',s3_image_path).put(Body=io.BytesIO(r.content), ACL="public-read",ContentType='image/jpeg')

            # uploading downloaded video to S3
            # if item['type'] == "video":
            #     with open(video_path, 'rb') as f:
            #         print('uploading to s3')
            #         s3_upload = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            #         s3_upload.Object('pleblira',video_path).put(Body=f,ACL="public-read")

            # append to image_files_dict for later creating row on Airtable
            filename = str(index+1)+filetype
            # appending all files to the same image column
            # if media_file["_type"] == "snscrape.modules.twitter.Gif":
            #     airtable_gif_files_dict.append({"url":image_url,'filename':filename+"."+filetype})
            # else:
            airtable_image_files_dict.append({"url":image_url,'filename':filename+"."+filetype})
            # if video_path != "":
            #     airtable_gif_files_dict.append({"url":"https://pleblira.s3.amazonaws.com/"+video_path,'filename':video_filename_and_filetype})
       
            # appending url and html tag for embedding to dictionaries which will then be added to the json on S3 and to the html table
            image_url_dict.append(image_url)
            img_src_dict.append(f"<a href=\"/{image_url}\" target=\"_blank\"><img src=\"/{image_preview_url}\" style=\"max-width:100px;\"></a>")
            # print(f"the image_url_dict is: {image_url_dict}")

            # appending url and html tag for video files (new implementation)
            # if item['type'] == "video":
            #     image_url_dict.append(video_path)
            #     img_src_dict.append(f"<a href=\"/{video_path}\" target=\"_blank\"><img src=\"/{s3_image_preview_path}\" style=\"max-width:100px;\"></a>")
                # print(f"the image_url_dict is: {image_url_dict}")
    else:
        print("no image")
    
    # defining airtable_API_import_notes string
    airtable_API_import_notes = ""
    # if " [*Tweet has video attached (videos are unretrievable via API). Open original tweet to access video.]" in tweet_message:
    #     airtable_API_import_notes = "[*Tweet has video attached (videos are unretrievable via API). Open original tweet to access video.]"
    if stackjoinadd_reporter != "0":
        airtable_API_import_notes += stackjoinadd_reporter
    if stackjoinadd_tweet_message != "":
        airtable_API_import_notes += stackjoinadd_tweet_message
    # tweet_message_for_airtable_API = tweet_message.replace(" [*Tweet has video attached (videos are unretrievable via API). Open original tweet to access video.]","")

    # creating row or updating row on Airtable
    table = Table(AIRTABLE_API_KEY, "appiNbM9r6Zy7G2ux", stackjoin_tweets_or_blocks)
    if stackjoin_tweets_or_blocks == "blocks":
        stackjoin_tweets_or_blocks = "tblcwUsNLE3AecXpu"
        stackjoin_tweets_or_blocks_filter_term = "block_height"
    else:
        stackjoin_tweets_or_blocks = "tblAHtdeESADDCKGA"
        stackjoin_tweets_or_blocks_filter_term = "tweet_id"
    url = "https://api.airtable.com/v0/appiNbM9r6Zy7G2ux/"+stackjoin_tweets_or_blocks
    if block_height_or_tweet_id == "":
        block_height_or_tweet_id = 21000000
    headers = {"Authorization": "Bearer "+AIRTABLE_BEARER_TOKEN}
    x = requests.get(url, headers=headers, params={'fields[]':[stackjoin_tweets_or_blocks_filter_term], 'filterByFormula':stackjoin_tweets_or_blocks_filter_term+"="+str(block_height_or_tweet_id)}).json()
    # print(json.dumps(x,indent=4))
    print(x)
    if x['records'] == []:
        create_or_update = "create"
    else:
        create_or_update = "update"
        record_id = x['records'][0]['id']

    # checking if block
    if stackjoin_tweets_or_blocks == "tblcwUsNLE3AecXpu": 
        # merge airtable_gif_files_dict into airtable_image_files_dict
        for item in airtable_gif_files_dict:
            airtable_image_files_dict.append(item)
        # checking if valid block height was added to tweet
        try:
            block_height_or_tweet_id = int(block_height_or_tweet_id.replace("$",""))
        except:
            block_height_or_tweet_id = 21000000
        if create_or_update == "create":
            print('creating')
            table.create({
                "block_height": block_height_or_tweet_id,
                "tweet_id": tweet_id,
                "author_handle": author_handle,
                "author_id": author_id,
                "importing_full_block_message": tweet_message,
                "block_summary_image": airtable_image_files_dict,
                "image_url_dict": str(image_url_dict).translate({39: None,91: None, 93: None, 44: None}),
                "block_timestamp": int(tweet_timestamp),
                "block_datetimeISO": tweet_datetimeISO,
                "img_src_dict": str(img_src_dict).translate({39: None,91: None, 93: None, 44: None}),
                "airtable_API_import_notes": airtable_API_import_notes.strip()
                })
        # if updating: 
        elif create_or_update == "update":
            print('updating')
            table = Table(AIRTABLE_API_KEY, 'appiNbM9r6Zy7G2ux', "blocks")
            Table.update(table, record_id=record_id,fields={
                "tweet_id": tweet_id,
                "author_handle": author_handle,
                "author_id": author_id,
                "importing_full_block_message": tweet_message,
                "block_summary_image": airtable_image_files_dict,
                "image_url_dict": str(image_url_dict).translate({39: None,91: None, 93: None, 44: None}),
                "block_timestamp": int(tweet_timestamp),
                "block_datetimeISO": tweet_datetimeISO,
                "img_src_dict": str(img_src_dict).translate({39: None,91: None, 93: None, 44: None}),
                "airtable_API_import_notes": airtable_API_import_notes.strip()
                })
            
    # for stackjoins
    else:
        try:
            dollar_amount = float(dollar_amount.replace("$",""))
            stackjoinadd_reporters = ["AnthonyDessauer", "__overflow_", "jc4466", "LoKoBTC", "BrokenSystem20", "pleblira", "phathodl", "derekmross", "VStackSats"]
            if stackjoinadd_reporter[25:25+stackjoinadd_reporter[25:].find(" ")] not in stackjoinadd_reporters:
                print("stackjoin reporter not found in list")
                dollar_amount = 0.0
        except:
            dollar_amount = 0.0
        
        if create_or_update == "create":
            print('creating')
            table.create({
                "tweet_id": tweet_id,
                "dollar_amount": dollar_amount,
                "author_handle": author_handle,
                "author_id": author_id,
                "tweet_message": tweet_message,
                "image_files": airtable_image_files_dict,
                "gif_files": airtable_gif_files_dict,
                "image_url_dict": str(image_url_dict).translate({39: None,91: None, 93: None, 44: None}),
                "tweet_timestamp": int(tweet_timestamp),
                "tweet_datetimeISO": tweet_datetimeISO,
                "img_src_dict": str(img_src_dict).translate({39: None,91: None, 93: None, 44: None}),
                "airtable_API_import_notes": airtable_API_import_notes.strip()
                })        # if updating: 
        elif create_or_update == "update":
            print('updating')
            table = Table(AIRTABLE_API_KEY, 'appiNbM9r6Zy7G2ux', "stackjoin_tweets")
            Table.update(table, record_id=record_id,fields={
                "tweet_id": tweet_id,
                "dollar_amount": dollar_amount,
                "author_handle": author_handle,
                "author_id": author_id,
                "tweet_message": tweet_message,
                "image_files": airtable_image_files_dict,
                "gif_files": airtable_gif_files_dict,
                "image_url_dict": str(image_url_dict).translate({39: None,91: None, 93: None, 44: None}),
                "tweet_timestamp": int(tweet_timestamp),
                "tweet_datetimeISO": tweet_datetimeISO,
                "img_src_dict": str(img_src_dict).translate({39: None,91: None, 93: None, 44: None}),
                "airtable_API_import_notes": airtable_API_import_notes.strip()
                })

    if stackjoinadd_reporter != "0":
        tweet_message += stackjoinadd_reporter

    #downloading stackjoin_tweets.json from s3 to append tweet information
    # boto3.client('s3').download_file('pleblira', 'stackjoin_tweets/stackjoin_tweets.json', 'stackjoin_tweets/stackjoin_tweets.json')

    # with open("stackjoin_tweets/stackjoin_tweets.json",'r+') as openfile:
    #     try:
    #         stackjoin_tweets = json.load(openfile)
    #         print("try")
    #     except:
    #         print("except")
    #         stackjoin_tweets = []
    #     stackjoin_tweets.append({"tweet_id":tweet_id,"author_handle":author_handle,"author_id":author_id,"tweet_message":tweet_message,"image_url_dict":image_url_dict,"img_src_dict":img_src_dict,"tweet_timestamp":tweet_timestamp,"tweet_datetimeISO":tweet_datetimeISO})
    #     openfile.seek(0)
    #     openfile.write(json.dumps(stackjoin_tweets, indent=4))

    # uploading appended json to s3
    # s3_upload = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    # content=json.dumps(stackjoin_tweets).encode('utf-8')
    # s3_upload.Object('pleblira', 'stackjoin_tweets/stackjoin_tweets.json').put(Body=content,ACL="public-read")

    # turning stackjoin_tweets into html table data
    # stackjoin_tweets_table_data = ""
    # for index, tweet in enumerate(stackjoin_tweets):
    #     if tweet['image_url_dict'] == []:
    #         tweet['image_url_dict'] = "no image"
    #     if tweet['img_src_dict'] == []:
    #         tweet['img_src_dict'] = "no image"
    #     if int(datetime.fromtimestamp(int(tweet['tweet_timestamp'])).strftime("%j")) % 2 >0:
    #         html_row_class = "row-odd-day"
    #     else:
    #         html_row_class = "row-even-day"
    #     stackjoin_tweets_table_data += (f"<tr class=\"{html_row_class}\"><td>{index+1}</td><td><a href=\"https://www.twitter.com/pleblira/status/{tweet['tweet_id']}\" target=\"_blank\">{tweet['tweet_id']}</a></td><td><a href=\"https://twitter.com/{tweet['author_handle']}\" target=\"_blank\">{tweet['author_handle']}</a><br>({tweet['author_id']})</td><td>{tweet['tweet_message']}</td><td>{str(tweet['img_src_dict']).translate({39: None,91: None, 93: None, 44: None})}</td><td style=\"word-break:break-all\">{str(tweet['image_url_dict'])}</td><td>{tweet['tweet_datetimeISO']} <br>({tweet['tweet_timestamp']})</td>")
    # print(stackjoin_tweets_table_data)
    # with open("stackjoin_tweets/stackjoin_tweets_table_data.html",'w') as openfile:
    #     openfile.write(stackjoin_tweets_table_data)

    # updating html template with table data
    # with open('stackjoin_tweets/stackjoin_tweets_template.html') as openfile:
    #     t = Template(openfile.read())
    #     vals = {"stackjoin_tweets_table_data": stackjoin_tweets_table_data}
    # with open('stackjoin_tweets/stackjoin_tweets.html','w') as f:
    #     f.write(t.render(vals))

    # uploading template to s3
    # content=t.render(vals)
    # s3_upload.Object('pleblira', 'stackjoin_tweets/stackjoin_tweets.html').put(Body=content,ACL="public-read",ContentType='text/html')



# if __name__ == "__main__":
#     store_stackjoin("scraped_tweet_with_image.json")




