#! python3
import praw
import pandas as pd
import datetime as dt
import easygui

#Login details
reddit = praw.Reddit(client_id='', \
                     client_secret='', \
                     user_agent='', \
                     username='', \
                     password='')

#Sub selection
_sub_choice = str(input('What sub do you want to analyse?\n'))
sub_choice = reddit.subreddit(_sub_choice)

#Number of posts to scrape
post_no = int(input('How many posts do you want to see? (Maximum 900)\n'))

#Category selection
cat_selection = input('Which category would you like to analyse?\nChoices are (Case sensitive):\nHot\nTop\nNew\nControversial\nor Search\n')
if cat_selection == 'Top':
    sub_choice = sub_choice.top(limit=post_no)
elif cat_selection == 'Hot':
    sub_choice = sub_choice.hot(limit=post_no)
elif cat_selection == 'New':
    sub_choice = sub_choice.new(limit=post_no)
#elif cat_selection == 'Gilded': #Not functional
#    sub_choice = sub_choice.gilded(limit=post_no)
elif cat_selection == 'Controversial':
    sub_choice = sub_choice.controversial(limit=post_no)
elif cat_selection == 'Search':
    keyword = input('What would you like to search?\n')
    _keyword = str('"' + keyword + '"')
    sub_choice = sub_choice.search(_keyword,limit=post_no,)

#Dictionnary creation
print('Creating dictionnary')
topics_dict = { "title":[], \
                "score":[], \
                "id":[], \
                "url":[], \
                "comms_num": [], \
                "created": [], \
                "body":[]}

#Scraping
print('Getting data')
for submission in sub_choice:
    topics_dict["title"].append(submission.title)
    topics_dict["score"].append(submission.score)
    topics_dict["id"].append(submission.id)
    topics_dict["url"].append(submission.url)
    topics_dict["comms_num"].append(submission.num_comments)
    topics_dict["created"].append(submission.created)
    topics_dict["body"].append(submission.selftext)

#Table creation
print('Creating table')
topics_data = pd.DataFrame(topics_dict)

#Fixing the dates
print('Converting dates')
def get_date(created):
    return dt.datetime.fromtimestamp(created)

_timestamp = topics_data["created"].apply(get_date)

#Replace timestamp with DateTime
topics_data = topics_data.assign(created = _timestamp)

#Dialog box to select save location
print('Saving')
if cat_selection == 'Search':
    path = easygui.filesavebox(default=str(_sub_choice + '_' + cat_selection + '_' + keyword +'_'+ str(post_no)+'.csv'))
else:
     path = easygui.filesavebox(default=str(_sub_choice + '_' + cat_selection +'_'+ str(post_no)+'.csv'))

#Send to CSV
topics_data.to_csv(path, index=False)
print('Done')