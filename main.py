import pygame
import sys
from os import path

# Configurações do jogo
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
BACKGROUND_COLOR = (0, 0, 0)
GRAVITY = 0.5
JUMP_STRENGTH = 10
PLAYER_SPEED = 5
FONT_COLOR = (255, 255, 255)
FONT_SIZE = 36
MOVING_PLATFORM_SPEED = 2

# Estabelece a pasta que contém as figuras.
img_dir = path.join(path.dirname(__file__), 'img')

# Define estados possíveis do jogador
STILL = 0
WALKING = 1
JUMPING = 2

def load_spritesheet(spritesheet, rows, columns):
    sprite_width = spritesheet.get_width() // columns
    sprite_height = spritesheet.get_height() // rows
    sprites = []
    for row in range(rows):
        for column in range(columns):
            x = column * sprite_width
            y = row * sprite_height
            dest_rect = pygame.Rect(x, y, sprite_width, sprite_height)
            image = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
            image.blit(spritesheet, (0, 0), dest_rect)
            sprites.append(image)
    return sprites

class Player(pygame.sprite.Sprite):
    def __init__(self, player_sheet):
        super().__init__()
        player_sheet = pygame.transform.scale(player_sheet, (192, 192))  # Supondo que o sprite sheet original seja 48x48 e tenha 4x4 sprites
        spritesheet = load_spritesheet(player_sheet, 4, 4)
        self.animations = {
            STILL: spritesheet[0:4],
            WALKING: spritesheet[4:7],
            JUMPING: spritesheet[7:8],
        }
        self.state = STILL
        self.animation = self.animations[self.state]
        self.frame = 0
        self.image = self.animation[self.frame]
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT
        self.velocity_y = 0
        self.on_ground = False
        self.last_update = pygame.time.get_ticks()
        self.frame_ticks = 300
        self.facing_right = True

    def update(self, keys_pressed):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
            self.state = WALKING
            self.facing_right = False
        elif keys_pressed[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
            self.state = WALKING
            self.facing_right = True
        else:
            self.state = STILL

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.on_ground = True

        now = pygame.time.get_ticks()
        elapsed_ticks = now - self.last_update
        if elapsed_ticks > self.frame_ticks:
            self.last_update = now
            self.frame += 1
            self.animation = self.animations[self.state]
            if self.frame >= len(self.animation):
                self.frame = 0
            center = self.rect.center
            self.image = self.animation[self.frame]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect()
            self.rect.center = center

    def jump(self):
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH
            self.on_ground = False
            self.state = JUMPING

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(0, 255, 0)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, color=(255, 0, 0)):
        super().__init__(x, y, width, height, color)
        self.direction = 1

    def update(self):
        self.rect.x += MOVING_PLATFORM_SPEED * self.direction
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

def draw_text(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple 2D Mario-style Game")

    font = pygame.font.Font(None, FONT_SIZE)

    player_sheet = pygame.image.load(path.join(img_dir, 'hero.png')).convert_alpha()
    player = Player(player_sheet)
    platforms = pygame.sprite.Group()
    moving_platforms = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    platforms.add(Platform(100, 500, 200, 10))
    platforms.add(Platform(400, 400, 200, 10))
    platforms.add(Platform(200, 300, 200, 10))
    moving_platforms.add(MovingPlatform(100, 100, 100, 10))

    for platform in platforms:
        all_sprites.add(platform)
    for moving_platform in moving_platforms:
        all_sprites.add(moving_platform)

    clock = pygame.time.Clock()
    score = 0
    running = True

    while running:
        keys_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        player.update(keys_pressed)
        moving_platforms.update()

        collisions = pygame.sprite.spritecollide(player, platforms, False)
        if collisions:
            player.rect.bottom = collisions[0].rect.top
            player.velocity_y = 0
            player.on_ground = True

        moving_collisions = pygame.sprite.spritecollide(player, moving_platforms, False)
        if moving_collisions:
            player.rect.bottom = moving_collisions[0].rect.top
            player.velocity_y = 0
            player.on_ground = True
            player.rect.x += MOVING_PLATFORM_SPEED * moving_collisions[0].direction

        score += 1
        screen.fill(BACKGROUND_COLOR)
        all_sprites.draw(screen)
        draw_text(screen, f"Score: {score}", font, FONT_COLOR, 10, 10)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
