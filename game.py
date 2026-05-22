import os
import random
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime

import pygame

pygame.init()

WIDTH,HEIGHT=1400,900
CARD_W,CARD_H=120,170
DRAW_X=60
WASTE_X=225
TOP_CARD_Y=100
FOUNDATION_X=650
FOUNDATION_GAP=165
TABLEAU_X=45
TABLEAU_Y=330
TABLEAU_GAP=190
HIDDEN_STEP=24
VISIBLE_STEP=42
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Klondike Solitaire")
clock=pygame.time.Clock()

BLACK=(0,0,0)
WHITE=(255,255,255)
GREEN_BACKGROUND=(18,97,46)
BAR=(54,58,64)
GREEN_TITLE=(35,124,17)
GREEN=(38,185,91)
DARK_GREEN=(12,120,58)
RED=(214,54,54)
YELLOW=(245,202,66)
BLUE=(66,133,244)
GREY=(190, 198, 205)

def font(size,bold=False):
    path="PressStart2P-Regular.ttf"
    if os.path.exists(path):
        return pygame.font.Font(path,size)
    return pygame.font.SysFont("consolas",size,bold=bold)

title_font=font(46,True)
button_font=font(28,True)
small_font=font(20,True)
tiny_font=font(15,True)
card_font=font(26,True)
large_card_font=font(44,True)

DB_PATH="solitaire.db"
conn=sqlite3.connect(DB_PATH)
cursor=conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS stats(
        date TEXT PRIMARY KEY,
        wins INTEGER NOT NULL,
        loss INTEGER NOT NULL
    )
    """
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS saved_games(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        save_name TEXT UNIQUE,
        date TEXT,
        time TEXT,
        score INTEGER,
        timer INTEGER,
        difficulty TEXT,
        draw_count INTEGER
    )
    """
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS playable_cards(
        save_id INTEGER,
        pile INTEGER,
        position INTEGER,
        card TEXT,
        hidden INTEGER
    )
    """
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS draw_pile(
        save_id INTEGER,
        position INTEGER,
        card TEXT
    )
    """
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS waste_pile(
        save_id INTEGER,
        position INTEGER,
        card TEXT
    )
    """
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS solved_piles(
        save_id INTEGER,
        suit TEXT,
        position INTEGER,
        card TEXT
    )
    """
)
def add_column_if_missing(table,column,column_type):
    cursor.execute(f"PRAGMA table_info({table})")
    existing_columns=[row[1] for row in cursor.fetchall()]
    if column not in existing_columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
add_column_if_missing("saved_games", "difficulty", "TEXT")
add_column_if_missing("saved_games", "draw_count", "INTEGER")
add_column_if_missing("playable_cards", "position", "INTEGER")
add_column_if_missing("draw_pile", "position", "INTEGER")
add_column_if_missing("waste_pile", "position", "INTEGER")
add_column_if_missing("solved_piles", "position", "INTEGER")
conn.commit()
RANKS=["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
SUITS=["spades","hearts","clubs","diamonds"]
SUIT_MARK={"spades":"♠️","hearts":"♥️","clubs":"♣️","diamonds":"♦️"}
FILE_SUIT={"spades":"pik","hearts":"kier","clubs":"trefl","diamonds":"karo"}
RED_SUITS={"hearts","diamonds"}
BLACK_SUITS={"spades","clubs"}

CARD_FOLDERS=[os.path.join(os.getcwd(),"cards_120x170"),r"D:\mini nea\cards_120x170",]

@dataclass(eq=False)
class Card:
    suit:str
    rank:str
    image:pygame.Surface|None=None
    @property
    def key(self):
        return f"{self.rank}_{self.suit}"
    @property
    def red(self):
        return self.suit in RED_SUITS

def load_card_image(rank,suit):
    filename=f"{rank}_{FILE_SUIT[suit]}.png"
    for folder in CARD_FOLDERS:
        path=os.path.join(folder,filename)
        if os.path.exists(path):
            image=pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(image, (CARD_W, CARD_H))
    return None

def load_card_back(colour):
    filename="rewers_czerwony.png" if colour=="red" else "rewers_niebieski.png"
    for folder in CARD_FOLDERS:
        path=os.path.join(folder,filename)
        if os.path.exists(path):
            image=pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(image,(CARD_W,CARD_H))
    return None

cards={f"{rank}_{suit}":Card(suit,rank,load_card_image(rank,suit)) for suit in SUITS for rank in RANKS}
card_backs={"red":load_card_back("red"),"blue":load_card_back("blue")}

game_draw_pile=[]
game_waste_pile=[]
game_foundations={suit:[] for suit in SUITS}
game_tableau=[[] for _ in range(7)]
hidden_counts=[0]*7
score=0
game_timer=0.0
game_active=False
current_screen="menu"
difficulty="EASY"
drawn_amount=1
theme="red"
dragging=False
drag_cards=[]
drag_source=None
drag_offset=(0,0)
load_input_active=False
load_input_text=""
load_error=""
save_feedback=""
save_feedback_timer=0
show_win_screen=False
result_recorded=False

start_button=pygame.Rect(0,0,300,70)
difficulty_button=pygame.Rect(0,0,300,70)
stats_button=pygame.Rect(0,0,300,70)
quit_button=pygame.Rect(0,0,120,40)
back_button=pygame.Rect(0,0,120,40)
new_game_button=pygame.Rect(0,0,280,70)
load_game_button=pygame.Rect(0,0,280,70)
confirm_load_button=pygame.Rect(0,0,120,40)

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

def rank_value(rank):
    return RANKS.index(rank)

def opposite_colour(suit):
    return BLACK_SUITS if suit in RED_SUITS else RED_SUITS

def draw_text(text,fnt,colour,center=None,pos=None):
    surf=fnt.render(text,True,colour)
    rect=surf.get_rect()
    if center:
        rect.center=center
    elif pos:
        rect.topleft=pos
    screen.blit(surf,rect)
    return rect

def draw_button(rect,label,colour):
    pygame.draw.rect(screen,colour,rect)
    draw_text(label,small_font if len(label)>10 else button_font,BLACK,center=rect.center)

def draw_card(card,rect):
    if card.image:
        screen.blit(card.image,rect.topleft)
        return
    colour=RED if card.red else BLACK
    pygame.draw.rect(screen,WHITE,rect,border_radius=7)
    pygame.draw.rect(screen,GREY,rect,2,border_radius=7)
    draw_text(card.rank,card_font,colour,pos=(rect.x+8,rect.y+8))
    draw_text(SUIT_MARK[card.suit],large_card_font,colour,center=rect.center)
    bottom=card_font.render(card.rank,True,colour)
    bottom=pygame.transform.rotate(bottom,180)
    screen.blit(bottom,(rect.right-bottom.get_width()-8,rect.bottom-bottom.get_height()-8))

def draw_back(rect):
    if card_backs[theme]:
        screen.blit(card_backs[theme],rect.topleft)
        return
    base=(154,34,52) if theme=="red" else (34,76,154)
    trim=(250,225,145)
    pygame.draw.rect(screen,base,rect,border_radius=7)
    pygame.draw.rect(screen,trim,rect.inflate(-12,-12),3,border_radius=5)
    for y in range(rect.y+24,rect.bottom-22,18):
        pygame.draw.line(screen,trim,(rect.x+18,y),(rect.right-18,y),2)
    pygame.draw.rect(screen,BLACK,rect,2,border_radius=7)

def draw_placeholder(rect,label="",colour=WHITE):
    pygame.draw.rect(screen,colour,rect,2)
    if label:
        draw_text(label,small_font,colour,center=rect.center)

def deal_new_game():
    global game_draw_pile,game_waste_pile,game_foundations,game_tableau
    global hidden_counts,score,game_timer,game_active,show_win_screen,result_recorded
    deck=list(cards.values())
    random.shuffle(deck)
    game_tableau=[[] for _ in range(7)]
    hidden_counts=[0]*7
    index=0
    for pile_idx in range(7):
        for _ in range(pile_idx+1):
            game_tableau[pile_idx].append(deck[index])
            index+=1
        hidden_counts[pile_idx]=pile_idx
    game_draw_pile=deck[index:]
    game_waste_pile=[]
    game_foundations={suit: [] for suit in SUITS}
    score=0
    game_timer=0.0
    game_active=True
    show_win_screen=False
    result_recorded=False

def can_place_on_tableau(card,pile_idx):
    pile=game_tableau[pile_idx]
    if not pile:
        return card.rank=="K"
    top=pile[-1]
    return rank_value(card.rank)==rank_value(top.rank)-1 and card.suit in opposite_colour(top.suit)

def can_place_on_foundation(card,suit):
    pile=game_foundations[suit]
    if card.suit!=suit:
        return False
    if not pile:
        return card.rank=="A"
    return rank_value(card.rank)==rank_value(pile[-1].rank)+1

def reveal_source_card(source):
    global score
    if source and source[0]=="tableau":
        pile_idx=source[1]
        if game_tableau[pile_idx] and hidden_counts[pile_idx]==len(game_tableau[pile_idx]):
            hidden_counts[pile_idx]-=1
            score+=5

def check_win():
    return all(len(game_foundations[suit])==13 for suit in SUITS)

def click_draw_pile():
    global game_draw_pile,game_waste_pile,score
    if game_draw_pile:
        for _ in range(min(drawn_amount,len(game_draw_pile))):
            game_waste_pile.append(game_draw_pile.pop())
    elif game_waste_pile:
        game_draw_pile=list(reversed(game_waste_pile))
        game_waste_pile=[]
        score=max(0,score-100)

def get_tableau_card_rect(pile_idx,card_idx):
    x=TABLEAU_X+pile_idx*TABLEAU_GAP
    y=TABLEAU_Y
    for i in range(card_idx):
        y+=HIDDEN_STEP if i<hidden_counts[pile_idx] else VISIBLE_STEP
    return pygame.Rect(x,y,CARD_W,CARD_H)

def find_click_target(pos):
    if pygame.Rect(DRAW_X,TOP_CARD_Y,CARD_W,CARD_H).collidepoint(pos):
        return ("draw",)
    if pygame.Rect(WASTE_X,TOP_CARD_Y,CARD_W,CARD_H).collidepoint(pos) and game_waste_pile:
        return ("waste",)
    for i,suit in enumerate(SUITS):
        if pygame.Rect(FOUNDATION_X+i*FOUNDATION_GAP,TOP_CARD_Y,CARD_W,CARD_H).collidepoint(pos) and game_foundations[suit]:
            return ("foundation",suit)
    for pile_idx in range(6,-1,-1):
        pile=game_tableau[pile_idx]
        for card_idx in range(len(pile)-1,hidden_counts[pile_idx]-1,-1):
            rect=get_tableau_card_rect(pile_idx,card_idx)
            if card_idx<len(pile)-1:
                next_rect=get_tableau_card_rect(pile_idx,card_idx+1)
                rect=pygame.Rect(rect.x,rect.y,CARD_W,next_rect.y-rect.y)
            if rect.collidepoint(pos):
                return ("tableau",pile_idx,card_idx)
    return None

def find_drop_target(pos):
    for i,suit in enumerate(SUITS):
        if pygame.Rect(FOUNDATION_X+i*FOUNDATION_GAP,TOP_CARD_Y,CARD_W,CARD_H).collidepoint(pos):
            return ("foundation",suit)
    for pile_idx in range(7):
        if pygame.Rect(TABLEAU_X+pile_idx*TABLEAU_GAP,TABLEAU_Y,CARD_W,HEIGHT-TABLEAU_Y).collidepoint(pos):
            return ("tableau",pile_idx)
    return None

def save_game():
    global save_feedback,save_feedback_timer
    stamp_date=extract_date()
    stamp_time=extract_time()
    save_name=f"{stamp_date}_{stamp_time}"
    cursor.execute("INSERT INTO saved_games(save_name,date,time,score,timer,difficulty,draw_count) VALUES(?,?,?,?,?,?,?)",
                   (save_name,stamp_date,stamp_time,score,int(game_timer),difficulty,drawn_amount))
    conn.commit()
    save_id=cursor.lastrowid
    for pile_idx,pile in enumerate(game_tableau):
        for pos,card in enumerate(pile):
            cursor.execute("INSERT INTO playable_cards(save_id,pile,position,card,hidden) VALUES(?,?,?,?,?)",(save_id,pile_idx,pos,card.key,1 if pos<hidden_counts[pile_idx] else 0))
    for pos,card in enumerate(game_draw_pile):
        cursor.execute("INSERT INTO draw_pile(save_id,position,card) VALUES(?,?,?)",(save_id,pos,card.key))
    for pos,card in enumerate(game_waste_pile):
        cursor.execute("INSERT INTO waste_pile(save_id,position,card) VALUES(?,?,?)",(save_id,pos,card.key))
    for suit,pile in game_foundations.items():
        for pos,card in enumerate(pile):
            cursor.execute("INSERT INTO solved_piles(save_id,suit,position,card) VALUES(?,?,?,?)",(save_id, suit, pos, card.key))
    conn.commit()
    save_feedback=f"SAVED:{save_name}"
    save_feedback_timer=210

def latest_save_name():
    cursor.execute("SELECT save_name FROM saved_games ORDER BY id DESC LIMIT 1")
    row=cursor.fetchone()
    return row[0] if row else ""

def load_game(save_name):
    global game_draw_pile,game_waste_pile,game_foundations,game_tableau,hidden_counts
    global score,game_timer,game_active,difficulty,drawn_amount,show_win_screen,result_recorded
    cursor.execute("SELECT id,score,timer,difficulty,draw_count FROM saved_games WHERE save_name=?", (save_name,))
    row=cursor.fetchone()
    if not row:
        return False
    save_id,saved_score,saved_timer,saved_difficulty,saved_draw_count=row
    score=saved_score
    game_timer=float(saved_timer)
    if saved_difficulty:
        difficulty=saved_difficulty
    if saved_draw_count:
        drawn_amount=saved_draw_count
    game_tableau=[[] for _ in range(7)]
    hidden_counts=[0]*7
    cursor.execute("SELECT pile,position,card,hidden FROM playable_cards WHERE save_id=? ORDER BY pile,position", (save_id,))
    for pile_idx,_,card_key,hidden in cursor.fetchall():
        game_tableau[pile_idx].append(cards[card_key])
        if hidden:
            hidden_counts[pile_idx]+=1
    game_draw_pile=[]
    cursor.execute("SELECT card FROM draw_pile WHERE save_id=? ORDER BY position",(save_id,))
    for (card_key,) in cursor.fetchall():
        game_draw_pile.append(cards[card_key])
    game_waste_pile=[]
    cursor.execute("SELECT card FROM waste_pile WHERE save_id=? ORDER BY position",(save_id,))
    for (card_key,) in cursor.fetchall():
        game_waste_pile.append(cards[card_key])
    game_foundations={suit:[] for suit in SUITS}
    cursor.execute("SELECT suit,card FROM solved_piles WHERE save_id=? ORDER BY suit,position,rowid", (save_id,))
    for suit,card_key in cursor.fetchall():
        game_foundations[suit].append(cards[card_key])
    game_active=True
    show_win_screen=False
    result_recorded=False
    return True

def record_result(win):
    date= extract_date()
    cursor.execute("SELECT wins,loss FROM stats WHERE date=?",(date,))
    row=cursor.fetchone()
    if row:
        wins,losses=row
        if win:
            wins+=1
        else:
            losses+=1
        cursor.execute("UPDATE stats SET wins=?, loss=? WHERE date=?",(wins,losses,date))
    else:
        cursor.execute("INSERT INTO stats(date,wins,loss) VALUES(?,?,?)",(date,1 if win else 0,0 if win else 1))
    conn.commit()

def menu_page():
    screen.fill(BLACK)
    draw_text("Klondike Solitaire",title_font,GREEN_TITLE,center=(WIDTH//2,120))
    start_button.center=(WIDTH//2,280)
    difficulty_button.center=(WIDTH//2,380)
    stats_button.center=(WIDTH//2,480)
    quit_button.center=(WIDTH-90,50)
    draw_button(start_button,"START",GREEN)
    draw_button(difficulty_button,f"{difficulty}",YELLOW)
    draw_button(stats_button,"STATS",RED)
    draw_button(quit_button,"EXIT",RED)

def stats_page():
    screen.fill(BLACK)
    back_button.center=(100,50)
    draw_button(back_button,"BACK",RED)
    draw_text("STATISTICS",button_font,WHITE,center=(WIDTH//2,60))
    graph=pygame.Rect(250,140,900,540)
    pygame.draw.rect(screen,WHITE,graph)
    pygame.draw.line(screen,BLACK,(graph.x+70,graph.y+30),(graph.x+70,graph.bottom-60),3)
    pygame.draw.line(screen,BLACK, (graph.x+70,graph.bottom-60),(graph.right-30,graph.bottom-60),3)
    draw_text("Wins / Losses",tiny_font,BLACK,pos=(graph.x+10,graph.y+22))
    draw_text("Date",tiny_font,BLACK,pos=(graph.right-75,graph.bottom-38))
    key_box=pygame.Rect(graph.right-210,graph.y+18,180,72)
    pygame.draw.rect(screen,WHITE,key_box)
    draw_text("Key",tiny_font,BLACK,pos=(key_box.x+10,key_box.y+8))
    pygame.draw.circle(screen,GREEN,(key_box.x+22,key_box.y+35),7)
    draw_text("Wins",tiny_font,BLACK,pos=(key_box.x+40,key_box.y+27))
    pygame.draw.circle(screen,RED,(key_box.x+22,key_box.y+58),7)
    draw_text("Losses",tiny_font,BLACK,pos=(key_box.x+40,key_box.y+50))
    cursor.execute("SELECT date,wins,loss FROM stats ORDER BY date LIMIT 12")
    data=cursor.fetchall()
    if not data:
        draw_text("NO DATA YET",small_font,BLACK,center=graph.center)
        return
    max_val=max(1,max(max(w,l) for _,w,l in data))
    usable_h=graph.height-110
    step=(graph.width-120)//(len(data)+1)
    wins_points=[]
    loss_points=[]
    for i,(date,wins,losses) in enumerate(data):
        x=graph.x+70+step*(i+1)
        wy=graph.bottom-60-int((wins/max_val)*usable_h)
        ly=graph.bottom-60-int((losses/max_val)*usable_h)
        wins_points.append((x,wy))
        loss_points.append((x,ly))
        pygame.draw.circle(screen,GREEN,(x,wy),7)
        pygame.draw.circle(screen,RED,(x,ly),7)
        draw_text(str(wins),tiny_font,DARK_GREEN,pos=(x+8,wy-18))
        draw_text(str(losses),tiny_font,RED,pos=(x+8,ly+2))
        draw_text(date[:5],tiny_font,BLACK,center=(x,graph.bottom-35))
    if len(wins_points)>1:
        pygame.draw.lines(screen,GREEN,False,wins_points,3)
        pygame.draw.lines(screen,RED,False,loss_points,3)

def game_page():
    global save_feedback_timer
    screen.fill(GREEN_BACKGROUND)
    pygame.draw.rect(screen,BAR,(0,0,WIDTH,70))
    back_button=pygame.Rect(20,15,120,40)
    save_button=pygame.Rect(160,15,120,40)
    theme_button=pygame.Rect(300,15,160,40)
    draw_button(back_button,"BACK",RED)
    draw_button(save_button,"SAVE",BLUE)
    draw_button(theme_button,"THEME",YELLOW)
    draw_text(f"TIME:{int(game_timer)}s",small_font,WHITE,pos=(850,25))
    draw_text(f"SCORE:{score}",small_font,YELLOW,pos=(1110,25))
    if save_feedback_timer>0:
        draw_text(save_feedback,tiny_font,GREEN,pos=(475,28))
        save_feedback_timer-=1
    if not game_active:
        new_game_button.center=(WIDTH//2-180,HEIGHT//2)
        load_game_button.center=(WIDTH//2+180,HEIGHT//2)
        draw_button(new_game_button,"NEW GAME",GREEN)
        draw_button(load_game_button,"LOAD GAME",BLUE)
        recent=latest_save_name()
        if recent:
            draw_text(f"Latest save:{recent}",tiny_font,WHITE,center=(WIDTH//2,HEIGHT//2+70))
        if load_input_active:
            box=pygame.Rect(WIDTH//2-300,HEIGHT//2+110,600,50)
            pygame.draw.rect(screen,WHITE,box)
            pygame.draw.rect(screen,BLACK,box,2)
            draw_text(load_input_text,tiny_font,BLACK,pos=(box.x+10,box.y+16))
            draw_text("Enter save name, or press LOAD with latest save filled in.",tiny_font,WHITE,center=(WIDTH//2,box.y-18))
            confirm_load_button.center=(WIDTH//2,HEIGHT//2+190)
            draw_button(confirm_load_button,"LOAD",GREEN)
        if load_error:
            draw_text(load_error,small_font,RED,center=(WIDTH//2,HEIGHT//2+250))
        return
    draw_rect=pygame.Rect(DRAW_X,TOP_CARD_Y,CARD_W,CARD_H)
    waste_rect=pygame.Rect(WASTE_X,TOP_CARD_Y,CARD_W,CARD_H)
    if game_draw_pile:
        draw_back(draw_rect)
    else:
        draw_placeholder(draw_rect,"RESET")
    if game_waste_pile:
        draw_card(game_waste_pile[-1],waste_rect)
    else:
        draw_placeholder(waste_rect)
    for i, suit in enumerate(SUITS):
        rect=pygame.Rect(FOUNDATION_X+i*FOUNDATION_GAP,TOP_CARD_Y,CARD_W,CARD_H)
        if game_foundations[suit]:
            draw_card(game_foundations[suit][-1],rect)
        else:
            draw_placeholder(rect,SUIT_MARK[suit])
    for pile_idx in range(7):
        base=pygame.Rect(TABLEAU_X+pile_idx*TABLEAU_GAP,TABLEAU_Y,CARD_W,CARD_H)
        pile=game_tableau[pile_idx]
        if not pile:
            draw_placeholder(base,"K")
            continue
        for card_idx,card in enumerate(pile):
            if dragging and drag_source and drag_source[0]=="tableau" and drag_source[1]==pile_idx and card_idx>=drag_source[2]:
                continue
            rect=get_tableau_card_rect(pile_idx,card_idx)
            if card_idx<hidden_counts[pile_idx]:
                draw_back(rect)
            else:
                draw_card(card,rect)
    if dragging and drag_cards:
        mx,my=pygame.mouse.get_pos()
        ox,oy=drag_offset
        for i,card in enumerate(drag_cards):
            draw_card(card,pygame.Rect(mx-ox,my-oy+i*VISIBLE_STEP,CARD_W,CARD_H))

def win_screen():
    overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    overlay.fill((0,0,0,170))
    screen.blit(overlay,(0,0))
    draw_text("YOU WIN!",title_font,YELLOW,center=(WIDTH//2,HEIGHT//2-80))
    draw_text(f"SCORE:{score}",button_font,WHITE,center=(WIDTH//2,HEIGHT//2))
    draw_text("Press ENTER or click to continue",small_font,WHITE,center=(WIDTH//2,HEIGHT//2+80))

def remove_dragged_from_source():
    if drag_source[0]=="waste":
        game_waste_pile.pop()
    elif drag_source[0]=="foundation":
        game_foundations[drag_source[1]].pop()
    elif drag_source[0]=="tableau":
        game_tableau[drag_source[1]]=game_tableau[drag_source[1]][:drag_source[2]]

def main():
    global current_screen,difficulty,drawn_amount,theme,dragging,drag_cards,drag_source,drag_offset
    global load_input_active,load_input_text,load_error,game_timer,score,show_win_screen,game_active,result_recorded
    running=True
    while running:
        dt=clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if event.type==pygame.KEYDOWN:
                if load_input_active:
                    if event.key==pygame.K_RETURN:
                        ok=load_game(load_input_text.strip() or latest_save_name())
                        if ok:
                            load_input_active=False
                            load_input_text=""
                            load_error=""
                        else:
                            load_error="Save not found"
                    elif event.key==pygame.K_ESCAPE:
                        load_input_active=False
                    elif event.key==pygame.K_BACKSPACE:
                        load_input_text=load_input_text[:-1]
                    elif event.unicode and len(load_input_text)<40:
                        load_input_text+=event.unicode
                elif show_win_screen and event.key==pygame.K_RETURN:
                    show_win_screen=False
                    current_screen="menu"
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                mouse_pos=event.pos
                if show_win_screen:
                    show_win_screen=False
                    current_screen="menu"
                elif current_screen=="menu":
                    if start_button.collidepoint(mouse_pos):
                        current_screen="game"
                    elif difficulty_button.collidepoint(mouse_pos):
                        difficulty="HARD" if difficulty=="EASY" else "EASY"
                        drawn_amount=3 if difficulty=="HARD" else 1
                    elif stats_button.collidepoint(mouse_pos):
                        current_screen="stats"
                    elif quit_button.collidepoint(mouse_pos):
                        running=False
                elif current_screen=="stats":
                    if back_button.collidepoint(mouse_pos):
                        current_screen="menu"
                elif current_screen=="game":
                    back_btn=pygame.Rect(20,15,120,40)
                    save_btn=pygame.Rect(160,15,120,40)
                    theme_btn=pygame.Rect(300,15,160,40)
                    if back_btn.collidepoint(mouse_pos):
                        current_screen="menu"
                    elif theme_btn.collidepoint(mouse_pos):
                        theme="blue" if theme=="red" else "red"
                    elif save_btn.collidepoint(mouse_pos) and game_active:
                        save_game()
                    elif not game_active:
                        new_game_button.center=(WIDTH//2-180,HEIGHT//2)
                        load_game_button.center=(WIDTH//2+180,HEIGHT//2)
                        confirm_load_button.center=(WIDTH//2,HEIGHT//2+190)
                        if new_game_button.collidepoint(mouse_pos):
                            deal_new_game()
                        elif load_game_button.collidepoint(mouse_pos):
                            load_input_active=True
                            load_input_text=latest_save_name()
                            load_error=""
                        elif load_input_active and confirm_load_button.collidepoint(mouse_pos):
                            ok=load_game(load_input_text.strip() or latest_save_name())
                            if ok:
                                load_input_active=False
                                load_input_text=""
                                load_error=""
                            else:
                                load_error="Save not found"
                    else:
                        target=find_click_target(mouse_pos)
                        if target:
                            if target[0]=="draw":
                                click_draw_pile()
                            elif target[0]=="waste":
                                dragging=True
                                drag_cards=[game_waste_pile[-1]]
                                drag_source=("waste",)
                                drag_offset=(mouse_pos[0]-WASTE_X,mouse_pos[1]-TOP_CARD_Y)
                            elif target[0]=="foundation":
                                suit=target[1]
                                dragging=True
                                drag_cards=[game_foundations[suit][-1]]
                                drag_source=("foundation", suit)
                                index=SUITS.index(suit)
                                drag_offset=(mouse_pos[0]-(FOUNDATION_X+index*FOUNDATION_GAP), mouse_pos[1] - TOP_CARD_Y)
                            elif target[0]=="tableau":
                                pile_idx,card_idx=target[1],target[2]
                                pile=game_tableau[pile_idx]
                                if card_idx>=hidden_counts[pile_idx]:
                                    dragging=True
                                    drag_cards=list(pile[card_idx:])
                                    drag_source=("tableau",pile_idx,card_idx)
                                    rect=get_tableau_card_rect(pile_idx,card_idx)
                                    drag_offset=(mouse_pos[0]-rect.x,mouse_pos[1]-rect.y)
            if event.type==pygame.MOUSEBUTTONUP and event.button==1 and dragging:
                mouse_pos=event.pos
                drop=find_drop_target(mouse_pos)
                moved=False
                if drop and drag_cards:
                    top_card=drag_cards[0]
                    if drop[0]=="foundation" and len(drag_cards)==1 and can_place_on_foundation(top_card,drop[1]):
                        remove_dragged_from_source()
                        game_foundations[drop[1]].append(top_card)
                        score+=15
                        moved=True
                    elif drop[0]=="tableau" and can_place_on_tableau(top_card,drop[1]):
                        remove_dragged_from_source()
                        game_tableau[drop[1]].extend(drag_cards)
                        score+=5
                        moved=True
                if not moved and len(drag_cards)==1 and can_place_on_foundation(drag_cards[0],drag_cards[0].suit):
                    top_card=drag_cards[0]
                    remove_dragged_from_source()
                    game_foundations[top_card.suit].append(top_card)
                    score+=15
                    moved=True
                if moved:
                    reveal_source_card(drag_source)
                dragging=False
                drag_cards=[]
                drag_source=None
                if check_win() and not result_recorded:
                    score+=500
                    record_result(True)
                    result_recorded=True
                    show_win_screen=True
                    game_active=False
        if current_screen=="game" and game_active and not show_win_screen:
            game_timer+=dt
        if current_screen=="menu":
            menu_page()
        elif current_screen=="stats":
            stats_page()
        elif current_screen=="game":
            game_page()
            if show_win_screen:
                win_screen()
        pygame.display.flip()
    pygame.quit()
    conn.close()
    sys.exit()
if __name__=="__main__":
    main()
    clock.tick(60)
pygame.quit()
conn.close()
sys.exit()
