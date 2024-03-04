import pygame
from bullet import Bullet
import threading

# Crea la condicion
condition = threading.Condition()

class Player(pygame.sprite.Sprite):
    def __init__(self, width, height, colorkey):
        super().__init__()
        self.image = pygame.image.load("assets/player.png").convert()
        self.image.set_colorkey(colorkey)
        self.rect = self.image.get_rect()
        self.rect.centerx = width // 2
        self.rect.bottom = height - 10
        self.speed_x = 0
        self.shield = 100
        self.width = width
        self.height = height
        
    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.right > self.width:
            self.rect.right = self.width
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self, sprite_semaphore, all_sprites, bullets, shoot_event, laser_sound):
        bullet = Bullet(self.rect.centerx, self.rect.top, laser_sound)
        sprite_semaphore.acquire()
        all_sprites.add(bullet)
        bullets.add(bullet)
        sprite_semaphore.release()
        shoot_event.set()

        # Notificar eventos
        condition.acquire()
        condition.notify_all()
        condition.release()
