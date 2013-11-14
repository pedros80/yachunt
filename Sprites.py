#!/usr/bin/env python
""" 

Sprites.py

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
import random
import cPickle
from pygame.locals import *
from sys import exit
import os
import time

class Bang(pygame.sprite.Sprite):

    def __init__(self, pos, score):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img" + os.sep + "bang.bmp").convert()
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.x, self.y = pos
        self.duration = 15
        self.bangLabel = Label(28)
        self.bangLabel.setText(score)
        self.bangLabel.setCenter(pos)
        self.bangLabel.setColour((0, 0, 0))
        
    def update(self):
        self.duration -= 1
        if self.duration == 0:
            self.kill()
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.bangLabel.image, (self.x-5, self.y-15))
        
class Label(pygame.sprite.Sprite):
    """ class for working with text and displaying it
        methods 
            __init__(fontSize)
            update()
            setText()
            setCenter()
            setColour
    """
    
    def __init__(self, size):
        """ new label object...
        font, text, center, color"""
        # label is a sprite
        pygame.sprite.Sprite.__init__(self)
        # initial values
        self.font = pygame.font.Font("Abscissa.ttf", size)
        self.colour = (255, 255, 255)
        self.text = ""
        self.center = (-100, -100)
    
    def update(self):
        """ update label values, render text """     
        self.image = self.font.render(self.text, 1, self.colour)
        self.rect = self.image.get_rect()
        self.rect.center = self.center
    
    def draw(self, screen):
        screen.blit(self.image, self.rect) 

    def setText(self, words):
        """ give label new text """
        self.text = words
        self.update()
    def setColour(self, colour):
        """ give text new colour """
        self.colour = colour
        self.update()
    def setCenter(self, center):
        """ give label new center """
        self.center = center
        self.update()
        
class Target(pygame.sprite.Sprite):
    """ class for player's target.
        extends Sprite """       
    def __init__(self, weapon, screen):
        """ new target """
        
        # weapons dictionary
        # "name":((width, height), shots, radius)
        weapons = {"pistol":((10, 10), 6, 5), "shotgun":((40, 40), 2, 20), "uzi":((20, 20), 100, 10)}
        
        pygame.sprite.Sprite.__init__(self)
        # image and rect
        self.image = pygame.Surface(weapons[weapon][0])
        circlePos = self.image.get_width()/2, self.image.get_height()/2 
        pygame.draw.circle(self.image, (255, 0, 0), circlePos, weapons[weapon][2], 1)
        pygame.draw.line(self.image, (255, 0, 0), (circlePos[0], 0), (circlePos[1], self.image.get_height()))
        pygame.draw.line(self.image, (255, 0, 0), (0, circlePos[1]), (self.image.get_width(), circlePos[1]))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.capacity = weapons[weapon][1]
        self.shots = self.capacity
        self.score = 0
        self.hits = 0
        self.escaped = 0
        self.misses = 0
        self.screen = screen
        self.reload = Reload()
        self.bangs = pygame.sprite.Group()
        if pygame.mixer is None:
            print "no sound"
            self.sngGun = None
        else:
            self.sndGun = pygame.mixer.Sound("wav" + os.sep + "%s.wav" % weapon)
    
    def getScore(self):
        return self.score
    
    def getShotsLeft(self):
        return self.shots
        
    def getEscaped(self):
        return self.escaped
    
    def getMisses(self):
        return self.misses
        
    def getHits(self):
        return self.hits
    
    def moreEscaped(self):
        self.escaped += 1
    
    def moreScore(self, score):
        self.score += score
            
    def draw(self, screen):
        screen.blit(self.reload.getImage(), self.reload.getRect())
        screen.blit(self.image, self.rect)
        
        
    def getCapacity(self):
        return self.capacity
        
    def setShotsLeft(self, shots):
        self.shots = shots  
      
    def shoot(self, birds, animals, clouds):
        
        reloading = False
        if self.rect.colliderect(self.reload.getRect()):
            self.shots = self.capacity
            reloading = True
            
        if not reloading:
            if self.shots > 0:
                if pygame.mixer is not None:
                    self.sndGun.play()
                numHits = 0
                shotScore = 0
                hitCloud = False
                for cloud in clouds:
                    if self.rect.colliderect(cloud.getRect()):
                        hitCloud = True
        
                if not hitCloud:        
                    for bird in birds:
                        if self.rect.colliderect(bird.getRect()):
                            # this parrot is no more
                            numHits+=1
                            bird.setYSpeed(1)
                            bird.setAlive(False)
                            if bird.getSound() != None:
                                bird.stopSound()
                            shotScore += bird.getXSpeed()
                            self.hits += 1
                    for a in animals:
                        if self.rect.colliderect(a.getRect()):
                            numHits += 1
                            a.setAlive(False)
                            if a.getXSpeed() < 0:
                                shotScore -= a.getXSpeed()
                            else:
                                shotScore += a.getXSpeed()
                            self.hits += 1
                    
                if numHits > 1:
                    self.score += 2 * shotScore
                    self.bangs.add(Bang(self.rect.center, str(2 * shotScore)))
                elif numHits == 0:
                    self.bangs.add(Bang(self.rect.center, str(-1)))
                    self.score -= 1
                    self.misses += 1
                else:
                    self.bangs.add(Bang(self.rect.center, str(shotScore)))
                    self.score += shotScore   
                self.shots -= 1
            
            
    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        self.checkPos()
        self.bangs.update()
        
    def checkPos(self):
        if self.rect.centerx > self.screen.get_width():
            self.rect.centerx = self.screen.get_width()
        if self.rect.centerx < 0:
            self.rect.centerx = 0
        if self.rect.centery > self.screen.get_height():
            self.rect.centery = self.screen.get_height()
        if self.rect.centery < 0:
            self.rect.centery = 0
            

class Reload(pygame.sprite.Sprite):
    """ a sprite for reloading weapon
        just an image of a bullet to be shot at at """
    def __init__(self):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img" + os.sep + "bullet.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = 500
        self.rect.y = 470
    
    def getRect(self):
        return self.rect
    
    def getImage(self):
        return self.image

class Cloud(pygame.sprite.Sprite):
    
    def __init__(self, size, screen):
    
        pygame.sprite.Sprite.__init__(self)       
        self.image = pygame.image.load("img" + os.sep + "%scloud.bmp" % size).convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = screen.get_width()
        self.rect.y = random.randint(10, 150)
        self.xspeed = random.randint(1, 3)
        self.yspeed = random.randint(1, 4)
        self.screen = screen
        
    def update(self):
    
        self.rect.x -= self.xspeed
        if random.randint(1, 4) == 1:
            if random.randint(1, 2) == 1:
                self.rect.y -= self.yspeed
            else:
                self.rect.y += self.yspeed
        
        if self.rect.right < 0:
            self.reset()
            
    def reset(self):
    
        self.rect.x = self.screen.get_width()
        self.rect.y = random.randint(10, 150)
        self.xspeed = random.randint(1, 3)
        self.yspeed = random.randint(1, 4)
        
    def getRect(self):
        return self.rect
        
        
class Bird(pygame.sprite.Sprite):
    """class of flying enemy. base class, to be extended by breed"""
    
    def __init__(self, breed, screen):
        
        pygame.sprite.Sprite.__init__(self)
        # load images
        self.imageMaster = pygame.image.load("img" + os.sep + "%s1.bmp" % breed).convert()
        self._imageMaster = pygame.image.load("img" + os.sep + "%s2.bmp" % breed).convert()
        # set random xspeed and yspeed
        self.xspeed = random.randint(3, 6)
        self.yspeed = 0
        # change size of bird according to speed
        self.image = pygame.transform.rotozoom(self.imageMaster, 0, self.xspeed / 3)
        self._image = pygame.transform.rotozoom(self._imageMaster, 0, self.xspeed / 3) 
        # make background transparent
        self._image.set_colorkey((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        # get rect and randomly set location
        self.rect = self.image.get_rect()
        self.rect.right = 0
        self.rect.y = random.randint(15, 200)
        # other initialising
        self.alive = True
        self.worth = self.xspeed
        self.frame = 0
        self.screen = screen
        
    def update(self, target):
        """update bird, called once a frame """
        
        # move bird to left and increase frame count for flapping wings
        self.rect.x += self.xspeed
        self.frame += 1
        
        # bird made it all the way to the end, reset
        if self.rect.left > self.screen.get_width() and self.alive:
            target.moreEscaped()
            self.reset()
            
        # move bird down, if yspeed non-zero
        self.rect.y += self.yspeed
        
        # if bird is falling, accelerate
        if self.yspeed > 0:
            self.yspeed *= 1.33

        
        # if bird fell off the bottom, reset
        if self.rect.top > 400:
            self.reset()
        
        # if bird is alive, flap wings and quack
        if self.alive == True and self.frame == 10:
        
            if self.birdSound != None:
                if random.randint(1, 9) == 1:
                    self.birdSound.play()
            self.frame = 0
            temp = self.image
            self.image = self._image
            self._image = temp  
    
    def reset(self):
        """ give all new inital data to bird which has died or escaped"""
        
        self.xspeed = random.randint(3, 7)
        self.image = pygame.transform.rotozoom(self.imageMaster, 0, self.xspeed / 3)
        self._image = pygame.transform.rotozoom(self._imageMaster, 0, self.xspeed / 3)
        self.image.set_colorkey((0, 0, 0))
        self._image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.frame = 0
        self.rect.right = 0
        self.rect.y = random.randint(15, 200)
        self.yspeed = 0
        self.alive = True
        
    def getXSpeed(self):
        return self.xspeed

    def getRect(self):
        return self.rect
    
    def getSound(self):
        return self.birdSound
    
    def stopSound(self):
        self.birdSound.stop()
        
    def setYSpeed(self, speed):
        self.yspeed = speed
    
    def setAlive(self, living):
        self.alive = living

class Duck(Bird):
    def __init__(self, screen):
        Bird.__init__(self, "duck", screen)
        if pygame.mixer is not None:
            self.birdSound = pygame.mixer.Sound("wav"+os.sep+"quack.wav")
        else:
            self.birdSound = None
            
class Hawk(Bird):
    def __init__(self, screen):
        Bird.__init__(self, "hawk", screen)
        self.birdSound = None
        
        
class Animal(pygame.sprite.Sprite):

    def __init__(self, screen):
        
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.images = self.loadImages()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.maxSpeed = 10
        self.minSpeed = 4
        self.xspeed = random.choice(range(-self.maxSpeed, -self.minSpeed) + range(self.minSpeed, self.maxSpeed))
        self.rect.y = random.randint(300, 400)
        if self.xspeed > 0:
            self.rect.right = 0
            for i in xrange(len(self.images)):
                self.images[i] = pygame.transform.flip(self.images[i], True, False)
                self.image = self.images[0]
        if self.xspeed < 0:
            self.rect.left = self.screen.get_width() 
        self.frame = 0
        self.alive = True
        self.delay = 10
        self.pause = 0

    def update(self, target):
        
        if self.alive == True:
            self.pause +=1
            if self.pause == self.delay:
                self.pause = 0
                self.frame+=1
                
                if self.frame > len(self.images) - 1:
                    self.frame = 0
              
                self.image = self.images[self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center
                self.rect.x += self.xspeed
                
                if (self.rect.right < 0 and self.xspeed < 0 and self.alive) or (self.rect.left > self.screen.get_width() and self.xspeed > 0 and self.alive):
                    target.moreEscaped()
                    self.reset()
        else:
            self.reset()
     
    def reset(self):
        self.images = self.loadImages()
        self.xspeed = random.choice(range(-self.maxSpeed, -self.minSpeed) + range(self.minSpeed, self.maxSpeed))
        self.rect.y = random.randint(300, 400)
        if self.xspeed > 0:
            self.rect.right = 0
            for i in xrange(len(self.images)):
                self.images[i] = pygame.transform.flip(self.images[i], True, False)
                self.image = self.images[0]
        if self.xspeed < 0:
            self.rect.left = self.screen.get_width() 
        self.image = self.images[0]
        self.alive = True

    def loadImages(self):
        pass

    def setAlive(self, living):
        self.alive = living

    def getXSpeed(self):
        return self.xspeed

    def getRect(self):
        return self.rect

class Frog(Animal):
    
    def __init__(self, screen):
        Animal.__init__(self, screen)

    def loadImages(self):
        images = []
        for i in xrange(4):
            tmpImage = pygame.image.load("img" + os.sep + "frog%d.bmp" % i).convert()
            tmpImage.set_colorkey((0, 0, 0))
            images.append(tmpImage)
        return images

class Cat(Animal):

    def __init__(self, screen):
        Animal.__init__(self, screen)
        self.xspeed *= 5
        self.maxSpeed *= 5
        self.minSpeed *= 5
    def loadImages(self):
        images = []
        for i in xrange(6):
            tmpImage = pygame.image.load("img" + os.sep + "cat%d.bmp" % i).convert()
            tmpImage = pygame.transform.flip(tmpImage, True, False)
            tmpImage.set_colorkey((0, 0, 0))
            images.append(tmpImage)
        return images
    
    def reset(self):
        self.kill()

class Snail(Animal):

    def __init__(self, screen):
        Animal.__init__(self, screen)
        
    def loadImages(self):
        images = []
        for i in xrange(4):
            tmpImage = pygame.image.load("img" + os.sep + "snail%d.bmp" % i).convert()
            tmpImage.set_colorkey((0, 0, 0))
            images.append(tmpImage)
        return images

class Turtle(Animal):

    def __init__(self, screen):
        Animal.__init__(self, screen)
        
    def loadImages(self):    
        images = []
        for i in xrange(4):
            tmpImage = pygame.image.load("img" + os.sep + "turtle%d.bmp" % i).convert()
            tmpImage.set_colorkey((0, 0, 0))
            images.append(tmpImage)
        return images


class Snake(Animal):

    def __init__(self, screen):
        Animal.__init__(self, screen)
        
    def loadImages(self):
        images = []
        for i in xrange(7):
            tmpImage = pygame.image.load("img" + os.sep + "snake%d.bmp" % i).convert()
            tmpImage.set_colorkey((0, 0, 0))
            images.append(tmpImage)
        return images
        


class ScoreTable():
    """ class to load and display high scores
        loads a pickled list of tuples
        generates labels
        checks users score against current high scores
            if bigger score than bottom score
                add to list
                sort list
                remove last entry
        write data to file
        persistence is key
        """                
    def __init__(self):
        # new scoreboard game object
        self.highScores = self.loadData() # load pickled list
        self.labels = self.getLabels() # get labels from list

    def update(self):
        # make sure all is current
        self.highScores = self.loadData()
        self.labels = self.getLabels()
                                
    def checkScore(self, score):
        # is score better than worst?
        if score >= self.highScores[-1][0]:
            # yes, get name
            name = self.getName(score)
            # add details to list
            self.highScores.append((score, name, time.strftime("%d/%m %H:%M")))
            self.highScores.sort()
            self.highScores.reverse()
            self.highScores = self.highScores[:9] # just the top ten
            self.writeData() # new list to file
            self.update() # new details in scoreTable
        
    def getHighScore(self):
        return self.highScores[0][0]
    
    def getLabels(self):
        """ generate labels and place in group """
        
        labels = pygame.sprite.Group()
        lineCount = 2 # start a bit down the screen
        for score in self.highScores:
            tmpLabel = Label(40)
            tmpLabel.setText("%d - %s - %s"% (score[0], score[1], score[2]))
            tmpLabel.setColour((0, 0, 0))
            tmpLabel.setCenter((400, 40 * lineCount))
            labels.add(tmpLabel) # add this label
            lineCount += 1 # move down screen
        return labels               
    
    def writeData(self):
        # open scores file and write pickled list
        try:
            fileObj = open("scores.p", "w")
            cPickle.dump(self.highScores, fileObj)
            fileObj.close()
        except IOError:
            print "can't write high scores exiting..."
            exit()
            
    def loadData(self):
        # open file and get pickled list
        try:
            fileObj = open("scores.p")
            data = cPickle.load(fileObj)
            fileObj.close()
        except IOError:
            data = None
        return data
    
    def getName(self, score):
        """ function to get high scoring user's name """
        # display
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("High Score - Enter Name")
        # background
        bg = pygame.image.load("img" + os.sep + "bg.bmp")
        # clock
        clock = pygame.time.Clock()
        
        clouds = pygame.sprite.Group()
        for i in xrange(4):
            cloud = random.choice([Cloud("large", screen), Cloud("small", screen)])
            clouds.add(cloud)
            
        target = Target("shotgun", screen)
        # labels and value-ising
        lblScore = Label(45)
        lblScore.setText("New High Score: %d." % (score))
        lblScore.setCenter((400, 55))
        lblScore.setColour((0, 0, 0))
        lblPrompt = Label(45)
        lblPrompt.setText("Enter Your Name...")
        lblPrompt.setCenter((400, 100))
        lblPrompt.setColour((0, 0, 0))
        lblName = Label(35)
        lblName.setCenter((400, 150))
        lblName.setColour((0, 0, 0))
    
        labels = pygame.sprite.Group(lblScore, lblPrompt, lblName)
    
        # main loop control and new name string
        gettingName = True
        name = u""
    
        while gettingName:
            clock.tick(30)
            screen.fill((0, 0, 0))
            screen.blit(bg, (0, 0))
        
            # check user input
            for event in pygame.event.get():
                # quit, back to menu and christen anon
                if event.type == pygame.QUIT:
                    exit()
                    
                # if typing add key to name string    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        name = name[:-1] # last char remove
                    elif event.key == pygame.K_ESCAPE:
                        gettingName = False
                        name = "anon"
                    elif event.key == pygame.K_RETURN:
                        gettingName = False # name finished
                    else:
                        if len(name) < 20:
                            name = name + event.unicode
                        
            # give name label current name value
            lblName.setText(name)    
            
            target.update()
            clouds.update()
            clouds.draw(screen)
            target.draw(screen)
            # update and display labels
            labels.update()
            labels.draw(screen)
         
            pygame.display.flip() # display frame
                
        return name # final name for user
        
    def showHighScores(self):
        """ function to display high score table
            data loaded from pickled list """
        # set up display and create new background    
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("YACHunt - High Scores")
        bg = pygame.image.load("img" + os.sep + "bg.bmp")

        clouds = pygame.sprite.Group()
        for i in xrange(4):
            cloud = random.choice([Cloud("large", screen), Cloud("small", screen)])
            clouds.add(cloud)
            
        target = Target("shotgun", screen)
        clock = pygame.time.Clock() # clock object    
    
        # table heading
        heading = Label(40)
        heading.setText("Score - Player - Time")
        heading.setCenter((400, 45))
        heading.setColour((0, 0, 0))
    
        pygame.mouse.set_visible(False) # hide mouse
    
        showHS = True # main loop control
        while showHS:
    
            clock.tick(30) # 30 fps
            
            # if quit or click, back to menu
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit()
                    elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or event.type == pygame.MOUSEBUTTONDOWN:
                        showHS = False
                        pygame.display.set_caption("YACHunt...Choose Your Weapon")

            
            screen.fill((0, 0, 0))
            screen.blit(bg, (0, 0)) # clear screen
            clouds.update()
            clouds.draw(screen)
            target.update()
            target.draw(screen)
            #render heading and draw
            heading.update()
            heading.draw(screen)
            # labels from score board, render then draw
            self.labels.update()
            self.labels.draw(screen)
        
            pygame.display.flip() # display frame
