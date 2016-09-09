'''
Created on 8 de nov de 2015

@author: chips
'''
from asyncio import get_event_loop
from FGAme import Vec, conf


async def time(loop):
    pass 

def current_timer():
    return None


def moveto(obj, pos, duration=1):
    t = 0
    step = pos - obj.pos
    
    while t < duration:
        dt = yield 'continue'
        t += dt
        obj.pos += dt/duration * step
        print('time: %s, pos: %s' % (t, obj.pos))
    obj.pos = pos
     
        
async def async_moveto(obj, pos, duration=1, timer=None):
    timer = timer or current_timer()
    t = 0
    step = pos - obj.pos
    
    while t < duration:
        dt = await timer.tick()
        t += dt
        obj.pos += dt / time * step
        print('time: %s, pos: %s' % (t, obj.pos))
    obj.pos = pos
    
