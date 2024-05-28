import pygame
import sys
import random
from os import path

# Configurações do jogo
LARGURA_TELA = 800
ALTURA_TELA = 540
LARGURA_JOGADOR = 50
ALTURA_JOGADOR = 50
COR_FUNDO = (0, 0, 0)
GRAVIDADE = 0.5
FORCA_PULO = 10
VELOCIDADE_JOGADOR = 5
COR_TEXTO = (255, 255, 255)
TAMANHO_FONTE = 36
VELOCIDADE_PLATAFORMA_MOVEL = 2

# Estabelece a pasta que contém as figuras.
diretorio_img = path.join(path.dirname(__file__), 'img')

# Define estados possíveis do jogador
PARADO = 0
ANDANDO = 1
PULANDO = 2

def carregar_spritesheet(spritesheet, linhas, colunas):
    largura_sprite = spritesheet.get_width() // colunas
    altura_sprite = spritesheet.get_height() // linhas
    sprites = []
    for linha in range(linhas):
        for coluna in range(colunas):
            x = coluna * largura_sprite
            y = linha * altura_sprite
            dest_rect = pygame.Rect(x, y, largura_sprite, altura_sprite)
            imagem = pygame.Surface((largura_sprite, altura_sprite), pygame.SRCALPHA)
            imagem.blit(spritesheet, (0, 0), dest_rect)
            sprites.append(imagem)
    return sprites

class Jogador(pygame.sprite.Sprite):
    def __init__(self, spritesheet_jogador):
        super().__init__()
        spritesheet_jogador = pygame.transform.scale(spritesheet_jogador, (192, 192))  # Supondo que o sprite sheet original seja 48x48 e tenha 4x4 sprites
        spritesheet = carregar_spritesheet(spritesheet_jogador, 4, 4)
        self.animacoes = {
            PARADO: spritesheet[0:4],
            ANDANDO: spritesheet[4:7],
            PULANDO: spritesheet[7:8],
        }
        self.estado = PARADO
        self.animacao = self.animacoes[self.estado]
        self.quadro = 0
        self.image = self.animacao[self.quadro]
        self.rect = self.image.get_rect()
        self.rect.x = LARGURA_TELA // 2
        self.rect.y = ALTURA_TELA - ALTURA_JOGADOR
        self.velocidade_y = 0
        self.no_chao = False
        self.ultimo_update = pygame.time.get_ticks()
        self.intervalo_quadros = 300
        self.direcao_direita = True

    def atualizar(self, teclas_pressionadas):
        self.velocidade_y += GRAVIDADE
        self.rect.y += self.velocidade_y

        if teclas_pressionadas[pygame.K_LEFT]:
            self.rect.x -= VELOCIDADE_JOGADOR
            self.estado = ANDANDO
            self.direcao_direita = False
        elif teclas_pressionadas[pygame.K_RIGHT]:
            self.rect.x += VELOCIDADE_JOGADOR
            self.estado = ANDANDO
            self.direcao_direita = True
        else:
            self.estado = PARADO

        if self.rect.bottom >= ALTURA_TELA:
            self.rect.bottom = ALTURA_TELA
            self.velocidade_y = 0
            self.no_chao = True

        agora = pygame.time.get_ticks()
        tempo_decorrido = agora - self.ultimo_update
        if tempo_decorrido > self.intervalo_quadros:
            self.ultimo_update = agora
            self.quadro += 1
            self.animacao = self.animacoes[self.estado]
            if self.quadro >= len(self.animacao):
                self.quadro = 0
            centro = self.rect.center
            self.image = self.animacao[self.quadro]
            if not self.direcao_direita:
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect()
            self.rect.center = centro

    def pular(self):
        if self.no_chao:
            self.velocidade_y = -FORCA_PULO
            self.no_chao = False
            self.estado = PULANDO

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura, cor=(0, 255, 0)):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(cor)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class PlataformaMovel(Plataforma):
    def __init__(self, x, y, largura, altura, cor=(0 , 255 , 0)):
        super().__init__(x, y, largura, altura, cor)
        self.direcao = 1

    def atualizar(self):
        self.rect.x += VELOCIDADE_PLATAFORMA_MOVEL * self.direcao
        if self.rect.right >= LARGURA_TELA or self.rect.left <= 0:
            self.direcao *= -1

class ZonaPerigosa(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura, cor=(255, 0, 0)):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(cor)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def desenhar_texto(tela, texto, fonte, cor, x, y):
    superficie_texto = fonte.render(texto, True, cor)
    rect_texto = superficie_texto.get_rect()
    rect_texto.topleft = (x, y)
    tela.blit(superficie_texto, rect_texto)

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Jogo Plataforma")

    fonte = pygame.font.Font(None, TAMANHO_FONTE)

    # Carregar imagem de fundo
    fundo = pygame.image.load(path.join(diretorio_img, 'background.jpg')).convert()

    spritesheet_jogador = pygame.image.load(path.join(diretorio_img, 'hero.png')).convert_alpha()
    jogador = Jogador(spritesheet_jogador)
    todos_sprites = pygame.sprite.Group()
    todos_sprites.add(jogador)

    plataformas = pygame.sprite.Group()
    plataformas_moveis = pygame.sprite.Group()
    zonas_perigosas = pygame.sprite.Group()

    # Adiciona plataformas iniciais
    plataformas.add(Plataforma(100, 500, 200, 10))
    plataformas.add(Plataforma(400, 400, 200, 10))
    plataformas.add(Plataforma(200, 300, 200, 10))
    plataformas_moveis.add(PlataformaMovel(100, 100, 100, 10))
    zonas_perigosas.add(ZonaPerigosa(200, 450, 50, 40))
    zonas_perigosas.add(ZonaPerigosa(470, 350, 50, 40))
    zonas_perigosas.add(ZonaPerigosa(250, 250, 50, 40))
    plataformas_moveis.add(PlataformaMovel(400, 200, 210, 10))  # Adicionando plataforma móvel

    for plataforma in plataformas:
        todos_sprites.add(plataforma)
    for plataforma_movel in plataformas_moveis:
        todos_sprites.add(plataforma_movel)
    for zona_perigosa in zonas_perigosas:
        todos_sprites.add(zona_perigosa)

    relogio = pygame.time.Clock()
    pontuacao = 0
    rodando = True

    while rodando:
        teclas_pressionadas = pygame.key.get_pressed()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    jogador.pular()

        jogador.atualizar(teclas_pressionadas)
        for plataforma_movel in plataformas_moveis:
            plataforma_movel.atualizar()  # Atualiza as plataformas móveis

        colisoes = pygame.sprite.spritecollide(jogador, plataformas, False)
        if colisoes:
            jogador.rect.bottom = colisoes[0].rect.top
            jogador.velocidade_y = 0
            jogador.no_chao = True

        colisoes_moveis = pygame.sprite.spritecollide(jogador, plataformas_moveis, False)
        if colisoes_moveis:
            jogador.rect.bottom = colisoes_moveis[0].rect.top
            jogador.velocidade_y = 0
            jogador.no_chao = True
            jogador.rect.x += VELOCIDADE_PLATAFORMA_MOVEL * colisoes_moveis[0].direcao

        colisoes_perigosas = pygame.sprite.spritecollide(jogador, zonas_perigosas, False)
        if colisoes_perigosas:
            desenhar_texto(tela, "Perdeu o jogo", fonte, COR_TEXTO, LARGURA_TELA // 2 - 100, ALTURA_TELA // 2)
            pygame.display.flip()
            pygame.time.wait(2000)
            # Reiniciar o jogo
            return main()

        pontuacao += 1
        tela.blit(fundo, (0, 0))  # Desenha o fundo na tela
        todos_sprites.draw(tela)
        desenhar_texto(tela, f"Pontuação: {pontuacao}", fonte, COR_TEXTO, 10, 10)
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

