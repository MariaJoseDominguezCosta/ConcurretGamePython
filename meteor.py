import pygame
import random

class Meteor(pygame.sprite.Sprite):
    def __init__(self, width, height, BLACK):
        super().__init__()
        self.meteor_images = ["assets/meteorGrey_big1.png", "assets/meteorGrey_big2.png", "assets/meteorGrey_big3.png",
                              "assets/meteorGrey_big4.png",
                              "assets/meteorGrey_med1.png", "assets/meteorGrey_med2.png", "assets/meteorGrey_small1.png",
                              "assets/meteorGrey_small2.png",
                              "assets/meteorGrey_tiny1.png", "assets/meteorGrey_tiny2.png"]
        self.image = pygame.image.load(random.choice(self.meteor_images)).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(-140, -100)
        self.speedy = random.randrange(1, 10)
        self.speedx = random.randrange(-5, 5)
        self.width = width
        self.height = height

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > self.height + 10 or self.rect.left < -40 or self.rect.right > self.width + 40:
            self.rect.x = random.randrange(self.width - self.rect.width)
            self.rect.y = random.randrange(-140, -100)
            self.speedy = random.randrange(1, 10)
