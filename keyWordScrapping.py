import datetime
import random
import time
import json
import pandas as pd
import pickle
import brotli
import base64
import pytz
from dateConversionUtils import *
import config
import numpy as np
import re
from bs4 import BeautifulSoup
import os
import pdb


global driver, proxy,server,f2

monthDict = {'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 'may': 'May', 'jun': 'Jun', 'jul': 'Jul',
             'ago': 'Aug',
             'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'}


def format_date_col2(date):
    try:
        fmt = '%Y-%m-%d %H:%M:%S'
        dt = datetime.datetime.fromtimestamp(int(date))
        dt = dt.astimezone(pytz.utc)
        dt = dt.replace(tzinfo=pytz.utc)
        dt = dt.strftime(fmt)

    except Exception as e:
        print("Exception format_date_col:", e)
        dt = date

    return dt

def format_date_col(date,correct_date):
    if correct_date==False:
        try:
            fmt = "%d %b %Y"
            dt = datetime.datetime.strptime(date,fmt)
            dt = dt.astimezone(pytz.utc)
            dt = dt.replace(tzinfo=pytz.utc)
            #dt = dt.strftime(fmt)

        except Exception as e:
            print("Exception format_date_col:", e)
            dt = date

        return dt


def startBrowser():
    global driver, proxy,server

    from browsermobproxy import Server
    dict = {'port': 8090}
    server = Server('browsermob-proxy-2.1.4-bin/browsermob-proxy-2.1.4/bin/browsermob-proxy', options=dict)
    server.start()
    proxy = server.create_proxy()

    from selenium import webdriver
    # Configure the browser proxy in chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--blink-settings=imagesEnabled=false')

    driver = webdriver.Chrome('chromedriver_linux64/chromedriver', options=chrome_options)

    driver.get("https://www.facebook.com/VuseVaporUS/")
    time.sleep(3)
    username = driver.find_element_by_id("email")
    password = driver.find_element_by_id("pass")
    submit = driver.find_element_by_id("loginbutton")

    username.send_keys("sebas24680@hotmail.com")
    password.send_keys("chafaso2358")

    submit.click()
    time.sleep(30)



def FIX_DATE(myDate,correct_date):
    if correct_date==False:

        myDate=myDate.lower()
        myDate = myDate.replace('.', '').replace(' de ', ' ').replace(' of ', ' ')

        if (len(myDate.split(' ')) < 3):
            myDate = myDate + ' ' + str(datetime.datetime.now().year)
        for m in monthDict:
            if (myDate.find(m) > -1):
                myDate = myDate.replace(m, monthDict.get(m))

        else:
            if((myDate.find('h')>-1) or (myDate.find('min')>-1)):
                myDate=datetime.datetime.now()
                myDate = myDate.strftime('%d %b %Y')

            if((myDate.find('ayer')>-1) or (myDate.find('yesterday')>-1)):
                myDate=datetime.datetime.now()-datetime.timedelta(1)
                myDate = myDate.strftime('%d %b %Y')


    return myDate




def doScrappingKeywords(myQuery):
    global driver, proxy,server,f2

    filters='&filters=eyJycF9hdXRob3I6MCI6IntcIm5hbWVcIjpcIm1lcmdlZF9wdWJsaWNfcG9zdHNcIixcImFyZ3NcIjpcIlwifSIsInJwX2NyZWF0aW9uX3RpbWU6MCI6IntcIm5hbWVcIjpcImNyZWF0aW9uX3RpbWVcIixcImFyZ3NcIjpcIntcXFwic3RhcnRfeWVhclxcXCI6XFxcIjIwMjFcXFwiLFxcXCJzdGFydF9tb250aFxcXCI6XFxcIjIwMjEtMVxcXCIsXFxcImVuZF95ZWFyXFxcIjpcXFwiMjAyMVxcXCIsXFxcImVuZF9tb250aFxcXCI6XFxcIjIwMjEtMTJcXFwiLFxcXCJzdGFydF9kYXlcXFwiOlxcXCIyMDIxLTEtMVxcXCIsXFxcImVuZF9kYXlcXFwiOlxcXCIyMDIxLTEyLTMxXFxcIn1cIn0ifQ%3D%3D'

    startBrowser()

    keywords = pd.read_excel('kw2.xlsx', sheet_name='words')
    keywords['Theme'] = keywords['Theme'].str.strip()
    keywords['Subtheme'] = keywords['Subtheme'].str.strip()
    keywords['Keyword'] = keywords['Keyword'].str.strip()

    print('General KW',len(keywords))

    e_keywords = pd.read_excel('especific_keywords.xlsx')
    e_keywords['Theme'] = e_keywords['Theme'].str.strip()
    e_keywords['Subtheme'] = e_keywords['Subtheme'].str.strip()
    e_keywords['Keyword'] = e_keywords['Keyword'].str.strip()

    print('Especific KW',len(e_keywords))

    keywords=pd.concat([e_keywords,keywords])

    print('TOTAL KW',len(keywords))


    arr = os.listdir()
    arr = [f for f in arr if f.endswith('.xlsx')]
    arr = [f.replace('%23', '#') for f in arr]
    arr = [f.replace('%40', '@') for f in arr]

    ready=[]
    for index, row in keywords.iterrows():
        myKeyword = row['Keyword']
        for f in arr:
            if (myKeyword in f):
                ready.append(myKeyword)

    keywords=keywords[~(keywords['Keyword'].isin(ready))]



    keywordNumber=1

    for index, row in keywords.iterrows():

        myKeyword=row['Keyword']
        myTheme=row['Theme']
        mySubtheme=row['Subtheme']

        print(myKeyword)
        if(myKeyword.find('#')>-1):
            myKeyword=myKeyword.replace('#','%23')

        if (myKeyword.find('@') > -1):
            myKeyword = myKeyword.replace('#', '%40')

        responseList = []

        try:

            myurl = 'https://www.facebook.com/search/posts/?q=' + str(myKeyword) + '&spell=1'+ filters

            proxy.new_har("myHar", options={'captureHeaders': True, 'captureContent': True, 'captureEntries': True,
                                            'captureBinaryContent': True})
            time.sleep(3)
            driver.get(myurl)
            time.sleep(5)

        except Exception as e:
            print('Exception first load',e)
            startBrowser()
            myurl = 'https://www.facebook.com/search/posts/?q=' + str(myKeyword) + filters
            proxy.new_har("myHar", options={'captureHeaders': True, 'captureContent': True, 'captureEntries': True,
                                     'captureBinaryContent': True})
            time.sleep(3)
            driver.get(myurl)
            time.sleep(5)


        try:
            # get first posts
            for entry in proxy.har['log']['entries']:
                if entry['request']['url'] == myurl:
                    if 'text' in list(entry['response']['content'].keys()):
                        res = brotli.decompress(base64.b64decode(entry['response']['content']['text'])).decode()
                        #res = entry['response']['content']['text']
                        #print(res)

                        if ('{"data":{"serpResponse":{"results":{"edges":' in res):
                            MyStr = res.split('{"data":{"serpResponse":{"results":{"edges"')[1]
                            MyStr = '{"data":{"serpResponse":{"results":{"edges"' + MyStr

                        MyStr = MyStr.split(',"extensions"')[0]
                        MyStr = MyStr+'}'

                        firstPosts = json.dumps({'data': {'node': json.loads(MyStr)}})
                        firstPosts = json.loads(firstPosts)
                        responseList.append(firstPosts)

        except Exception as e:
            print('Exception first posts',e)

        # scroll to next posts
        w=False
        actualRole=''
        endOfResults = False
        maximumScrolls=0

        try:

            while ((actualRole != 'END_OF_RESULTS_INDICATOR') and (endOfResults==False) and (maximumScrolls<30)):
                time.sleep(random.randint(4,6))
                if (w == True ):
                    print("SCROLL", w)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                time.sleep(random.randint(4,6))

                try:
                    data = driver.page_source
                    soup = BeautifulSoup(data, "lxml")
                    text=soup.get_text().lower()
                    if((text.find('fin de los resultados')>-1) or (text.find('end of results')>-1) or (text.find('no encontramos resultados')>-1) or (text.find('solo incluyen contenido que puedes ver')>-1)):
                        endOfResults=True
                except Exception as e:
                    print('Exception on soup',e)

                for entry in proxy.har['log']['entries']:
                    try:
                        if entry['request']['url'] == 'https://www.facebook.com/api/graphql/':
                            if 'text' in list(entry['response']['content'].keys()):
                                #pdb.set_trace()
                                try:
                                    res = brotli.decompress(base64.b64decode(entry['response']['content']['text'])).decode()
                                except Exception as e:
                                    res=entry['response']['content']['text']
                                    print('Exception on brtoli')

                                try:
                                    j=json.loads(res)
                                except Exception as e:
                                    print('TRYING SECOND SPLIT')
                                    if ('{"label":"CometFeedStoryVideoAttachmentVideoPlayer_video$defer$VideoPlayerWithVideoCardsOverlay_video"' in res):
                                        res = res.split('{"label":"CometFeedStoryVideoAttachmentVideoPlayer_video$defer$VideoPlayerWithVideoCardsOverlay_video"')[0]
                                    j=json.loads(res)


                                if 'serpResponse' in list(j['data']):
                                    j=json.dumps({'data': {'node': json.loads(res)}})
                                    j=json.loads(j)
                                    responseList.append(j)
                                    actualResponse=j['data']['node']['data']
                                    for temp in actualResponse['serpResponse']['results']['edges']:
                                        actualRole=temp['node']['role']
                    except Exception as e:
                        print('Exception on a while iter', e)


                proxy.new_har("myHar", options={'captureHeaders': True, 'captureContent': True, 'captureEntries': True,
                                                'captureBinaryContent': True})
                w = True

                print('End of res', endOfResults)
                print('Actual Role', actualRole)
                print('Maximun Scrolls',maximumScrolls)
                maximumScrolls=maximumScrolls+1

        except Exception as e:
            print("exception on while loop",e)


        allPosts=[]
        for i in range(0, len(responseList)):

            try:
                q = responseList[i]['data']['node']['data']
                for subq in q['serpResponse']['results']['edges']:

                    if('click_model' in subq['relay_rendering_strategy']['view_model'].keys()):

                        post=[]
                        try:
                            content = subq['relay_rendering_strategy']['view_model']['content_model']['title_text']
                            content = content.replace("\n", " ").replace("\r", " ").replace("\t", " ")
                            if(content.startswith('…')):
                                content = content.replace('…','',1)

                        except:
                            try:
                                content = \
                                subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['content']['story']['comet_sections']['message'][
                                    'story']['message'][
                                    'text']
                                content = content.replace("\n", " ").replace("\r", " ").replace("\t", " ")
                            except:
                                content = ''

                        print('CONTENT: ', content)


                        try:
                            date = subq['relay_rendering_strategy']['view_model']['header_model']['timestamp']
                            correct_date=False

                        except:
                            try:
                                date = subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['context_layout']['story']['comet_sections'][
                                    'metadata'][0]['story']['creation_time']

                                date = format_date_col2(date)
                                correct_date=True
                            except:
                                date = ''

                        print('DATETIME: ', date)



                        try:
                            permalink= subq['relay_rendering_strategy']['view_model']['click_model']['permalink']
                        except:
                            try:
                                permalink = subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['feedback']['story']['url']
                            except:
                                permalink = ''

                        print('PERMALINK ', permalink)



                        try:
                            totalComments=subq['relay_rendering_strategy']['view_model']['footer_model']['feedback']['comment_count']['total_count']
                            totalComments=float(totalComments)

                        except:
                            try:
                                totalComments = subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['feedback']['story']['feedback_context'][
                                    'feedback_target_with_context']['comment_count']['total_count']
                                totalComments = float(totalComments)

                            except:
                                totalComments = 0


                        print('TOTAL COMMENTS', totalComments)



                        try:
                            totalReactions=subq['relay_rendering_strategy']['view_model']['footer_model']['feedback']['reaction_count']['count']
                            totalReactions=float(totalReactions)
                        except:
                            try:
                                totalReactions = \
                                subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['feedback']['story']['feedback_context'][
                                    'feedback_target_with_context']['comet_ufi_summary_and_actions_renderer'][
                                    'feedback']['reaction_count'][
                                    'count']
                                totalReactions = float(totalReactions)
                            except:
                                totalReactions = 0

                        print('TOTAL REACTIONS', totalReactions)


                        try:
                            shareCount=subq['relay_rendering_strategy']['view_model']['footer_model']['feedback']['share_count']['count']
                            shareCount=float(shareCount)
                        except:
                            try:
                                shareCount = subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['feedback']['story']['feedback_context'][
                                    'feedback_target_with_context']['comet_ufi_summary_and_actions_renderer'][
                                    'feedback']['share_count'][
                                    'count']
                                shareCount = float(shareCount)
                            except:
                                shareCount = 0

                        print('SHARE COUNT', shareCount)



                        try:
                            mediaType = subq['relay_rendering_strategy']['view_model']['media_model_for_content']['attachment_media'][0]['__typename']
                        except:
                            try:
                                mediaType = subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['content']['story']['attachments'][0][
                                    'style_type_renderer']['attachment']['media']['__typename']
                            except:
                                mediaType = 'UNKNOWN'

                        print('MEDIA TYPE', mediaType)



                        try:
                            statusID = subq['relay_rendering_strategy']['view_model']['media_model_for_content']['attachment_media'][0]['id']
                        except:
                            try:
                                statusID = subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['content']['story']['attachments'][0][
                                    'style_type_renderer']['attachment']['media']['id']
                            except:
                                statusID = permalink.split('/')[-1]

                        print('statusID', statusID)


                        try:
                            author = subq['relay_rendering_strategy']['view_model']['header_model']['author_model']['author_text']
                        except:
                            try:
                                author = subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['context_layout']['story']['comet_sections'][
                                    'actor_photo']['story']['actors'][0]['name']
                            except:
                                author = ''

                        print('author: ', author)

                        try:
                            authorLink = subq['relay_rendering_strategy']['view_model']['header_model']['author_model']['author']['url']
                        except:
                            try:
                                authorLink = subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['context_layout']['story']['comet_sections'][
                                    'actor_photo']['story']['actors'][0]['profile_url']
                            except:
                                authorLink = ''

                        print('authorlink: ', authorLink)


                        try:
                            reactions = subq['relay_rendering_strategy']['view_model']['footer_model']['feedback']['top_reactions']['edges']
                        except:
                            try:
                                reactions = \
                                    subq['relay_rendering_strategy']['view_model']['click_model']['story']['comet_sections']['feedback']['story']['feedback_context'][
                                        'feedback_target_with_context'][
                                        'comet_ufi_summary_and_actions_renderer']['feedback']['top_reactions']['edges']
                            except:
                                reactions = []


                        reactionsDict = {'LIKE': 0, 'LOVE': 0, 'HAHA': 0, 'WOW': 0, 'SUPPORT': 0, 'SAD': 0, 'ANGER': 0,
                                         'THANKFUL': 0,
                                         'PRIDE': 0}
                        for r in reactions:
                            reactType=r['node']['reaction_type']
                            reactCount=r['reaction_count']
                            reactCount=float(reactCount)
                            if reactType in list(reactionsDict.keys()):
                                reactionsDict[reactType]=reactionsDict.get(reactType)+reactCount


                        print(reactionsDict)
                        print("####################################")

                        totalEngagement=totalReactions+totalComments
                        post.append(myTheme)
                        post.append(mySubtheme)
                        post.append('FACEBOOK')
                        post.append(author)
                        post.append(authorLink)
                        post.append(statusID)
                        post.append(permalink)
                        post.append(date)
                        post.append(content)
                        post.append(mediaType)
                        post.append(totalReactions)
                        post.append(totalComments)
                        post.append(shareCount)
                        post.append(totalEngagement)
                        post.append(correct_date)
                        for r in reactionsDict.keys():
                            post.append(reactionsDict.get(r))

                        allPosts.append(post)

            except Exception as e:
                print('Exception on loading posts content', e)


        try:
            headings=['theme','subtheme','platform','author','author_link','statusID','permalink','date','content','media_type','reaction_count','comment_count','share_count','total_engagement','correct_date']
            for r in reactionsDict.keys():
                headings.append(r)

            result = pd.DataFrame(allPosts, columns=headings)
            result.to_excel(myTheme+'_'+mySubtheme+'_'+myKeyword+'.xlsx')


            result['date'] = result.apply(lambda x: FIX_DATE(x['date'],x['correct_date']), axis=1)
            result['date'] = result.apply(lambda x: format_date_col(x['date'],x['correct_date']), axis=1)
            temp = result["date"].astype('str').str.split(" ", n=1, expand=True)
            result["date"] = temp[0]
            result.drop('correct_date',axis=1,inplace=True)
            result.to_excel(myTheme+'_'+mySubtheme+'_'+myKeyword+'.xlsx')


        except Exception as e:
            print('Exception Creating DF', e)

        keywordNumber = keywordNumber + 1
        print('Iteration',keywordNumber)
        if keywordNumber%300==0:
            keywordNumber=0
            proxy.close()
            server.stop()
            driver.close()
            startBrowser()





if __name__ == "__main__":

    global driver, proxy,server,f2

    arr = os.listdir()
    arr = [f for f in arr if f.endswith('.xlsx')]

    retrys=0
    doScrappingKeywords('')

    proxy.close()
    server.stop()
    driver.close()

    #while (len(arr)<435 or retrys>=20):
    #    try:
    #        doScrappingKeywords('')
    #        arr = os.listdir()
    #        arr = [f for f in arr if f.endswith('.xlsx')]
    #        retrys=retrys+1

    #    except Exception as e:
    #        print('GLOBAL EXCEPTION',e)
    #        arr = os.listdir()
    #        arr = [f for f in arr if f.endswith('.xlsx')]
    #        retrys=retrys+1
