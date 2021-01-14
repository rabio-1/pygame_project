import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()
size = width, height = 480, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Shoot!')
clock = pygame.time.Clock()
FPS = 50
cont = 0
POWERUP_TIME = 3000
global running


def load_image(name, colorkey=None):
    fullname = 'data\\' + name
    # если на диске не найден файл fullname
    if not os.path.isfile(fullname):
        print(f'Файл с именем {fullname} не найден')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (100, 50))
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = width / 2
        self.rect.bottom = height - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = width / 2
            self.rect.bottom = height - 10

        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound_ult.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (width / 2, height + 200)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 5)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > height + 10 or self.rect.left < -25 or self.rect.right > width + 20:
            self.rect.x = random.randrange(width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        # убить, если он сдвинется с нижней части экрана
        if self.rect.top > height:
            self.kill()


background = load_image('fon1.png')
background_rect = background.get_rect()
player_img = load_image('space_ship.png')
meteor_images = []
meteor_list = ['met1.png', 'met2.png',
               'met3.png', 'met5.png',
               's1.png', 's2.png',
               's3.png']
for imge in meteor_list:
    meteor_images.append(load_image(imge))

bullet_img = load_image('bullet1.png')
font_name = pygame.font.match_font('arial')
powerup_images = {'shield': load_image('shield_gold.png'), 'gun': load_image('bolt_gold.png')}

shoot_sound = pygame.mixer.Sound('laser_sound2.mp3')
shoot_sound.set_volume(0.2)
shoot_sound_ult = pygame.mixer.Sound('laser_sound1.mp3')
shoot_sound_ult.set_volume(0.2)
pygame.mixer.music.load('fon_music.mp3')
pygame.mixer.music.set_volume(0.3)
# Параметр loops определяет, как часто трек будет повторяться. Если установить значение на -1,
# то он будет воспроизводиться бесконечно.
pygame.mixer.music.play(loops=-1)

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = Player()
all_sprites.add(player)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


for i in range(8):
    newmob()
score = 0


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    br = 100
    b_height = 10
    fill = (pct / 100) * br
    outline_rect = pygame.Rect(x, y, br, b_height)
    fill_rect = pygame.Rect(x, y, fill, b_height)
    pygame.draw.rect(surf, pygame.Color('green'), fill_rect)
    pygame.draw.rect(surf, width, outline_rect, 2)


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, (255, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_lives(surf, x, y, lives, img):
    for u in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * u
        img_rect.y = y
        surf.blit(img, img_rect)


def terminate():  # завершение работы
    screen.blit(background, background_rect)
    draw_text(screen, "GAME OVER!", 85, width / 2, height / 3)
    draw_text(screen, f"""Your score: {score}""", 50, width / 2, height / 2)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for o in pygame.event.get():
            if o.type == pygame.QUIT:
                waiting = False
    if not waiting:
        pygame.quit()


def start_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "Shoot!", 64, width / 2, height / 4)
    draw_text(screen, "Перемещение - (<- ; ->)", 22,
              width / 2, height / 2)
    draw_text(screen, "Стрельба - (space)", 18, width / 2, height * 3 / 4)
    pygame.display.flip()
    while True:
        for t in pygame.event.get():
            if t.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif t.type == pygame.KEYDOWN or \
                    t.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


start_screen()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    all_sprites.update()

    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50
        if random.random() > 0.9:
            pows = Pow(hit.rect.center)
            all_sprites.add(pows)
            powerups.add(pows)
        newmob()

    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= 20
        newmob()
        if player.shield <= 0:
            running = False

    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()

    screen.fill(pygame.Color('black'))

    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, width / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    pygame.display.flip()
    clock.tick(FPS)
if not running:
    terminate()
