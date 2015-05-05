#-*- coding: utf8 -*-
#
# Nome: Guilherme Costa 10/45792
#

'''Tremble ye who enters here!
Este código foi feito em ritmo de gamejam, as gambiarras estão por toda'''

from FGAme import * 
from random import uniform

class Ship(World):
    def __init__(self):
        super(Ship, self).__init__(gravity=0, damping = 0.2)

        self.listen('frame-enter', self.check_victory)
        self.listen('frame-enter', self.ap_bar_ctl)

        self.player1_indicator = []
        self.player2_indicator = []

        self.height = 600
#        self.gambiarra.pos_cm = (390.0, -150)
        self.ap_bar = AABB(shape=(20, self.height), color=(255, 0, 155))
        self.ap_bar.pos_cm = (390.0, -400)
        self.add(self.ap_bar, layer = 1, has_collision = False)
#        self.add(self.gambiarra, layer = 2, has_collision = False)
        self.projectile = None

        self.player1 = self.new_ship(ship_color = 'blue', start = (-200, -200))
        self.player1_orientation = Vector(0.0, 1.0)
        self.player1_hp = 3
        self.player1_ammo = 1;
        self.player1_ap = 100;

        self.player2 = self.new_ship(ship_color = 'red', start = (200, 200))
        self.player2_orientation = Vector(0.0, 1.0)
        self.player2_hp = 3
        self.player1_ammo = 1;
        self.player1_ap = 100;

        for i in range(self.player1_hp):
            chunk = AABB(shape=(20, 20), color='blue')
            chunk.pos_cm = (-170 + 30*i , -270.0)
            self.player1_indicator.append(chunk)
            self.add(chunk, layer = 1, has_collision = False)

        for i in range(self.player2_hp):
            chunk = AABB(shape=(20, 20), color='red')
            chunk.pos_cm = (170 + 30*i , -270.0)
            self.player2_indicator.append(chunk)
            self.add(chunk, layer = 1, has_collision = False)

        self.current_player = self.player1
        
        self.asteroid_field = self.make_field(quantity = 30)

        for asteroid in self.asteroid_field:
            self.add(asteroid)

        self.listen('key-down', 'space', self.fire)
        self.listen('key-down', 'e', self.switch)
        
        self.listen('long-press', 'left', self.stabilise, (0.1,))
        self.listen('long-press', 'right', self.stabilise, (-0.1,))
        
        self.listen('long-press', 'up', self.move, (1.8,))
        self.listen('long-press', 'down', self.move, (-1.8,))
    
        self.player1.listen('collision', self.deal_damage)
        self.player2.listen('collision', self.deal_damage)

        self.receiving_input = True

    #===========================================================================
    #: Controle do Jogo
    #===========================================================================

    def check_victory(self):
        if(self.player1_hp is 0):
            print("Player 2 Wins!")
            self.stop()

        if(self.player2_hp is 0):
            print("Player 1 Wins!")
            self.stop()

        if self.player1.pos_cm.y > 300 or self.player1.pos_cm.y < -300:
            print("Player 2 Wins!")
            self.stop()

        if self.player1.pos_cm.x > 400 or self.player1.pos_cm.x < -400:
            print("Player 2 Wins!")
            self.stop()

        if self.player2.pos_cm.y > 300 or self.player2.pos_cm.y < -300:
            print("Player 1 Wins!")
            self.stop()

        if self.player2.pos_cm.x > 400 or self.player2.pos_cm.x < -400:
            print("Player 1 Wins!")
            self.stop()

    def ap_bar_ctl(self):
        if self.current_player is self.player1:
            self.ap_bar.ymax = self.height*(self.player1_ap/100 - 0.5)
        else:
            self.ap_bar.ymax = self.height*(self.player2_ap/100 - 0.5)
    
    #===========================================================================
    #: Criação de Objetos
    #===========================================================================

    def new_ship(self, ship_color, start):
        ship = Poly([(0, 0), (-10, -30), (10, -30)], color= ship_color, adamping = 1000.0,world=self)
        ship.pos_cm = start
        ship_orientation = Vector(0.0, 1.0)
        ship.inertia *= 10
        ship.mass = 10000
        return ship

    def make_field(self, quantity):
        
        field = []

        for i in range(quantity):
            obj = Poly.regular(5, 30, color = (50, 50, 50), density=1)
            obj.scale(uniform(0.75, 2))
            obj.rotate(uniform(0, 2 * pi))
            field.append(obj)            

        return field
    
    #===========================================================================
    #: Controle das naves
    #===========================================================================

    def fire(self):
        if self.current_player is self.player1:
            if self.player1_ammo is not int(0):
                self.player1_ammo = self.player1_ammo - 1 
                self.player1_orientation = self.player1.vertices[0] - self.player1.pos_cm
                self.player1_orientation = self.player1_orientation.normalized()
            else:
                return
        else:
            if self.player2_ammo is not int(0):
                self.player2_ammo = self.player2_ammo - 1
                self.player2_orientation = self.player2.vertices[0] - self.player2.pos_cm
                self.player2_orientation = self.player2_orientation.normalized()
            else:
                return

        self.projectile = Poly([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], color= 'blue', world=self)

        if self.current_player is self.player1:        
            self.projectile.boost(200*self.player1_orientation)
        else:
            self.projectile.boost(200*self.player2_orientation)
        
        self.projectile.move(self.current_player.vertices[0] + (1.0, 1.0))
        self.projectile.mass = 1000        

    def deal_damage(self, dummy = None):
        if self.projectile is not None:
            result = get_collision(self.projectile, self.player2)
            
            if result is not None:
                self.remove(self.player2_indicator[self.player2_hp - 1])
                self.player2_hp = self.player2_hp - 1
            
            result = get_collision(self.projectile, self.player1)
            if result is not None:
                self.remove(self.player1_indicator[self.player1_hp - 1])
                self.player1_hp -= 1
            
            self.remove(self.projectile)

            return

    def switch(self):
        if self.current_player is self.player1:
            self.current_player = self.player2
            self.player2_ammo = 1
            self.player2_ap = 100
        else:
            self.current_player = self.player1
            self.player1_ammo = 1
            self.player1_ap = 100

    def change_omega(self, delta):
        '''Modifica a velocidade angular da nave por um fator delta'''

        if self.receiving_input:
            if self.current_player is self.player1:        
                self.player1_orientation = self.player1.vertices[0] - self.player1.pos_cm
                self.player1_orientation = self.player1_orientation.normalized()
            else:
                self.player2_orientation = self.player2.vertices[0] - self.player2.pos_cm
                self.player2_orientation = self.player2_orientation.normalized()

            self.current_player.rotate(delta)

    def stabilise(self, delta):
        'Utilizado para estabilizar a nave após uma colisão'

        if self.receiving_input:
            if self.current_player is self.player1:        
                self.player1_orientation = self.player1.vertices[0] - self.player1.pos_cm
                self.player1_orientation = self.player1_orientation.normalized()
            else:
                self.player2_orientation = self.player2.vertices[0] - self.player2.pos_cm
                self.player2_orientation = self.player2_orientation.normalized()

            self.current_player.aboost(delta)

            if self.current_player.omega_cm**2 < 0.1**2:
                self.current_player.omega_cm = 0.0

    def move(self, v):
        '''Modifica a velocidade linear da nave por um fator v'''

        if self.receiving_input:
            if self.current_player is self.player1:        
                if self.player1_ap > 0:
                    self.player1_orientation = self.player1.vertices[0] - self.player1.pos_cm
                    self.player1_orientation = self.player1_orientation.normalized()
                    self.current_player.boost(v*self.player1_orientation)
                    vabs = (v**2)**0.5
                    self.player1_ap = self.player1_ap - (vabs**0.25)                    
                    if self.player1_ap < 0:
                        self.player1_ap = 0

            else:
                if self.player2_ap > 0:
                    self.player2_orientation = self.player2.vertices[0] - self.player2.pos_cm
                    self.player2_orientation = self.player2_orientation.normalized()
                    self.current_player.boost(v*self.player2_orientation)
                    vabs = (v**2)**0.5
                    self.player2_ap = self.player2_ap - (vabs**0.25)
                    if self.player2_ap < 0:
                        self.player2_ap = 0                
# #     def game_over(self):
# #         '''Game over'''

# #         
# #         GameOver().run()

# # class GameOver(World):
# #     def __init__(self):
# #         super(GameOver, self).__init__(background=(255, 0, 0), gravity=10)
# #         Poly.rect(shape=(600, 100), pos_cm=(0, -200), theta_cm=pi / 9,
# #                   centered=True, world=self, mass='inf', color=(255, 0, 0))
# #         letters = add_word('game over', self, scale=5, pos=(-220, 50))
# #         for l in letters:
# #             l.inertia *= 20

# #         self.listen('key-down', 'enter', self.reinit)

# #     def reinit(self):
# #         self.stop()
# #         Field().run()

if __name__ == '__main__':
    Ship().run()
