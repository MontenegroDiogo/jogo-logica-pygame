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

# Estabelece a pasta que contém as figuras e sons.
diretorio_img = path.join(path.dirname(__file__), 'img')
diretorio_sons = path.join(path.dirname(__file__), 'sounds')

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
    def __init__(self, spritesheet_jogador, som_pulo):
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
        self.pulos_disponiveis = 2  # Para o pulo duplo
        self.som_pulo = som_pulo

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
            self.pulos_disponiveis = 2  # Resetar os pulos disponíveis quando tocar o chão

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
        if self.pulos_disponiveis > 0:
            self.velocidade_y = -FORCA_PULO
            self.no_chao = False
            self.estado = PULANDO
            self.pulos_disponiveis -= 1
            self.som_pulo.play()

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

class Moeda(pygame.sprite.Sprite):
    def __init__(self, x, y, imagem_moeda):
        super().__init__()
        self.image = pygame.image.load(imagem_moeda).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))  # Reduzir o tamanho da moeda
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def desenhar_texto(tela, texto, fonte, cor, x, y):
    superficie_texto = fonte.render(texto, True, cor)
    rect_texto = superficie_texto.get_rect()
    rect_texto.topleft = (x, y)
    tela.blit(superficie_texto, rect_texto)

def mostrar_menu(tela, fundo, fonte):
    tela.blit(fundo, (0, 0))
    desenhar_texto(tela, "Coin Master", fonte, COR_TEXTO, LARGURA_TELA // 2 - 100, ALTURA_TELA // 2 - 100)
    desenhar_texto(tela, "Pressione ENTER para iniciar", fonte, COR_TEXTO, LARGURA_TELA // 2 - 150, ALTURA_TELA // 2)
    pygame.display.flip()

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Coin Master")

    fonte = pygame.font.Font(None, TAMANHO_FONTE)

    # Carregar imagem de fundo
    fundo = pygame.image.load(path.join(diretorio_img, 'background.jpg')).convert()

    # Carregar sons
    som_pulo = pygame.mixer.Sound(path.join(diretorio_sons, 'pulo.wav'))
    som_moeda = pygame.mixer.Sound(path.join(diretorio_sons, 'coletar_moeda.wav'))

    # Mostrar tela de menu
    mostrar_menu(tela, fundo, fonte)
    no_menu = True
    while no_menu:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    no_menu = False

    spritesheet_jogador = pygame.image.load(path.join(diretorio_img, 'hero.png')).convert_alpha()
    jogador = Jogador(spritesheet_jogador, som_pulo)
    todos_sprites = pygame.sprite.Group()
    todos_sprites.add(jogador)

    plataformas = pygame.sprite.Group()
    plataformas_moveis = pygame.sprite.Group()
    zonas_perigosas = pygame.sprite.Group()
    moedas = pygame.sprite.Group()

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

    def adicionar_moedas():
        for _ in range(10):  # Adicionar 10 moedas em posições aleatórias
            x = random.randint(0, LARGURA_TELA - 32)
            y = random.randint(0, ALTURA_TELA - 32)
            moeda = Moeda(x, y, path.join(diretorio_img, 'coin.png'))
            moedas.add(moeda)
            todos_sprites.add(moeda)

    adicionar_moedas()

    relogio = pygame.time.Clock()
    pontuacao = 0
    rodando = True
    perdeu = False

    while rodando:
        teclas_pressionadas = pygame.key.get_pressed()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    jogador.pular()
                elif evento.key == pygame.K_r and perdeu:
                    return main()

        if not perdeu:
            jogador.atualizar(teclas_pressionadas)
            for plataforma_movel in plataformas_moveis:
                plataforma_movel.atualizar()  # Atualiza as plataformas móveis

            colisoes = pygame.sprite.spritecollide(jogador, plataformas, False)
            if colisoes:
                jogador.rect.bottom = colisoes[0].rect.top
                jogador.velocidade_y = 0
                jogador.no_chao = True
                jogador.pulos_disponiveis = 2  # Resetar os pulos disponíveis ao tocar uma plataforma

            colisoes_moveis = pygame.sprite.spritecollide(jogador, plataformas_moveis, False)
            if colisoes_moveis:
                jogador.rect.bottom = colisoes_moveis[0].rect.top
                jogador.velocidade_y = 0
                jogador.no_chao = True
                jogador.pulos_disponiveis = 2  # Resetar os pulos disponíveis ao tocar uma plataforma móvel
                jogador.rect.x += VELOCIDADE_PLATAFORMA_MOVEL * colisoes_moveis[0].direcao

            colisoes_perigosas = pygame.sprite.spritecollide(jogador, zonas_perigosas, False)
            if colisoes_perigosas:
                perdeu = True

            colisoes_moedas = pygame.sprite.spritecollide(jogador, moedas, True)
            if colisoes_moedas:
                pontuacao += len(colisoes_moedas)
                som_moeda.play()
                if len(moedas) == 0:  # Se todas as moedas foram coletadas
                    adicionar_moedas()  # Adicionar mais moedas

        tela.blit(fundo, (0, 0))  # Desenha o fundo na tela
        todos_sprites.draw(tela)
        desenhar_texto(tela, f"Pontuação: {pontuacao}", fonte, COR_TEXTO, 10, 10)
        if perdeu:
            desenhar_texto(tela, "Perdeu o jogo. Pressione R para reiniciar", fonte, COR_TEXTO, LARGURA_TELA // 2 - 200, ALTURA_TELA // 2)
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
