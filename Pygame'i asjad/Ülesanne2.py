import pygame
import sys

pygame.init()

#ekraani seadistus
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Ülesanne 2")
#pildid ja skaleerimine
bg = pygame.image.load("bg_shop.jpg")
bg = pygame.transform.smoothscale(bg, (640, 480))#taust

seller = pygame.image.load("seller.png")
seller = pygame.transform.smoothscale(seller, (260, 310))#müüja

chat = pygame.image.load("chat.png")
chat = pygame.transform.smoothscale(chat, (252, 200))#jutumull

#teksti seadistus
font = pygame.font.SysFont("arial", 28) # fondi valikud on: times_new_roman, calibri, comic_sans
text = font.render("Tere, olen Kristjan", True, (255, 255, 255))

#põhiloop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    #taust
    screen.blit(bg, (0, 0))

    #poemüüja
    screen.blit(seller, (105, 155))

    #jutumull
    screen.blit(chat, (250, 65))

    #tekst jutumulli sisse
    screen.blit(text, (280, 145))

    pygame.display.flip()