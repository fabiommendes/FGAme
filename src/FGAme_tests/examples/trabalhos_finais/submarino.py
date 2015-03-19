# -*- coding: utf8 -*-
#Lucas Rufino Travassos 14/0151176
#Tiago Gomes Pereira 09/0134222

from __future__ import print_function

from FGAme import *
from random import uniform, choice

COR_SUB = (76,76,255)
COR_FUN = (6,0,204)
COR_PED = (0,0,64)
COR_PED2 = (38,38,127)
COR_INI = (48,178,9)
COR_INI2 = (145,13,58)
COR_PRO = (121,20,204)

ENEMIE_RATE = 60

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))

class Submarino(World):
    #===========================================================================
    # Inicializa o mundo
    #===========================================================================
    def __init__(self, **kwds):
        #Inicializa o mundo
        #H, W = 
        super(Submarino, self).__init__(rest_coeff=1.0,background=(0,0,255))
        # self.make_bounds(-W + 10, 2 * W, -H + 10, H - 10, delta=400)
        self.listen('long-press', 'up', self.move_up)
        self.listen('long-press', 'down', self.move_down)
        self.listen('key-down', 'space', self.shoot)
        
        #Cria o Player
        self.player = player = AABB(shape=[100, 45], pos_cm=(-300, 0), world=self, color=(76,76,255), mass=50)
        player.damping = 30
        
        player.listen('collision', self.player_collision)
        
        self.score = 0
        
        self.enemies = []
        self.projectiles = []
        
        self.walls = []
        self.ceiling_floor((0,0,0))
        self.ceiling_floor(random_color(), 800)
        self.listen('frame-enter', self.detect_end)
        self.listen('frame-enter', self.add_enemies)
        
        self.counter = 0
        
#         self.background1 = self.create_background(1,100,200)
        
    #===========================================================================
    # Funções do Player
    #===========================================================================
    def move_up(self):
        '''Acionado com a seta para cima'''

        if self.player.ymax < 290:
            self.player.boost(Vector(0, 100))

    def move_down(self):
        '''Acionado com a seta para baixo'''

        if self.player.ymax > -240:
            self.player.boost(Vector(0, -100))
    
    def shoot(self):
        # criar o projetil
        
        self.projectile = projectile = AABB(shape=[50, 30], pos_cm=(self.player.xmax+25, self.player.pos_cm.y), vel_cm=(500, 0), world=self, color=COR_INI2, mass=1e9)
        self.projectiles.append([projectile])
        
    def player_collision(self, col):
        # Detecta todas as colisões do player
        
        #if self.player in col.objects:
        self.stop()
        GameOver().run()
    #===========================================================================
    # Construção do cenário
    #===========================================================================
    def ceiling_floor(self, colors, posx=0):
        '''Cria as paredes de cima e de baixo da caverna onde o submarino está'''
        
        speed = 250
        
        ceiling = AABB(bbox=(-400, 400, 250, 300),
                     mass='inf', vel_cm=(-speed, 0), world=self, color=colors)
        
        floor = AABB(bbox=(-400, 400, -300, -250),
                     mass='inf', vel_cm=(-speed, 0), world=self, color=colors)
        if posx:
            ceiling.move((posx, 0))
            floor.move((posx, 0))
        
        self.walls.append([ceiling, floor])
        
    def detect_end(self):
        '''Detecta quando o inicio do teto e do chão saem da tela e adiciona outros teto e chão'''

        L = self.walls
        if L[0][0].xmax < -400:
            middle = L[1][0].pos_cm.x
            self.remove(L[0][0])
            self.remove(L[0][1])
            del L[0]
            self.ceiling_floor(random_color(), middle + 800)
    
    def create_background(self, y_inicial, yi, yf):
        
        pontos = []
        pontos.append([(-500,y_inicial),(500,y_inicial)])
         
        for x in range(500,-501,-50):
            y = uniform(yi,yf)
            p = (x, y)
            pontos.append([p])
               
        return Poly(pontos,color='red',world=self)
    
    def add_enemies(self):
        global ENEMIE_RATE
        if(self.counter == ENEMIE_RATE):
            global COR_INI
            #cria a posicao randomicamente
            pos_inimigo = (400, uniform(249,-249))
            #cria o inimigo e manda ele andar pra frente de boa
            inimigo = AABB(shape=[100, 45], pos_cm=pos_inimigo, world=self, color=COR_INI, mass=50)
            inimigo.boost(Vector(uniform(-500,-150), 0))
            inimigo.listen("collision", self.destroy_enemie)
            self.enemies.append([inimigo])
            
            self.counter = 0
            ENEMIE_RATE = int(uniform(60, 120))
        else:
            self.counter += 1
    
    def delete_enemy(self):
        pass
    
    def destroy_enemie(self, col):        
        #print("matou inimigo")
        #self.remove(col.objects[1])
        self.score += 1
        print(self.score)
        
    def game_over(self):
        '''Game over'''
        self.stop()
        GameOver().run()
    

class GameOver(World):
    def __init__(self):
        super(GameOver, self).__init__(background=(255, 0, 0), gravity=10)
        Poly.rect(shape=(600, 100), pos_cm=(0, -200), theta_cm=pi / 9,
                  centered=True, world=self, mass='inf', color=(255, 0, 0))
        letters = add_word('game over', self, scale=5, pos=(-220, 50))
        for l in letters:
            l.inertia *= 20

        self.listen('key-down', 'enter', self.reinit)

    def reinit(self):
        self.stop()
        Submarino().run()
 
#===========================================================================
# Inicia o Jogo
#===========================================================================
Submarino().run()