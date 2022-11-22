import pygame
import os
import time
import random
import main
import cv2
import mediapipe as mp

def f():
    xx, yy=0, 0
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(imgRGB)

    # print(result.multi_hand_landmarks)
    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id,cx, cy)

                if id == 8:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
                    xx, yy=cx, cy

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)




    cv2.imshow("Image", img)
    cv2.waitKey(1)
    print(xx, yy)
    return xx, yy

cap=cv2.VideoCapture(0)
mpHands=mp.solutions.hands
hands=mpHands.Hands()
mpDraw=mp.solutions.drawing_utils






pygame.font.init()

WIDTH, HEIGHT =  cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

SPACESHIP_RED = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))                               ###############
SPACESHIP_GREEN = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))                           # enemy ships #
SPACESHIP_BLUE = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))                             ###############

SPACESHIP_YELLOW = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))                               #   player ship #

LASER_RED = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))                                        #########################
LASER_GREEN = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))                                    #   lasers              #
LASER_BLUE = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))                                      #   (pew pew)           #
LASER_YELLOW = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))                                  #########################

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))     #   background (obviously)  #

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y < height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)

class Ship:
    COOLDOWN = 240
    def __init__(self, x, y, health = 3):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 1

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 1
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0: 
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

class Player(Ship):
    def __init__(self, x, y, health = 3):
        super().__init__(x, y, health)
        self.ship_img = SPACESHIP_YELLOW
        self.laser_img = LASER_YELLOW
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

class Enemy(Ship):
    COLOR_MAP = {
        "red" : (SPACESHIP_RED, LASER_RED),
        "green" : (SPACESHIP_GREEN, LASER_GREEN),
        "blue": (SPACESHIP_BLUE, LASER_BLUE)
    }
    def __init__(self, x, y, color, health = 1):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self, vel):
        self.y += vel

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 30
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans", 20)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player = Player(350,350)

    laser_vel = 1

    lost = False
    lost_count = 0

    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BG, (0,0))
        #draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,0,0))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,0))
        
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH-level_label.get_width() - 10, 10))

        if lost:
            lost_label = lost_font.render("Game Over", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        cx, cy=f()
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
       

        player.shoot()



        if 0 < cx - player.get_width()/2 and cx + player.get_width()/2 < WIDTH:
            player.x = cx - player.get_height()/2
        if 0 < cy - player.get_height()/2 and cy + player.get_height()/2 < HEIGHT:
            player.y = cy - player.get_width()/2

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
            
            player.move_lasers(-laser_vel, enemies)
main()
