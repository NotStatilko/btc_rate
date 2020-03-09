from PIL import Image, ImageFont, ImageDraw 

from json import loads
from datetime import datetime, timedelta

from urllib.request import urlopen
from bs4 import BeautifulSoup


def get_fng_color(index: int):
    red, green, _, _ = (255,0,0,255)
    if index <= 1: 
        return (255,0,0,255)
    elif index >= 100:
        return (0,255,0,255)
        
    for _ in range(index):
        if green < 255:
            green += 4.25
        else: red -= 4.25
    
    return (int(red), int(green), 0, 255)


fng_link = 'https://api.alternative.me/fng/'
halving_url = 'https://www.binance.vision/halving'
difficulty_url = 'https://m.btc.com/stats/diff'
curr_price = 'https://api.coindesk.com/v1/bpi/currentprice/btc/.json'

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

font_rate = ImageFont.truetype('Anonymous.ttf',97)
font_per_change = ImageFont.truetype('Anonymous.ttf',45)
font_old_rate_date = ImageFont.truetype('Anonymous.ttf',30)
font_other = ImageFont.truetype('Anonymous.ttf',38)
font_diff = ImageFont.truetype('Anonymous.ttf',35)

template = Image.open('btc_template.png')
draw = ImageDraw.Draw(template)

rate = loads(urlopen(curr_price).read())['bpi']['USD']['rate']
rate_fl = float(rate.replace(',',''))
rate = '$' + rate.split('.')[0]

old_rate = urlopen('https://api.coindesk.com/v1/bpi/historical/close.json')
old_rate_loads = loads(old_rate.read())['bpi']
old_rate_fl = old_rate_loads[tuple(old_rate_loads.keys())[-1]] 
old_rate_date = tuple(old_rate_loads.keys())[-1]

fng_index = int(loads(urlopen(fng_link).read())['data'][0]['value'])
fng_color = get_fng_color(fng_index)

per_symbol = '+' if rate_fl > old_rate_fl else '-'
sorted_rates = sorted((rate_fl, old_rate_fl))

per_change = per_symbol + str(
    round(100 - (sorted_rates[0] / sorted_rates[1] * 100),2)
) + '%'   
         
date = datetime.now().ctime().replace('  ',' ')[4:]

rate_text_size = draw.textsize(rate,font=font_rate)
rate_position = (
    (1080 - rate_text_size[0] - 250) / 2, 
    (1920 - rate_text_size[1] + 7) / 2
)
per_change_size = draw.textsize(per_change,font=font_per_change)
per_change_position = (
    (1080 - per_change_size[0] + 730) / 2, 
    (1920 - per_change_size[1]) / 2
)
old_rate_date_size = draw.textsize(old_rate_date,font=font_old_rate_date)
old_rate_date_position = (
    (1080 - old_rate_date_size[0] + 745) / 2, 
    (1920 - old_rate_date_size[1] - 185) / 2
)
halving_text_size = draw.textsize(halving,font=font_other)
halving_position = (
    (1080 - halving_text_size[0] + 210) / 2, 
    (1920 - halving_text_size[1] + 311) / 2
)
date_text_size = draw.textsize(date,font=font_other)
date_position = (
    (1080 - halving_text_size[0]) / 2, 
    (1920 - halving_text_size[1] + 880) / 2
)
est_diff_text_size = draw.textsize(
    estimated_difficulty,font=font_diff
)
est_diff_position = (
    (1080 - est_diff_text_size[0] + 293) / 2, 
    (1920 - est_diff_text_size[1] + 556) / 2
)
est_diff_time_text_size = draw.textsize(
    estimated_time,font=font_diff
)
est_diff_time_position = (
    (1080 - est_diff_time_text_size[0] + 783) / 2, 
    (1920 - est_diff_time_text_size[1] + 557) / 2
)
draw.text(rate_position,rate,(0,0,0),font=font_rate)
draw.text(halving_position,halving,(0,0,0),font=font_other)
draw.text(date_position,date,(255,255,255),font=font_other)

diff_color = (0,122,0) if estimated_difficulty[0] == '+' else (160,0,0)
per_change_color = (0,122,0) if per_change[0] == '+' else (160,0,0)

draw.text(est_diff_position,estimated_difficulty,diff_color,font=font_diff)
draw.text(per_change_position,per_change,per_change_color,font=font_per_change)
draw.text(old_rate_date_position,old_rate_date,(80,80,80),font=font_old_rate_date)
draw.text(est_diff_time_position,estimated_time,(0,0,0),font=font_diff)

ImageDraw.floodfill(template,(345,704),fng_color)

template.save('btc_rate.png')