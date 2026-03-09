# -*- coding: utf-8 -*-
import sys
import math
import time
import numpy as np
import pygame

from Physics import Physics
from Graphics import Graphics

class PA:
    def __init__(self):
        self.physics = Physics(hardware_version=3) 
        self.device_connected = self.physics.is_device_connected()
        self.graphics = Graphics(self.device_connected)
        xc,yc = self.graphics.screenVR.get_rect().center
        ##############################################
        #ADD things here that you want to run at the start of the program!
        # These gains are weird because we do not convert to SI units. The mass especially
        self.k = 0.05 # Spring stiffness
        self.spring_anchor = np.array([xc, yc])  # Spring anchor at screen center
        self.c =  0.003 # Damping coefficient
        self.m = 0.00002 # A bit unrealistic, I might convert to SI units someday
        self.dt = 1/30 # Simulation seems to run in 30 fps
        ##############################################
    
    def run(self):
        p = self.physics
        g = self.graphics
        keyups,xm = g.get_events()
        if self.device_connected:
            pA0,pB0,pA,pB,pE = p.get_device_pos() 
            pA0,pB0,pA,pB,xh = g.convert_pos(pA0,pB0,pA,pB,pE)
        else:
            xh = g.haptic.center
        fe = np.array([0.0,0.0])
        xh = np.array(xh) 
        xc,yc = g.screenVR.get_rect().center
        g.erase_screen()
        for key in keyups:
            if key==ord("q"): #q for quit, ord() gets the unicode of the given character
                sys.exit(0) #raises a system exit exception so the "PA.close()" function will still execute
            if key == ord('m'): #Change the visibility of the mouse
                pygame.mouse.set_visible(not pygame.mouse.get_visible())
            if key == ord('r'): #Change the visibility of the linkages
                g.show_linkages = not g.show_linkages
            if key == ord('d'): #Change the visibility of the debug text
                g.show_debug = not g.show_debug
            #you can add more if statements to handle additional key characters

        ##############################################
        if not hasattr(self, "xh_prev"):
            self.xh_prev = xh.copy()
        if not hasattr(self, "v_prev"):
            self.v_prev = np.zeros(2)

        # velocity + acceleration (px/s, px/s^2)
        v = (xh - self.xh_prev) / self.dt
        a = (v - self.v_prev) / self.dt

        fs =  self.k * (xh - self.spring_anchor)
        fd =  self.c * v
        fm =  self.m * a            

        fe = fs + fd + fm

        # update history
        self.xh_prev = xh.copy()
        self.v_prev = v.copy()


        ##############################################
        
        if self.device_connected:
            p.update_force(fe)
        else:
            xh = g.sim_forces(xh,fe,xm,mouse_k=0.5,mouse_b=0.8) 
            pos_phys = g.inv_convert_pos(xh)
            pA0,pB0,pA,pB,pE = p.derive_device_pos(pos_phys)
            pA0,pB0,pA,pB,xh = g.convert_pos(pA0,pB0,pA,pB,pE) 

        # Show arrows for the spring (red), damping (blue), mass (brown), total (green)
        # We have to draw these arrows the opposite direction because somehow the simulation flips force direction
        pygame.draw.line(g.screenVR, (255, 0, 0),   tuple(xh), tuple((xh + -20 * fs).astype(int)), 2)
        pygame.draw.line(g.screenVR, (0, 0, 255),   tuple(xh), tuple((xh + -20 * fd).astype(int)), 2)
        pygame.draw.line(g.screenVR, (150, 75, 0),  tuple(xh), tuple((xh + -40 * fm).astype(int)), 2)
        # pygame.draw.line(g.screenVR, (0, 255, 0),   tuple(xh), tuple((xh + -20 * fe).astype(int)), 2)

        # Display forces on screen
        font = pygame.font.Font('freesansbold.ttf', 16)
        g.screenVR.blit(font.render(f'fs: [{fs[0]:.2f}, {fs[1]:.2f}]', True, (255, 0, 0),   (255, 255, 255)), (10, 40))
        g.screenVR.blit(font.render(f'fd: [{fd[0]:.2f}, {fd[1]:.2f}]', True, (0, 0, 255),   (255, 255, 255)), (10, 60))
        g.screenVR.blit(font.render(f'fm: [{fm[0]:.2f}, {fm[1]:.2f}]', True, (150, 75, 0),  (255, 255, 255)), (10, 80))
        g.screenVR.blit(font.render(f'fe: [{fe[0]:.2f}, {fe[1]:.2f}]', True, (0, 255, 0),   (255, 255, 255)), (10, 100))

        g.render(pA0,pB0,pA,pB,xh,fe,xm)
        
    def close(self):
        ##############################################
        #ADD things here that you want to run right before the program ends!

        
        ##############################################
        self.graphics.close()
        self.physics.close()

if __name__=="__main__":
    pa = PA()
    try:
        while True:
            pa.run()
    finally:
        pa.close()