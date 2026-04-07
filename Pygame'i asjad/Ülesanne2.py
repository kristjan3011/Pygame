import pygame
import sys
import math

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

#2.1 pildid
logo = pygame.image.load("VIKK_logo.png")
logo = pygame.transform.smoothscale(logo, (280, 70))#logo

mook = pygame.image.load("mõõk.png")
mook = pygame.transform.smoothscale(mook, (120, 160))#mõõk

tort = pygame.image.load("tort.png")
tort = pygame.transform.smoothscale(tort, (120, 120))
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

    #logo
    screen.blit(logo, (25, 10))

    #kaare tekst
    font3 = pygame.font.SysFont("arial", 22, bold=True)
    tekst_kaar = "0502 KIVELUT" #0502 KIVELUT, TULEVIK 2050

    # kaare seadistus
    center_x, center_y = 120, 5  # kaare keskpunkt
    radius = 100  # kaare raadius
    algus_nurk = 0.8  # kust kaar algab (radiaanides)

    for i, tahl in enumerate(tekst_kaar):
        nurk = algus_nurk + i * 0.13  # tähtede vahekaugus
        x = center_x + radius * math.cos(nurk)
        y = center_y + radius * math.sin(nurk)

        tahl_surf = font3.render(tahl, True, (0, 150, 200))  #sinakas värvus
        tahl_surf = pygame.transform.rotate(tahl_surf, -math.degrees(nurk) + 90)

        rect = tahl_surf.get_rect(center=(x, y))
        screen.blit(tahl_surf, rect)

    #mõõk
    screen.blit(mook, (510, 140))

    #tort
    screen.blit(tort, (400, 200))
    pygame.display.flip()