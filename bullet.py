import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, laser_sound):
        super().__init__()
        self.image = pygame.image.load("assets/laser1.png")
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.centerx = x
        self.speedy = -10
        self.laser_sound = pygame.mixer.Sound.play(laser_sound)

    def update(self):
        self.rect.y += self.speedy
        self.laser_sound
        if self.rect.bottom < 0:
            self.kill()
