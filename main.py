import pygame
import threading
import time
from queue import Queue
from player import Player
from meteor import Meteor
from explosion import Explosion

WIDTH = 800
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter Concurrente")
clock = pygame.time.Clock()

# Funciones auxiliares
def draw_text(surface, text, size, x, y):
    font = pygame.font.SysFont("serif", size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def draw_shield_bar(surface, x, y, percentage):
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (percentage / 100) * BAR_LENGTH
    border = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill)
    pygame.draw.rect(surface, WHITE, border, 2)

# Función para mostrar la pantalla de inicio
def show_go_screen():
    screen.blit(background, [0, 0])
    draw_text(screen, "SHOOTER CONCURRENTE", 65, WIDTH // 2, HEIGHT // 4)
    draw_text(screen, "Diviértete (^^)", 27, WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Presiona una tecla para comenzar", 20, WIDTH // 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

# Inicializaciones
meteor_images = []
meteor_list = ["assets/meteorGrey_big1.png", "assets/meteorGrey_big2.png", "assets/meteorGrey_big3.png",
               "assets/meteorGrey_big4.png",
               "assets/meteorGrey_med1.png", "assets/meteorGrey_med2.png", "assets/meteorGrey_small1.png",
               "assets/meteorGrey_small2.png",
               "assets/meteorGrey_tiny1.png", "assets/meteorGrey_tiny2.png"]

for img in meteor_list:
    meteor_images.append(pygame.image.load(img).convert())

explosion_anim = []
for i in range(9):
    file = "assets/regularExplosion0{}.png".format(i)
    img = pygame.image.load(file).convert()
    img.set_colorkey(BLACK)
    img_scale = pygame.transform.scale(img, (70, 70))
    explosion_anim.append(img_scale)

background = pygame.image.load("assets/background.png").convert()

laser_sound = pygame.mixer.Sound("assets/laser5.ogg")
explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
# game_sound = pygame.mixer.Sound("assets/game.ogg")
pygame.mixer.music.load("assets/music.ogg")
pygame.mixer.music.set_volume(10)
pygame.mixer.music.play(-1)


# Variables globales
all_sprites = pygame.sprite.Group()
meteor_list = pygame.sprite.Group()
bullets = pygame.sprite.Group()
running = True
score = 0
game_over = True
sprite_semaphore = threading.Semaphore()
shoot_event = threading.Event()

# Barrera para esperar la carga de recursos
resources_barrier = threading.Barrier(2)

# Barreras para coordinar los hilos
background_barrier = threading.Barrier(3)
front_plain_barrier = threading.Barrier(11)

# Cola para comunicación entre hilos
queue = Queue()

# Semáforos para controlar acceso concurrente a recursos compartidos
meteor_semaphore = threading.Semaphore()
bullet_semaphore = threading.Semaphore()

# Eventos para coordinar acciones
meteor_creation_event = threading.Event()
shoot_done_event = threading.Event()


# Hilo para los meteoros
def meteor_thread():
    global running
    resources_barrier.wait()  # Esperar a que los recursos estén cargados
    while running:
        meteor_creation_event.wait()
        meteor_creation_event.clear()
        meteor_semaphore.acquire()
        time.sleep(1)
        meteor = Meteor(WIDTH, HEIGHT, BLACK)  # Pasa las dimensiones de la pantalla y el color clave al meteorito
        queue.put(("meteor", meteor))
        meteor_semaphore.release()


# Iniciar los hilos de meteoros en background
for _ in range(2):
    threading.Thread(target=meteor_thread).start()


# Hilo para manejar el evento de disparo
def handle_shoot_event():
    while running:
        shoot_event.wait()
        shoot_event.clear()
        bullet_semaphore.acquire()
        queue.put(("shoot", None, sprite_semaphore, all_sprites, bullets, shoot_event))
        bullet_semaphore.release()
        shoot_done_event.set()


# Iniciar el hilo para manejar el evento de disparo
threading.Thread(target=handle_shoot_event).start()

# Bucle principal del juego
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        meteor_list = pygame.sprite.Group()
        bullets = pygame.sprite.Group()

        player = Player(WIDTH, HEIGHT, BLACK)  # Pasa las dimensiones de la pantalla y el color clave al jugador
        all_sprites.add(player)

        for i in range(8):
            meteor_creation_event.set()
            meteor_semaphore.acquire()
            meteor = Meteor(WIDTH, HEIGHT, BLACK)  # Pasa las dimensiones de la pantalla y el color clave al meteorito
            all_sprites.add(meteor)
            meteor_list.add(meteor)
            meteor_semaphore.release()

        score = 0

    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot(sprite_semaphore, all_sprites, bullets, shoot_event, laser_sound)
                shoot_done_event.wait()
                shoot_done_event.clear()

    # Procesar eventos desde la cola
    while not queue.empty():
        data = queue.get()
        event_type = data[0]
        if event_type == "meteor":
            meteor = data[1]
            all_sprites.add(meteor)
            meteor_list.add(meteor)

    all_sprites.update()

    hits = pygame.sprite.groupcollide(meteor_list, bullets, True, True)
    for hit in hits:
        score += 10
        explosion = Explosion(explosion_anim, hit.rect.center, explosion_sound)
        all_sprites.add(explosion)
        meteor_creation_event.set()

    hits = pygame.sprite.spritecollide(player, meteor_list, True)
    for hit in hits:
        player.shield -= 25
        meteor_creation_event.set()
        if player.shield <= 0:
            game_over = True

    screen.blit(background, [0, 0])
    all_sprites.draw(screen)

    draw_text(screen, str(score), 25, WIDTH // 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)

    pygame.display.flip()

pygame.quit()
