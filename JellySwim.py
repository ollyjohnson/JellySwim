import pygame
import neat
import time
import os
import random

pygame.init()

WIN_WIDTH = 800
WIN_HEIGHT = 800
  
# Load the images of the jellyfish jumping
JELLY_IMGS = []
for i in range(12):
    if i < 10:
        image_path = os.path.join("assets", "jellyjump", f"attack__00{i}.png")
    else:
        image_path = os.path.join("assets", "jellyjump", f"attack__0{i}.png")

    image = pygame.image.load(image_path)
    scaled_image = pygame.transform.scale(image, (100, 100))
    rotated_image = pygame.transform.rotate(scaled_image, 330)
    JELLY_IMGS.append(rotated_image)

flipped_anchor = pygame.transform.flip(pygame.image.load(os.path.join("assets", "Grappling Hook.png")), False, True)
ANCHOR_IMG = pygame.transform.scale(flipped_anchor, (200, 400))
scaled_cannon = pygame.transform.scale(pygame.image.load(os.path.join("assets", "cartcannon2.png")), (350, 200))
CANNON_IMG = pygame.transform.rotate(scaled_cannon, 280)
BASE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "sand.jpg")), (WIN_WIDTH, int(WIN_HEIGHT / 4)))
BG_IMG = pygame.image.load(os.path.join("assets", "bg", "sea_background.png"))
FG_IMG = pygame.image.load(os.path.join("assets", "bg", "mid_background.png"))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Fish:
    IMGS = JELLY_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 4

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        self.animation_index = 0

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        if d >= 16:
            d = 16
        if d < 0:
            d -= 2

        self.y += d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count >= self.ANIMATION_TIME:
            self.img_count = 0
            self.animation_index += 1

            if self.animation_index >= len(self.IMGS):
                self.animation_index = 0

        self.img = self.IMGS[self.animation_index]
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = ANCHOR_IMG
        self.PIPE_BOTTOM = CANNON_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(100, 200)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, fish):
        fish_mask = fish.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - fish.x, self.top - round(fish.y))
        bottom_offset = (self.x - fish.x, self.bottom - round(fish.y))

        b_point = fish_mask.overlap(bottom_mask, bottom_offset)
        t_point = fish_mask.overlap(top_mask, top_offset)

        return t_point or b_point

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, fish, pipes, base, score):
    win.blit(BG_IMG, (0, 0))
    win.blit(FG_IMG, (0, -100))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)
    fish.draw(win)
    pygame.display.update()

def main():
    fish = Fish(230, 350)
    base = Base(650)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fish.jump()  # Make the fish jump when spacebar is pressed

        fish.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(fish):
                run = False  # End the game if the fish hits a pipe

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < fish.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(700))

        for r in rem:
            pipes.remove(r)

        # End the game if the fish hits the ground or goes above the screen
        if fish.y + fish.img.get_height() >= base.y or fish.y < 0:
            run = False

        base.move()
        draw_window(win, fish, pipes, base, score)

    pygame.quit()
    quit()
 
main()