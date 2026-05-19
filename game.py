import pygame
import sqlite3 
import os
import sys
from datetime import datetime

def extract_date():
    date_extract=datetime.now()
    date=date_extract.strftime('%d.%m.%Y')
    return date

def extract_time():
    time_extract=datetime.now()
    hour=time_extract.hour
    minute=time_extract.minute
    hour_str=str(hour)
    minute_str=str(minute)
    time=hour_str+"."+minute_str
    return time

def table_name_generator(): #add the feature
    time=extract_time()
    date=extract_date()
    name=feature+'_'+date+'_'+time
    print(name)

def folder_for_game():
    time=extract_time()
    date=extract_date()
    name='game~'+date+'~'+time
    os.makedirs(name)
    return name

def open_folder():
    date=extract_date()
    time=extract_time()
    name='game~'+date+'~'+time
    path="C:\\Users\\askna\\Desktop\\nea\\"+name
    try:
        os.system(f'start{os.path.realpath(path)}')
        print('good')
    except:
        print("An error has occured and a file doesn't exsist")

pygame.init()
size=(800,600)
width,height=size
screen=pygame.display.set_mode((size))
pygame.display.set_caption('Klondike Solitaire')

BLACK=(0,0,0)
GREEN_title=(35,124,17)

font=pygame.font.Font('PressStart2P-Regular.ttf',32)
text=font.render('Klondike Solitaire',True,GREEN_title)
text_play=font.render('PLAY',True,BLACK)
text_rec=text.get_rect(center=(width//2,50))
text_play_rec=text_play.get_rect(center=(width//2,250))

running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    screen.fill(BLACK)
    screen.blit(text,text_rec)
    screen.blit(text_play,text_play_rec)
    pygame.display.flip()

pygame.quit()
sys.exit()
