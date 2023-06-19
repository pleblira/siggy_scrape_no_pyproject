from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
import random
from selenium.webdriver.chrome.options import Options
from dotenv import find_dotenv, load_dotenv
import os

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

def send_tweet(tweet_message, tweet_id_to_reply_to, author_handle):
    twitter_username = os.environ.get("TWITTER_USERNAME")
    twitter_password = os.environ.get("TWITTER_PASSWORD")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    # driver=webdriver.Chrome(options=options)
    driver=webdriver.Firefox()
    driver.get("https://twitter.com/login")

    time.sleep(1)
    print(f'user agent is {driver.execute_script("return navigator.userAgent")}')

    print("username...")
    time.sleep(1)
    username = driver.find_element("xpath",'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input')
    time.sleep(1)
    username.send_keys(twitter_username)
    time.sleep(1)
    username.send_keys(Keys.ENTER)

    print("password...")
    time.sleep(1)
    password = driver.find_element("xpath",'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
    time.sleep(1)
    password.send_keys(twitter_password)
    time.sleep(1)
    password.send_keys(Keys.ENTER)

    print("opening tweet to reply to...")
    time.sleep(1)
    driver.get("https://twitter.com/"+author_handle+"/status/"+str(tweet_id_to_reply_to))
    time.sleep(3)
    reply_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Reply']").click()

    time.sleep(1)
    print("adding text to tweet...")
    tweet = driver.find_element(By.CLASS_NAME,'public-DraftStyleDefault-block')
    actions = ActionChains(driver)
    actions.click(tweet)
    actions.send_keys(tweet_message)
    actions.perform()

    time.sleep(1)
    print("selecting replies...")
    selecting_replies = driver.find_element("xpath",'/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[1]/div/div/div[2]/div/span/span')
    selecting_replies.click()
    # print(tweet_message+" replied to https://twitter.com/"+author_handle+"/status/"+str(tweet_id_to_reply_to))

    time.sleep(1)
    print("removing replies...")
    removing_replies = driver.find_element("xpath",'/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[2]/h2/div[3]/div/label/div/div/input')
    removing_replies.click()
    # print(tweet_message+" replied to https://twitter.com/"+author_handle+"/status/"+str(tweet_id_to_reply_to))

    time.sleep(1)
    print("clicking done after removing replies...")
    clicking_done_after_removing_replies = driver.find_element("xpath",'/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/div[3]/div/div/span/span')
    clicking_done_after_removing_replies.click()
    # print(tweet_message+" replied to https://twitter.com/"+author_handle+"/status/"+str(tweet_id_to_reply_to))

    time.sleep(1)
    print("sending tweet...")
    send_tweet_button = driver.find_element("xpath",'//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/span/span')
    send_tweet_button.click()
    print(tweet_message+" replied to https://twitter.com/"+author_handle+"/status/"+str(tweet_id_to_reply_to))

    time.sleep(2)

# if __name__ == "__main__":
#     send_tweet("selenium test"+str(random.randint(1,1000)),1670571478016839681, "jusabitcoiner")