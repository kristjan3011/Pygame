import pygame
import sys

pygame.init()

# Ekraani seadistus
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
font = pygame.font.SysFont("arial", 28)
text = font.render("Tere, olen Kristjan", True, (255, 255, 255))

# Põhiloop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Taust
    screen.blit(bg, (0, 0))

    # Poemüüja
    screen.blit(seller, (105, 155))

    # Jutumull
    screen.blit(chat, (250, 65))

    # Tekst jutumulli sisse
    screen.blit(text, (290, 145))

    pygame.display.flip()