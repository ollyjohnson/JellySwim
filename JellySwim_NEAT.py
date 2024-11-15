import neat.config
import pygame
import neat
import time
import os
import random

pygame.init()

WIN_WIDTH = 800
WIN_HEIGHT = 800

#Loads the images of the jellyfish jumping
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
ANCHOR_IMG = pygame.transform.scale(flipped_anchor,(200,400))
scaled_cannon = pygame.transform.scale(pygame.image.load(os.path.join("assets", "cartcannon2.png")),(350,200))
CANNON_IMG = pygame.transform.rotate(scaled_cannon, 280)
BASE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "sand.jpg")), (WIN_WIDTH, (WIN_HEIGHT/4)))
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

        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d = 16
        if d < 0:
            d -= 2
        
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self,win):
        self.img_count += 1

        if self.img_count >= self.ANIMATION_TIME:
            self.img_count = 0
            self.animation_index += 1

            if self.animation_index >= len(self.IMGS):
                self.animation_index = 0
        
        self.img = self.IMGS[self.animation_index]
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self,x):
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
        self.height = random.randrange(100,200)
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
        bottom_mask = pygame.mask.from_surface(self.PIPE_TOP)

        top_offset = (self.x - fish.x, self.top - round(fish.y))
        bottom_offset = (self.x - fish.x, self.bottom - round(fish.y))

        b_point = fish_mask.overlap(bottom_mask, bottom_offset)
        t_point = fish_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        
        return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self,y):
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


def draw_window(win, fishes, pipes, base, score):
    win.blit(BG_IMG, (0,0))
    win.blit(FG_IMG, (0,-100))

    for pipe in pipes:
        pipe.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1,(255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    for fish in fishes:
        fish.draw(win)
    pygame.display.update()

def main(genomes, config):
    nets = []
    ge = []
    fishes = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        fishes.append(Fish(230,350))
        g.fitness = 0
        ge.append(g)

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
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(fishes) > 0:
            if len(pipes) > 1 and fishes[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break
        
        for x, fish in enumerate(fishes):
            fish.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((fish.y, abs(fish.y-pipes[pipe_ind].height), abs(fish.y-pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                fish.jump()

        #fish.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, fish in enumerate(fishes):
                if pipe.collide(fish):
                    #lowers the fitness when a fish hits an obstacle to train the model to avoid obstacles
                    ge[x].fitness -= 1
                    fishes.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < fish.x:
                    pipe.passed = True
                    add_pipe = True
                
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(700))
        
        for r in rem:
            pipes.remove(r)
        
        for x, fish in enumerate(fishes):
            if fish.y + fish.img.get_height() >= 650 or fish.y < 0:
                fishes.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, fishes, pipes, base, score)         


def run(config_path):
    #load the configuration
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    #set a population
    p = neat.Population(config)

    #set the output
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    #set the fitness function that we will run for the specified number of generations
    winner = p.run(main,50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)