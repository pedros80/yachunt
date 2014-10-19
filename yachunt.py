#!/usr/bin/env python
""" 

yachunt.py

YACHunt: yet another computerised hunting game

another genuine copy by pedros

graphics from ari feldman's gpl spritelib
background by steph

Copyright (C) 2009-2013 Peter Somerville

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Peter Somerville"
__email__ = "peterwsomerville@gmail.com"

import pygame
from pygame.locals import *
from Sprites import *

def main():
    """main function
        call menu to determine weapon then
        play game
        or exit """
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.init()
    pygame.mixer.init()  
    
    playing = True
    score = 0
    while playing:
     
        playing, weapon = menu(score)
        if weapon is not None:
            score = game(weapon)

def menu(score):
    # Set up the display
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("YACHunt...Choose Your Weapon")
    bg = pygame.image.load("img" + os.sep + "bg.bmp")
    
    scoreBoard = ScoreTable()
    
    words = (
    "YACHunt:", 
    "Yet Another Computerised", 
    "Hunting game", 
    "", 
    "(a) - SHOTGUN - 2 shots, wide area", 
    "(b) - PISTOL - 6 shots, small area", 
    "(c) - high scores", 
    "(d) - instructions", 
    "", 
    "last score %d" % score, 
    "high score %d" % scoreBoard.getHighScore()
    )
    
    menuLabels = pygame.sprite.Group()
    lineCount = 1
    for line in words:
        templabel = Label(40)
        templabel.setText(line)
        templabel.setCenter((400, lineCount*35))
        templabel.setColour((0, 0, 0))
        menuLabels.add(templabel)
        lineCount += 1
    
    displayMenu = True
    weapon = None
    playing = True
    
    target = Target("shotgun", screen)
    clouds = pygame.sprite.Group()
    for i in xrange(4):
        cloud = random.choice([Cloud("large", screen), Cloud("small", screen)])
        clouds.add(cloud)
            
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    while displayMenu:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                elif event.key == pygame.K_a:
                    displayMenu = False
                    weapon = "shotgun"
                    playing = True
                elif event.key == pygame.K_b:
                    displayMenu = False
                    weapon = "pistol"
                    playing = True
                elif event.key == pygame.K_c:
                    scoreBoard.showHighScores()
                elif event.key == pygame.K_d:
                    instructions()
                elif event.key == pygame.K_u:
                    displayMenu = False
                    weapon = "uzi"
                    playing = True
        
        screen.fill((0, 0, 0))        
        screen.blit(bg, (0, 0)) 
        clouds.update()
        clouds.draw(screen)
        target.update()
        target.draw(screen)
        menuLabels.update()
        menuLabels.draw(screen)  

        pygame.display.flip() # draw frame
                    
    return playing, weapon 
        

def game(weapon):
    screen = pygame.display.set_mode((800, 600))
    level = 1
    scoreBoard = ScoreTable()

    # player
    target = Target(weapon, screen)

    hunting = True
    while hunting:
        hunting = dolevel(level, target)
        if hunting:
            level+=1
            
    scoreBoard.checkScore(target.score)
    return target.score  
    
def dolevel(level, target):
    # Set up the display
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("YACHunt... Level: %d" % level)
    bg = pygame.image.load("img" + os.sep + "bg.bmp")

    target.shots = target.capacity
    
    animallevel = 0
    birdlevel = 0
    if level > 4:
        animallevel = 4
    else:
        animallevel = level
    if level > 8:
        birdlevel = 8
    else:
        birdlevel = level
    # birds group
    birds = pygame.sprite.Group()
    for i in xrange(birdlevel):
        bird = random.choice([Duck(screen), Hawk(screen)])
        birds.add(bird)
   
    # animals group
    animals = pygame.sprite.Group()
    for i in xrange(animallevel):
        animal = random.choice([Frog(screen), Snake(screen), Turtle(screen), Snail(screen)])
        animals.add(animal)
    
    if random.randint(1, 5) == 1:
        animals.add(Cat(screen))
        
    # clouds
    clouds = pygame.sprite.Group()
    for i in xrange(level+2):
        cloud = random.choice([Cloud("large", screen), Cloud("small", screen)])
        clouds.add(cloud)
    
    # label objects and positioning    
    scoreLabel = Label(30)
    scoreLabel.setCenter((50, 500))
    hitsLabel = Label(30)
    hitsLabel.setCenter((50, 550))
    escapedLabel = Label(30)
    escapedLabel.setCenter((200, 500))
    missesLabel = Label(30)
    missesLabel.setCenter((200, 550))
    shotsLeftLabel = Label(30)
    shotsLeftLabel.setCenter((400, 500))
    levelLabel = Label(30)
    levelLabel.setCenter((400, 550))
    levelLabel.setText("Level: %d"%level)
    goLabel = Label(60)
    goLabel.setCenter((screen.get_width()/2, screen.get_height()/2))
    goLabel.setColour((255, 0, 0))
    
    # add to labels group
    labels = pygame.sprite.Group(levelLabel, scoreLabel, hitsLabel, missesLabel, escapedLabel, shotsLeftLabel, goLabel)
    
    # hide mouse
    pygame.mouse.set_visible(False)
    
    # new clock
    clock = pygame.time.Clock() 
    
    target.bangs.empty()
    # main loop
    running = True
    paused = False
    while running:

        clock.tick(30)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                target.shoot(birds, animals, clouds)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_p:
                    paused = not paused
                elif e.key == pygame.K_SPACE:
                    target.shots = target.capacity
        
        # clear screen and re-blit bg       
        screen.fill((0, 0, 0))        
        screen.blit(bg, (0, 0))
        totalshots = float(target.misses + target.hits)

        if totalshots > 0:
            accuracy = float(target.hits/totalshots)*100 
        else:
            accuracy = 0
        # set labels new text
        scoreLabel.setText("1Up: %i" % target.score)
        hitsLabel.setText("Hits: %i" % target.hits)
        missesLabel.setText("Hit Rate: %.2f" % accuracy+"%")
        escapedLabel.setText("Escaped: %i" % target.escaped)
        shotsLeftLabel.setText("Shots: %i" % target.shots)
            
        if not paused:
            # update and draw sprites
            goLabel.setText("")
            labels.update()
            target.update()
            clouds.update()
            birds.update(target)
            animals.update(target)
            
        else:
            goLabel.setText("Paused!!")
            labels.update()
            
        if target.escaped == 21:
            goLabel.setText("Game Over !!")
            labels.update()
            birds.draw(screen)
            animals.draw(screen)
            target.draw(screen)
            clouds.draw(screen)
            labels.draw(screen)      
            pygame.display.flip()
            pygame.time.wait(2500)
            return False
        
        if target.hits >= level*20:
            goLabel.setText("Level %d Completed !!" % level)
            labels.update()
            birds.draw(screen)
            animals.draw(screen)
            target.draw(screen)
            clouds.draw(screen)
            labels.draw(screen)      
            pygame.display.flip()
            if accuracy > 75.0:
                target.score += 50
            if accuracy == 100.0:
                target.score += 100
            pygame.time.wait(2500)
            return True  
                     
        birds.draw(screen)
        animals.draw(screen)
        target.draw(screen)
        clouds.draw(screen)
        labels.draw(screen)
        if len(target.bangs) > 0:
                for b in target.bangs:
                    b.draw(screen)      
        pygame.display.flip()
        
      

def instructions():
    
    # Set up the display
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("YACHunt...")
    bg = pygame.image.load("img" + os.sep + "bg.bmp")
    
    words = (
    "YACHunt:", 
    "Yet Another Computerised", 
    "Hunting game", 
    "", 
    "Shoot the birds and animals", 
    "by clicking when they are targeted.", 
    "If more than 20 escape your shooting, you lose!", 
    "", 
    "Kill two creatures with one round", 
    "to score more points", 
    "Shoot the bullet or space bar to reload weapon"
    )
    
    insLabels = pygame.sprite.Group()
    lineCount = 1
    for line in words:
        templabel = Label(35)
        templabel.setText(line)
        templabel.setCenter((400, lineCount*35))
        templabel.setColour((0, 0, 0))
        insLabels.add(templabel)
        lineCount += 1
    
    clouds = pygame.sprite.Group()
    for i in xrange(4):
        cloud = random.choice([Cloud("large", screen), Cloud("small", screen)])
        clouds.add(cloud)
    
    target = Target("shotgun", screen)
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)

    showIns = True
    while showIns:

        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                showIns = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    showIns = False

        screen.fill((0, 0, 0))        
        screen.blit(bg, (0, 0)) 
        clouds.update()
        clouds.draw(screen)
        insLabels.update()
        insLabels.draw(screen)  
        target.update()
        target.draw(screen)
        pygame.display.flip() # draw scene
            
if __name__ == "__main__":
   main()            
