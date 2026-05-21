import pygame
import sqlite3 
import os
import sys
from datetime import datetime

pygame.init()
size=(1400,900)
width,height=size
screen=pygame.display.set_mode(size)
pygame.display.set_caption("Klondike Solitaire")
clock=pygame.time.Clock()

BLACK=(0,0,0)
GREEN_BACKGROUND=(18,97,46)
GREEN_TITLE=(35,124,17)
WHITE=(255,255,255)
GREEN=(0,200,0)
YELLOW=(255,255,0)
RED=(220,0,0)
GREY_BAR=(70,70,70)
BLUE=(40,120,255)

current_theme="light"

def apply_theme():
    if current_theme=="light":
        return "back_red"
    else:
        return "back_blue"

title_font=pygame.font.Font('PressStart2P-Regular.ttf',42)
button_font=pygame.font.Font('PressStart2P-Regular.ttf',22)
small_font=pygame.font.Font('PressStart2P-Regular.ttf',14)

conn=sqlite3.connect('solitaire.db')
cursor=conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS stats(
    date TEXT,
    wins INTEGER,
    loss INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS cards(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    suit TEXT,
    rank TEXT,
    image_path TEXT,
    card_back TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS saved_games(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_name TEXT,
    date TEXT,
    time TEXT,
    score INTEGER,
    timer INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS playable_cards(
    save_id INTEGER,
    pile INTEGER,
    card TEXT,
    hidden INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS draw_pile(
    save_id INTEGER,
    position INTEGER,
    card TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS solved_piles(
    save_id INTEGER,
    suit TEXT,
    card TEXT
)
""")
conn.commit()

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

class Card:
    def __init__(self,suit,rank,image):
        self.suit=suit
        self.rank=rank
        self.image=image
        self.rect = image.get_rect()

def load_cards_from_folder():
    suits=["trefl","kier","pik","karo"]
    ranks=["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    card_dict={}
    for suit in suits:
        for rank in ranks:
            filename=f"smaller/{rank}_{suit}.png"
            try:
                image=pygame.image.load(filename).convert_alpha()
                card_dict[f"{rank}_{suit}"]=Card(rank,suit,image)
            except:
                print("Missing:",filename)

    card_dict["back_red"]=Card("back","red",pygame.image.load("smaller/rewers_czerwony.png").convert_alpha())
    card_dict["back_blue"] = Card("back","blue",pygame.image.load("smaller/rewers_niebieski.png").convert_alpha())
    return card_dict

cards=load_cards_from_folder()
all_cards=list(cards.values())
test_draw_pile=all_cards[:24]
test_waste_pile=[]
test_foundations={"♠️":None, "♥️":None, "♦️":None, "♣️":None}
test_tableau=[]
index=24
for pile_size in range(1,8):
    pile=[]
    for _ in range(pile_size):
        if index<len(all_cards):
            pile.append(all_cards[index])
            index+=1
    test_tableau.append(pile)

difficulty='EASY'
drawn_amount=1
current_screen='menu'
game_timer=0

start_button=pygame.Rect(0,0,250,70)
difficulty_button=pygame.Rect(0,0,250,70)
stats_button=pygame.Rect(0,0,250,70)
exit_button=pygame.Rect(0,0,120,40)
back_button=pygame.Rect(0,0,120,40)

def game_page():
    global current_theme
    Top_bar_height=70
    Top_bar_surface=pygame.Surface((width,Top_bar_height),pygame.SRCALPHA)
    Top_bar_surface.fill(GREY_BAR)
    back_button=pygame.Rect(20,15,120,40)
    save_button=pygame.Rect(160,15,120,40)
    theme_button=pygame.Rect(300,15,160,40)
    draw_pile_rect=pygame.Rect(60,100,90,130)
    waste_pile_rect=pygame.Rect(190,100,90,130)
    foundations_piles=[]
    start_x=850
    for i in range(4):
        foundations_piles.append(pygame.Rect(start_x+i*120,100,90,130))
    tableau_piles=[]
    tableau_x=60
    for i in range(7):
        tableau_piles.append(pygame.Rect(tableau_x+i*170,300,90,130))
    card_back_key=apply_theme()
    screen.fill(GREEN_BACKGROUND)
    screen.blit(Top_bar_surface,(0,0))
    pygame.draw.rect(screen,RED,back_button)
    pygame.draw.rect(screen,BLUE,save_button)
    pygame.draw.rect(screen,YELLOW,theme_button)
    screen.blit(small_font.render("BACK",True,BLACK),(40,28))
    screen.blit(small_font.render("SAVE",True,BLACK),(180,28))
    screen.blit(small_font.render("THEME",True,BLACK),(325,28))
    timer_text=button_font.render(f"TIME:{int(game_timer)}",True,WHITE)
    screen.blit(timer_text,(1080,22))
    screen.blit(cards[card_back_key].image,draw_pile_rect.topleft)
    if test_waste_pile:
        screen.blit(test_waste_pile[-1].image,waste_pile_rect.topleft)
    else:
        pygame.draw.rect(screen,WHITE,waste_pile_rect,3)
    foundation_suits=["♠️", "♥️", "♦️", "♣️"]
    for i, pile in enumerate(foundations_piles):
        suit=foundation_suits[i]
        if test_foundations[suit] is None:
            pygame.draw.rect(screen,WHITE,pile,3)
            suit_text=title_font.render(suit,True,WHITE)
            screen.blit(suit_text,suit_text.get_rect(center=pile.center))
        else:
            screen.blit(test_foundations[suit].image,pile.topleft)
    for i, pile in enumerate(tableau_piles):
        pygame.draw.rect(screen,WHITE,pile,3)
        if i<len(test_tableau):
            y_offset=0
            for card in test_tableau[i]:
                screen.blit(cards[card_back_key].image,(pile.x,pile.y+y_offset))
                y_offset+=30

def menu_page():
    screen.fill(BLACK)
    title_text=title_font.render('Klondike Solitaire',True,GREEN_TITLE)
    screen.blit(title_text,title_text.get_rect(center=(width//2,120)))
    start_button.center=(width//2,260)
    difficulty_button.center=(width//2,360)
    stats_button.center=(width//2,460)
    exit_button.center=(width-90,50)
    pygame.draw.rect(screen,GREEN,start_button)
    pygame.draw.rect(screen,YELLOW,difficulty_button)
    pygame.draw.rect(screen,RED,stats_button)
    pygame.draw.rect(screen,RED,exit_button)
    screen.blit(button_font.render("START",True,BLACK),start_button.move(70,20))
    screen.blit(button_font.render(difficulty,True,BLACK),difficulty_button.move(70,20))
    screen.blit(button_font.render("STATS",True,BLACK),stats_button.move(70,20))
    screen.blit(button_font.render('EXIT',True,BLACK),exit_button.move(20,10))

def stats_diagram():
    screen.fill(BLACK)
    back_button.center=(100,50)
    pygame.draw.rect(screen,RED,back_button)
    screen.blit(small_font.render("BACK",True,BLACK),back_button.move(20,10))
    graph_width=700
    graph_height=400
    graph_x=(width-graph_width)//2
    graph_y=(height-graph_height)//2
    graph_rect=pygame.Rect(graph_x,graph_y,graph_width,graph_height)
    pygame.draw.rect(screen,WHITE,graph_rect)
    pygame.draw.line(screen,BLACK,(graph_x+50,graph_y+20),(graph_x+50,graph_y+graph_height-20),3)
    pygame.draw.line(screen,BLACK,(graph_x+50,graph_y+graph_height-20),(graph_x+graph_width-20,graph_y+graph_height-20),3)
    cursor.execute("SELECT * FROM stats")
    data=cursor.fetchall()
    x=graph_x+80
    wins_points=[]
    loss_points=[]
    for row in data:
        date,wins,loss=row
        win_y=graph_y+graph_height-20-wins*50
        loss_y=graph_y+graph_height-20-loss*50
        wins_points.append((x,win_y))
        loss_points.append((x,loss_y))
        pygame.draw.circle(screen,GREEN,(x,win_y),6)
        pygame.draw.circle(screen,RED,(x,loss_y),6)
        screen.blit(small_font.render(date,True,BLACK),(x-20,graph_y+graph_height))
        x+=100
    if len(wins_points)> 1:
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
                    current_screen='game'
                if difficulty_button.collidepoint(mouse_pos):
                    if difficulty=='EASY':
                        difficulty='HARD'
                        drawn_amount=3
                    else:
                        difficulty='EASY'
                        drawn_amount=1
                if stats_button.collidepoint(mouse_pos):
                    current_screen='stats'
                if exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    conn.close()
                    sys.exit()
            elif current_screen=='stats':
                if back_button.collidepoint(mouse_pos):
                    current_screen='menu'
            elif current_screen=='game':
                theme_button=pygame.Rect(300,15,160,40)
                back_button=pygame.Rect(20,15,120,40)
                if theme_button.collidepoint(mouse_pos):
                    current_theme="dark" if current_theme=="light" else "light"
                if back_button.collidepoint(mouse_pos):
                    current_screen='menu'
    if current_screen=='game':
        game_timer+=1/60
    if current_screen=='menu':
        menu_page()
    elif current_screen=='stats':
        stats_diagram()
    elif current_screen=='game':
        game_page()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
conn.close()
sys.exit()
