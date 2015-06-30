#-*- coding: utf8 -*-
#
# Alunos:   Cristóvão Lima Frinhani         10/0097235
#           Lucas dos Santos Ribeiro Leite  10/0034462
#

import pygame
from FGAme import *
from random import *

pygame.font.init()
force = 15
MSGS_FONT = pygame.font.Font(pygame.font.match_font('monospace', bold=True), 30)


class Play(Circle):
    def __init__(self, **kwds):
        super(Play, self).__init__(20, color='red', **kwds)
        self.pos_cm = (0, 0)
        #self.rotate(uniform(0, 2 * pi))
        #self.inertia *= 10
        #self.omega_cm = uniform(-2, 2)
        self.receiving_input = True
        self.tipo='play'
        #self.listen('long-press', 'up', self.play_v,(1,))
        #self.listen('long-press', 'down', self.play_v,(-1,))
        #self.listen('long-press', 'left', self.play_h,(-1,))
        #self.listen('long-press', 'right', self.play_h,(1,))
        
    @listen('long-press', 'up',(1,))
    @listen('long-press', 'down',(-1,))
    def play_v(self,i):
        '''Aumenta a velocidade vertical do play'''
        if self.receiving_input:
            self.boost((0, i*force))
    @listen('long-press', 'left', (-1,))
    @listen('long-press', 'right', (1,))
    def play_h(self,i):
        '''Aumenta a velocidade horizontal do play'''
        if self.receiving_input:
            self.boost((i*force,0))

    @listen('collision')
    def block_input(self, col=None):
        '''trataInput'''
        
        if col.object_A.tipo=='play':
            col.object_B.vel_cm=col.object_A.vel_cm
            col.object_B.velocidade=0
            col.object_B.receiving_input = True
            col.object_B.color='red'
        else:
            col.object_A.vel_cm=col.object_B.vel_cm
            col.object_A.velocidade=0
            col.object_A.receiving_input = True
            col.object_A.color='red'
		
		
class Enemy(Poly):
    def __init__(self, **kwds):
        base = uniform(50,70)
        altura = uniform(40,90)
        x= uniform(20,80)
        super(Enemy, self).__init__([(0, 0), (base, 0), (x, altura)], color='black', **kwds)
        self.tipo='enemy'
        x_pos = uniform(-600,600)
        y_pos = uniform(-400,400)
        
        while 400>x_pos>-400 and 300>y_pos>-300:
            x_pos = uniform(-600,600)
            y_pos = uniform(-400,400)    
        
        type = random()
        #if type < 0.5 :
        #    self = Poly.regular(N=4, length = 50, color = 'black', world = self)
        #elif type < 0.8:
        #    self = Poly.regular(N=4, length = 50, color = 'black', world = self)
        #else:
        #    self = Poly.regular(N=3, length = 60, color = 'black', world = self)
        self.pos_cm = VectorM(x_pos, y_pos)
        
        #Vetor do inimigo ao player
        self.vel_cm = VectorM(random() * 200, random() * 200)

        self.receiving_input = False

    @listen('long-press', 'up',(1,))
    @listen('long-press', 'down',(-1,))
    def enemy_up(self,i):
        '''Aumenta a velocidade vertical do flappy'''
        if self.receiving_input:
            self.boost((0, i*force))
    @listen('long-press', 'left', (-1,))
    @listen('long-press', 'right', (1,))
    def change_omega(self,i):
        '''Modifica a velocidade angular do flappy por um fator delta'''
        if self.receiving_input:
            self.boost((i*force,0))
			
			
class Jogo(World):
    def __init__(self, **kwds):
        super(Jogo, self).__init__(rest_coeff=1, sfriction = 100)
        self.make_bounds(-800, 800, -400, 400)
        self.score = 0
		#self.highscore = 0
        
        # Adiciona a bola principal
        self.create_enemies()
        self.play = Play(world=self)
        self.listen('frame-enter', self.detect_exit)
		
    def create_enemies(self):
        self.enemyList=[]
        for _ in range(40):
            
            self.enemy = Enemy(world=self)
            self.enemyList.append(self.enemy)
            print(len(self.enemyList))
            
    def update(self, dt):
        super(Jogo, self).update(dt)
        self.score += 1
        
    def detect_exit(self):
        if self.play.xmax < -400 or self.play.xmin > 400:
            self.game_over()

        elif self.play.ymin > 300 or self.play.ymax < -300:
            self.game_over()
        count =0
        for i in self.enemyList:
            if i.receiving_input:
               count+=1
               if i.xmax < -400 or i.xmin > 400:
                    self.game_over()

               elif i.ymin > 300 or i.ymax < -300:
                    self.game_over()
        if count >4:
           self.game_over()
    def game_over(self):
        self.stop()
        print("Score", self.score)
        GameOver(score=self.score).run()

class GameOver(World):
    def __init__(self,score):
        super(GameOver, self).__init__(background=(255, 0, 0), gravity=10)
        Poly.rect(shape=(600, 100), pos_cm=(0, -200), theta_cm=pi / 9,
                  centered=True, world=self, mass='inf', color=(255, 0, 0))
        letters = add_word('game over ', self, scale=5, pos=(-220, 50))
        score = add_word('score '+str(score), self, scale=5, pos=(-330, 100))
		
        for l in letters:
            l.inertia *= 20
        for s in score:
            s.mass = 'inf'

        self.listen('key-down', 'enter', self.reinit)

    def reinit(self):
        self.stop()
        Jogo().run()

if __name__ == '__main__':
    Jogo().run()
