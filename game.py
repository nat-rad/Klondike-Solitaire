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
WHITE=(255,255,255)
GREEN=(0,200,0)
YELLOW=(255,255,0)
RED=(220,0,0)

difficulty='EASY'
drawn_amount=1
current_screen='menu'

start_button=pygame.Rect(275,180,250,70)
difficulty_button=pygame.Rect(275,290,250,70)
stats_button=pygame.Rect(275,400,250,70)
back_button=pygame.Rect(20,20,100,40)

title_font=pygame.font.Font('PressStart2P-Regular.ttf',42)
button_font=pygame.font.Font('PressStart2P-Regular.ttf',22)
small_font=pygame.font.Font('PressStart2P-Regular.ttf',14)

def menu_page():
    screen.fill(BLACK)
    title_text=title_font.render('Klondike Soliraire',True,GREEN_title)
    title_rect=title_text.get_rect(center=(width//2,50))
    start_text=button_font.render('START',True,BLACK)
    start_rect=start_text.get_rect(center=start_button.center)
    difficulty_text=button_font.render(difficulty,True,BLACK)
    difficulty_rect=difficulty_text.get_rect(center=difficulty_button.center)
    stats_text=button_font.render('STATS',True,BLACK)
    stats_rect=stats_text.get_rect(center=stats_button.center)
    screen.blit(title_text,title_rect)
    pygame.draw.rect(screen,GREEN,start_button)
    screen.blit(start_text,start_rect)
    pygame.draw.rect(screen,YELLOW,difficulty_button)
    screen.blit(difficulty_text,difficulty_rect)
    pygame.draw.rect(screen,RED,stats_button)
    screen.blit(stats_text,stats_rect)

conn=sqlite3.connect('stats,db') #see comment on line 106
cursor=conn.cursor()              

def stats_diagram():
    screen.fill(BLACK)
    pygame.draw.rect(screen,RED,back_button)
    back_text=small_font.render('BACK',True,BLACK)
    screen.blit(back_text,(30,32))
    graph_rect=pygame.Rect(120,120,550,350)
    pygame.draw.rect(screen,WHITE,graph_rect)
    pygame.draw.line(screen,BLACK,(150,140),(150,420),3)
    pygame.draw.line(screen,BLACK,(150,420),(620,420),3)
    for i in range(0,6):
        y=420-i*50
        pygame.draw.line(screen,BLACK,(145,y),(155,y),2)
        label=small_font.render(str(i),True,BLACK)
        screen.blit(label,(120,y-10))
    cursor.execute('SELECT * FROM stats')#make sure to make a stats sql table
    data=cursor.fetchall()
    x=180
    wins_points=[]
    loss_points=[]
    for row in data:
        date=row[0]
        wins=row[1]
        loss=row[2]
        win_y=420-wins*50
        loss_y=420-loss*50
        wins_points.append((x,win_y))
        loss_points.append((x,loss_y))
        pygame.draw.circle(screen,GREEN,(x,win_y),6)
        pygame.draw.circle(screen,RED,(x,loss_y),6)
        date_text=small_font.render(date,True,BLACK)
        screen.blit(date_text,(x-20,435))
        x+=100
    if len(wins_points)>1:
        pygame.draw.lines(screen,GREEN,False,wins_points,2)
    if len(loss_points)>1:
        pygame.draw.lines(screen,RED,False,loss_points,2)

running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if event.type==pygame.MOUSEBUTTONDOWN:
            mouse_pos=pygame.mouse.get_pos()
            if current_screen=='menu':
                if start_button.collidepoint(mouse_pos):
                    print('game started')
                    print('card draw:',drawn_amount)
                if difficulty_button.collidepoint(mouse_pos):
                    if difficulty=='EASY':
                        difficulty='HARD'
                        drawn_amount=3
                    else:
                        difficulty='EASY'
                        drawn_amount=1
                if stats_button.collidepoint(mouse_pos):
                    current_screen='stats'
            elif current_screen=='stats':
                if back_button.collidepoint(mouse_pos):
                    current_screen='menu'
        if current_screen=='menu':
            menu_page()
        elif current_screen=='stats':
            stats_diagram()
        pygame.display.flip()
pygame.quit()
sys.exit()
