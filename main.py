import pygame
import sys

# Configurações do jogo
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_COLOR = (0, 178, 200)
PLATFORM_COLOR = (0, 255, 0)
MOVING_PLATFORM_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)
GRAVITY = 0.5
JUMP_STRENGTH = 10
PLAYER_SPEED = 5
FONT_COLOR = (255, 255, 255)
FONT_SIZE = 36
MOVING_PLATFORM_SPEED = 2

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT
        self.velocity_y = 0
        self.on_ground = False

    def update(self, keys_pressed):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH
            self.on_ground = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=PLATFORM_COLOR):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, color=MOVING_PLATFORM_COLOR):
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

    player = Player()
    platforms = pygame.sprite.Group()
    moving_platforms = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    # Adicionar plataformas
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

        # Checar colisões
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

        # Atualizar pontuação
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
