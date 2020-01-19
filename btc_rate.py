from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

from json import loads
from datetime import datetime, timedelta

from urllib.request import urlopen
from bs4 import BeautifulSoup


halving_url = 'https://www.binance.vision/halving'
difficulty_url = 'https://m.btc.com/stats/diff'

bs4_halving = BeautifulSoup(urlopen(halving_url).read(),'html.parser')
bs4_difficulty = BeautifulSoup(urlopen(difficulty_url).read(),'html.parser')

halving_timer = bs4_halving.find_all(class_='halvingTimer')[0].find_all(class_='time')
days, hours, minutes, seconds = [int(i.text) for i in halving_timer]

halving_timedelta = timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)
halving = (datetime.now() + halving_timedelta).ctime().replace('  ',' ')[4:]

to_replace = ((' ',''),('Days','d'),('Hours','h'),('\n',' '))
diff_info = bs4_difficulty.find_all('dd')

estimated_difficulty = diff_info[2].text.split('\n')[1].strip()
estimated_difficulty = estimated_difficulty.replace('(','').replace(')','')

estimated_time = diff_info[3].text
for f,t in to_replace:
    estimated_time = estimated_time.replace(f,t)

font_rate = ImageFont.truetype('Anonymous.ttf',95)
font_other = ImageFont.truetype('Anonymous.ttf',38)
font_diff = ImageFont.truetype('Anonymous.ttf',35)

template = Image.open('btc_template.png')
draw = ImageDraw.Draw(template)

rate = urlopen('https://api.coindesk.com/v1/bpi/currentprice/btc/.json')
rate = '$' + str(loads(rate.read())['bpi']['USD']['rate']).split('.')[0]

date = datetime.now().ctime().replace('  ',' ')[4:]

rate_text_size = draw.textsize(rate,font=font_rate)
rate_position = (
    (1080 - rate_text_size[0]) / 2, 
    (1080 - rate_text_size[1] - 20) / 2
)
halving_text_size = draw.textsize(halving,font=font_other)
halving_position = (
    (1080 - halving_text_size[0] + 210) / 2, 
    (1080 - halving_text_size[1] + 311) / 2
)
date_text_size = draw.textsize(date,font=font_other)
date_position = (
    (1080 - halving_text_size[0]) / 2, 
    (1080 - halving_text_size[1] + 880) / 2
)
est_diff_text_size = draw.textsize(
    estimated_difficulty,font=font_diff
)
est_diff_position = (
    (1080 - est_diff_text_size[0] + 293) / 2, 
    (1080 - est_diff_text_size[1] + 556) / 2
)
est_diff_time_text_size = draw.textsize(
    estimated_time,font=font_diff
)
est_diff_time_position = (
    (1080 - est_diff_time_text_size[0] + 783) / 2, 
    (1080 - est_diff_time_text_size[1] + 557) / 2
)
draw.text(rate_position,rate,(0,0,0),font=font_rate)
draw.text(halving_position,halving,(0,0,0),font=font_other)
draw.text(date_position,date,(255,255,255),font=font_other)

diff_color = (0,122,0) if estimated_difficulty[0] == '+' else (122,0,0)
draw.text(est_diff_position,estimated_difficulty,diff_color,font=font_diff)
draw.text(est_diff_time_position,estimated_time,(0,0,0),font=font_diff)

template.save('btc_rate.png')
