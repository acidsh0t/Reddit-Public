#!python3

import datetime as dt
from datetime import datetime
import easygui as eg
import matplotlib.pyplot as plt
import pandas as pd
import praw
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

### = Sanity checks

#Easygui Title box
box_title = 'Reddit Scraper'

#Login details
reddit = praw.Reddit(client_id='', \
                     client_secret='', \
                     user_agent='', \
                     username='', \
                     password='')

#Sub selection
_sub_choice = str(eg.enterbox(msg='What sub do you want to analyse? \n (r/[just type this])',title=box_title))
sub_choice = reddit.subreddit(_sub_choice)

#Number of posts to scrape
post_no = int(eg.enterbox(msg='How many posts do you want to see? (Maximum 900)',title=box_title))

def remove_punctuation(text_string): #removes punctuation from str
    for char in text_string:
        if char in '"!@#$%^)&*(-_=+};]{[:<>,.?/\|`~1234567890â€™':
            text_string = text_string.replace(char,'')
        text_string = text_string.replace("'","")
    text_string = text_string.split()
    return text_string

def remove_stopwords(text_string):
    stop_words = set(stopwords.words('english'))
    word_list = word_tokenize(text_string)
    word_list = [word for word in word_list if not word.lower() in stop_words]
    filtered_words = []
    for word in word_list:
        if word not in stop_words:
            filtered_words.append(word)
    filtered_list = [ ' {} '.format(x) for x in filtered_words ] #adds space between list items
    text_string = ''.join([str(elem) for elem in filtered_list]) #converts list into str
    return text_string

def count_in_str(text_string): #counts individual words in str
    word_count = {}
    for word in text_string:
        if word in word_count:
            word_count[word] = word_count[word] + 1
        else:
            word_count[word] = 1
    return word_count

def word_counter(df): #counts words in df
    title_list = list(df['title']) #creates list from title column
    title_list = [ ' {} '.format(x) for x in title_list ] #adds space between list items
    title_str = ''.join([str(elem) for elem in title_list]) #converts list into str
    title_str = title_str.lower()
    title_str = remove_stopwords(title_str)
    title_str = remove_punctuation(title_str)
    count = count_in_str(title_str)

    count_table = pd.DataFrame([count])
    count_table = pd.DataFrame.transpose(count_table)

    path = eg.filesavebox(msg='save location',title='Word Counter',default='word_count.csv')

    count_table.to_csv(path)

def average(x): #gets mean
    try:
        y = sum(x)/len(x)
    except:
        y = 0
    y = '%.2f'%y
    return y

#Category selection
cat_choices = ['Hot','Top','New','Controversial','Search']
cat_selection = str(eg.choicebox(msg='Which category would you like to analyse?',title=box_title,choices=cat_choices))

if cat_selection == 'Top':
    sub_choice = sub_choice.top(limit=post_no)
elif cat_selection == 'Hot':
    sub_choice = sub_choice.hot(limit=post_no)
elif cat_selection == 'New':
    sub_choice = sub_choice.new(limit=post_no)
#elif cat_selection == 'gilded': #Not functional
#    sub_choice = sub_choice.gilded(limit=post_no)
elif cat_selection == 'Controversial':
    sub_choice = sub_choice.controversial(limit=post_no)
elif cat_selection == 'Search':
    keyword = str(eg.enterbox(msg='What would you like to search?',title=box_title))
    _keyword = str('"' + keyword + '"')
    sub_choice = sub_choice.search(_keyword,limit=post_no,)

#Dictionnary creation
print('Creating dictionary')
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

#Request for word frequency analysis
word_count_req = eg.choicebox(msg='Would you like to analyse the word count?',title=box_title,choices=['Yes','No'])
if word_count_req == 'Yes':
    print('Analysing word count')
    word_counter(topics_data)

#Fixing the dates
print('Converting dates')
def get_date(created):
    return dt.datetime.fromtimestamp(created)

_timestamp = topics_data['created'].apply(get_date)

#Replace timestamp with DateTime
topics_data = topics_data.assign(created = _timestamp) #Date in datetime64


#Add time column
print('Adding Time column')
time_created = []#new list 
for created in topics_data['created']:
    _time_created = datetime.strptime(str(created),"%Y-%m-%d %H:%M:%S") #converts to pd datetime
    _time_created = datetime.strftime(_time_created,'%H:%M:%S') #retains time only hh:mm:ss
    time_created.append(_time_created) #adds each entry to list

topics_data ['time_created'] = time_created #adds time_created column

#Count entries within time window
print('Assigning to time window')
time_window = [] #creates new list to assign values to proper time window
time_04 = float(40000)
time_08 = float(80000)
time_12 = float(120000)
time_16 = float(160000)
time_20 = float(200000)
time_24 = float(240000)

for post in topics_data['time_created']:
    post = float(post.replace(':','')) #converts time to floats
    if post < time_04 :
        _time_window = '0h-4h'
        time_window.append(_time_window)
    elif post >= time_04 and post < time_08:
        _time_window = '4h-8h'
        time_window.append(_time_window)
    elif post >= time_08 and post < time_12:
        _time_window = '8h-12h'
        time_window.append(_time_window)
    elif post >= time_12 and post < time_16:
        _time_window = '12h-16h'
        time_window.append(_time_window)
    elif post >= time_16 and post < time_20:
        _time_window = '16h -20h'
        time_window.append(_time_window)
    elif post >= time_20 and post < time_24:
        _time_window = '20h-24h'
        time_window.append(_time_window)

topics_data['time_window'] = time_window #adds time_window to topics_data

#Gets average score per time window
print('Calculating average scores')
_avg_04 = topics_data[topics_data['time_window'] == '0h-4h']['score'].to_list()
_avg_08 = topics_data[topics_data['time_window'] == '4h-8h']['score'].to_list()
_avg_12 = topics_data[topics_data['time_window'] == '8h-12h']['score'].to_list()
_avg_16 = topics_data[topics_data['time_window'] == '12h-16h']['score'].to_list()
_avg_20 = topics_data[topics_data['time_window'] == '16h-20h']['score'].to_list()
_avg_24 = topics_data[topics_data['time_window'] == '20h-24h']['score'].to_list()

avg_04 = average(_avg_04)
avg_08 = average(_avg_08)
avg_12 = average(_avg_12)
avg_16 = average(_avg_16)
avg_20 = average(_avg_20)
avg_24 = average(_avg_24)

mean_score = pd.DataFrame({ 'Time Window':['0h-4h','4h-8h','8h-12h','12h-16h','16h-20h','20h-24h'],
                            'Average Score':[avg_04,avg_08,avg_12,avg_16,avg_20,avg_24]})

mean_score["Average Score"]=mean_score["Average Score"].astype(float)
mean_score.plot(x = 'Time Window', y = 'Average Score', kind = 'bar', title = 'Average Score per Time Window', legend = False,)
plt.show()

#Gets comments per time window
print('Calculating average scores')
_avg_04 = topics_data[topics_data['time_window'] == '0h-4h']['comms_num'].to_list()
_avg_08 = topics_data[topics_data['time_window'] == '4h-8h']['comms_num'].to_list()
_avg_12 = topics_data[topics_data['time_window'] == '8h-12h']['comms_num'].to_list()
_avg_16 = topics_data[topics_data['time_window'] == '12h-16h']['comms_num'].to_list()
_avg_20 = topics_data[topics_data['time_window'] == '16h-20h']['comms_num'].to_list()
_avg_24 = topics_data[topics_data['time_window'] == '20h-24h']['comms_num'].to_list()

avg_04 = average(_avg_04)
avg_08 = average(_avg_08)
avg_12 = average(_avg_12)
avg_16 = average(_avg_16)
avg_20 = average(_avg_20)
avg_24 = average(_avg_24)

mean_comm = pd.DataFrame({ 'Time Window':['0h-4h','4h-8h','8h-12h','12h-16h','16h-20h','20h-24h'],
                            'Average Comments':[avg_04,avg_08,avg_12,avg_16,avg_20,avg_24]})

mean_comm["Average Comments"]=mean_comm["Average Comments"].astype(float)
mean_comm.plot(x = 'Time Window', y = 'Average Comments', kind = 'bar', title = 'Average Comments per Time Window', legend = False,)
plt.show()

#Dialog box to select save location
print('Saving .csv file')
if cat_selection == 'Search':
    path = eg.filesavebox(default=str(_sub_choice + '_' + cat_selection + '_' + keyword +'_'+ str(post_no)+'.csv'))
else:
    path = eg.filesavebox(default=str(_sub_choice + '_' + cat_selection +'_'+ str(post_no)+'.csv'))

#Send to CSV
topics_data.to_csv(path, index=False)
print('Done')
quit()