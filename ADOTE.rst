================
Adote uma classe
================

Iniciando uma campanha para dar mais amor para algumas classes que estão 
precisando. Ao todo a campanha corresponde a 5 trabalhos cujas notas são 
binárias. Algumas classes possuem menos tarefas que 5, enquanto outras podem
ter mais. Caso você tenha cumprido todas as tarefas de uma classe e queira 
adotar outra para chegar nas 5 tarefas necessárias, fique a vontade. As tarefas
podem ser realizadas em dupla ou individualmente.

Listamos classes com as respectivas tarefas agrupadas por temas.
Note que todos os trabalhos devem vir documentados e com testes unitários!


Core
====

core.mainloop.Mainloop
----------------------

    1) Manter estatísticas do tempo gasto em renderização e no loop de física
    2) Investigar e implementar clocks mais precisos que o time.time() e 
       time.sleep() 
    3) Implementar o método schedule_task() que registra tarefas que serão 
       executadas apenas quando o loop estiver desocupado

Extra
=====

extra.layout*
-------------

    Inicializadores de objetos: inicia um grupo de objetos de maneira 
    previsível ou aleatória. Ex.: Cores aleatórias, inicia em grade, inicia
    dentro de contorno, etc.   

   
Objetos matemáticos
===================

mathutils.vector.Vector
-----------------------

    1-5) 'almost_equals', 'angle', 'clamped', 'distance_to', 'is_null', 
         'lerp' (linear interpolation),  'perpendicular', 'polar', 'project',
         'reflect', 'scaled_to'
         
mathutils.vector.Vector3
------------------------

    1-5) Vetor 3D -- operações matemáticas e outros métodos da classe Vector.
    
mathutils.vector.Vector4
------------------------

    1-5) Vetor 4D -- operações matemáticas e outros métodos da classe Vector.
        

mathutils.vector.VecSeq
-----------------------
    
    Sequência de vetores 2D
    
    1-5) operações matemáticas vetor a vetor
    
         
mathutils.vector.Matrix3
------------------------

    1-5) Matrix 3x4 -- operações matemáticas + colvecs, rowvecs, flat, det, 
         trace, transposed
    6) eigval e eigvec
    7) inv
    8-9) RotMatrix3: matriz de rotação
          

mathutils.circle.Circle
-----------------------
    
    1) Testes de superposição e interseção, com outro círculo ou ponto
    2) Distância entre círculo e reta ou segmento 
    3) Interseção entre círculo e reta ou segmento
    
mathutils.segment.Segment
-------------------------
    
    1) Intersecção com outro segmento
    2) Testes de segmentação de ponto e círculo 

mathutils.vertices
------------------
    
    1) função de bound box máximo
    2) testar se o polígono é simples
    3-4) separar polígono complexo em vários simples
    
    
mathutils.instersects
---------------------

    Implementar intersecção entre figuras geométricas
    
    1) aabb e círculo
    2) aabb e aabb
    3) segmento e aabb
    4) segmento e círculo
    4) polígono e aabb
    5) polígono e círculo
    
    
Física
======

physics.obj_poly.Poly e outros
------------------------------
    
    1) implementar grande AABB invariante por rotações
    2) Construtor da classe triangulo
    3) Sub-classe Blob: polígono convexo randômico


physics.obj_group.Group
-----------------------

    Implementar classe que agrupa vários objetos
    
    1) distribuir funções tipo move, rotate para todos sub-objetos
    2) função split para desagrupar (mas mantendo velocidades consistentes)
    3) cálculo de massa, c.m  e momento de inércia
    4) cálculo da AABB
    5) mecanismo de AABB invariante como em Poly

physics.forces
--------------

    Várias coisas aqui: implementar integradores mais avançados, modelos de 
    força adicionais etc.
    Mouse force: força aplicada pelo clique do mouse
    

Visualização
============


draw.color.Color
----------------

    1) Implementar propriedades para red, green blue, alpha
    2) Implementar conversões de RGB para HSV (hue, saturation, value)
    3) Implementar conversões de HSV para RGB
    4) Implementar conversões de RGB para HSL (hue, saturation, lightness)
    5) Implementar conversões de HSL para RGB
    
    
draw.tree.Tree
--------------
    
    1) Implementar suporte para rotação e translação de todos os objetos 
       dentro da árvore
    2) Derivar Tree de Drawable e implementar os métodos rescale e transform
    
    
draw.texture.Texture (difícil!)
--------------------
    
    Esta classe ainda não existe!
    
    1) Definir a interface de Texture (ver pygame, sdl2 e outras bibliotecas 
       para inspiração)
    2) Implementar transformações simples como espelhos
    3) Tornar a Texture renderizável (conversar com o prof. sobre as outras 
       classes afetadas)
    4-5) Implementar um banco de texturas
 

core.screen.Canvas
------------------

    1) Implementar o método paint_pixel de algum backend (de preferência o 
       pygame)
    2) Implementar paint_aabb pixel a pixel
    3) Implementar paint_rect pixel a pixel
    4) Implementar paint_circle pixel a pixel
    5) Implementar paint_poly pixel a pixel (somente polígonos convexos)
    