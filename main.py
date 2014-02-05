import pygame
import numpy
import pathfinding
import random

class Game(object):
	def main(self,screen):
		clock = pygame.time.Clock()
		
		# loading materials	
		from pytmx import tmxloader
		tmxdata = tmxloader.load_pygame("../materials/map.tmx", pixelalpha=True)
		
		# get trigger layer
		for og in tmxdata.objectgroups:
			if hasattr(og,'triggers'):
				triggers = og
		
		
		# create search graph for pathfinding
		searchGraph = pathfinding.NodeGraph(triggers)
		
		#spawn_1 = searchGraph.start_nodes[0]
		#spawn_2 = searchGraph.start_nodes[1]
		
		creeps = []
		
		# create map with tiles
		areaMap = Map(tmxdata)
		
		# set up camera
		camera = Camera(screen.get_size(),areaMap.getDimensions())
		
		clock.tick()
		while True:
			dt = clock.tick()/1000.0	# calculate time in seconds since last frame	
			
			#print "fps:", clock.get_fps()
			
			mousePosition = pygame.mouse.get_pos()

			# Event handling
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return

				if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					return
				
				if event.type == pygame.MOUSEBUTTONDOWN:
					button_states = pygame.mouse.get_pressed()
					if button_states[0]:
						creeps.append(Creep(1,(mousePosition[0]+camera.pos[0],mousePosition[1]+camera.pos[1])))
					elif button_states[2]:
						searchGraph.makeImpassable((mousePosition[0]+camera.pos[0],mousePosition[1]+camera.pos[1]))
				
			#if pygame.key.get_pressed()[pygame.K_c]:
				#creeps.append(Creep(1,spawn_1.pos_x,spawn_1.pos_y))
				#creeps.append(Creep(1,spawn_2.pos_x,spawn_2.pos_y))
			
			
			
			# mouse scrolling	
			camera.scroll(mousePosition)


			
			###############################################################################################
			# Game logics
			###############################################################################################
			
			# move all creeps according to their tiles optimal directions
			for creep in creeps:
				d = searchGraph.getDirection(creep.pos)
				creep.move(d,dt)
				
			# check for collisions
			for creep in creeps:
				v = searchGraph.handleCollision(creep.pos,creep.size)				
				if v != None:
					creep.shift(v)
					
			# delete nodes that reached endnode
			for creep in creeps:
				if searchGraph.atEndNode(creep.pos):
					creeps.remove(creep)
					#del creep
				
			
			#print direct
			#print "creep at:", (goblin.pos_x, goblin.pos_y)
						
			###############################################################################################
			# Graphics
			###############################################################################################
			
			# set background color
			screen.fill((0,0,0))
			
			# draw map to screen, using the settings of the camera
			areaMap.drawMap(screen,camera)
			
			# plot nodes of search graph (for debugging purposes)
			searchGraph.plotNodes(screen,camera)
			
			# draw all towers
			
			# draw all creatures			
			for creep in creeps:
				creep.plot(screen,camera)
			
			# draw all special effects (arrows, missles, etc.)
			
			# background tileset
			#---------------------------------------- background.drawMap(screen)
			pygame.display.flip()
			
			
class Map(object):
	def __init__(self,tmxdata):
		self.tmxdata = tmxdata
		
	def getDimensions(self):
		return (self.tmxdata.width*self.tmxdata.tilewidth,self.tmxdata.height*self.tmxdata.tileheight)
		
	def drawMap(self,screen,camera):
		tw = self.tmxdata.tilewidth
		th = self.tmxdata.tileheight
		gt = self.tmxdata.getTileImage
					
		for l in xrange(0, len(self.tmxdata.tilelayers)):
			for y in xrange(0, self.tmxdata.height):
				for x in xrange(0, self.tmxdata.width):
					tile = gt(x, y, l)
					if tile: screen.blit(tile, (x*tw - camera.pos[0], y*th - camera.pos[1]))
			
class Camera(object):
	def __init__(self,display_dimensions,map_dimensions):
		self.display_width = display_dimensions[0]
		self.display_height = display_dimensions[1]
		
		self.pos = numpy.array((0,0))
		
		self.margin = 25
		self.scrollspeed = 50
		
		self.map_width = map_dimensions[0]
		self.map_height = map_dimensions[1]
				
	def scroll(self,mousePosition):
			if mousePosition[0] < self.margin:
				if self.pos[0] - self.scrollspeed >= 0:
					self.pos[0] -= self.scrollspeed
				else:
					self.pos[0] = 0
			elif mousePosition[0] > self.display_width - self.margin:
				if self.pos[0] + self.display_width + self.scrollspeed <= self.map_width:
					self.pos[0] += self.scrollspeed
				else:
					self.pos[0] = self.map_width - self.display_width
				
			if mousePosition[1] < self.margin:
				if self.pos[1] - self.scrollspeed >= 0:
					self.pos[1] -= self.scrollspeed
				else:
					self.pos[1] = 0
			elif mousePosition[1] > self.display_height - self.margin:
				if self.pos[1] + self.display_height + self.scrollspeed <= self.map_height:
					self.pos[1] += self.scrollspeed
				else:
					self.pos[1] = self.map_height - self.display_height
					
class Creep(object):
	def __init__(self,unit_type,pos):
		self.type = unit_type
		self.hp = 100
		self.speed = 100
		self.size = 5
		
		self.pos = numpy.array(pos)		# position of the creep on the map
		self.vel = numpy.array([0,0])	# velocity of the creep in pixels per second
	
	def move(self,direction,dt):
		if direction != None:
			self.vel = numpy.array(direction) * self.speed	# update velocity of creep
		self.pos += dt * self.vel	# update position
			
				
	def shift(self,v):		
		self.pos += v
		
	def plot(self,screen,camera):
		#print "pos:", self.pos
		#print "cam:", camera.pos
		#print (int(self.pos[0] - camera.pos[0]),int(self.pos[1]-camera.pos[1]))
		pygame.draw.circle(screen, pygame.Color(255,0,0,0), (int(self.pos[0] - camera.pos[0]),int(self.pos[1]-camera.pos[1])), self.size, 0)
		
		# plot direction the character is facing in (for debugging purposes)
		pygame.draw.line(screen, pygame.Color(0,255,0,255), (int(self.pos[0] - camera.pos[0]),int(self.pos[1] - camera.pos[1])),  (int(self.pos[0] + self.vel[0] - camera.pos[0]),int(self.pos[1] + self.vel[1] - camera.pos[1])), 1)

class Player(object):	
	def __init__(self):
		self.human = True
		
		self.units = []
		self.towers = []


if __name__ == '__main__':
		pygame.init()
		screen = pygame.display.set_mode((1280,768))
		Game().main(screen)
