import pygame
import sys

pygame.init()
size=(800,600)
width,height=size
screen=pygame.display.set_mode((size))
pygame.display.set_caption('Klondike Solitaire')

BLACK=(0,0,0)
GREEN_title=(35,124,17)

font=pygame.font.Font('PressStart2P-Regular.ttf',32)
text=font.render('Klondike Solitaire',True,GREEN_title)
text_rec=text.get_rect(center=(width//2,50))

running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    screen.fill(BLACK)
    screen.blit(text,text_rec)
    pygame.display.flip()

pygame.quit()
sys.exit()
