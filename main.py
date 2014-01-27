import pygame
import pathfinding

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
		
		#searchGraph.createPotentialField()
		
		searchGraph.generateNewPaths()
		
		spawn_1 = searchGraph.start_nodes[0]
		
		goblin = Creep(1,spawn_1.pos_x,spawn_1.pos_y)
		
		# create map with tiles
		areaMap = Map(tmxdata)
		
		# set up camera
		camera = Camera(screen.get_size(),areaMap.getDimensions())
		
		direct = (0,0)

		while True:
			clock.tick(30)

			# Event handling
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return

				if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					return
			
			mousePosition = pygame.mouse.get_pos()
			
			# mouse scrolling	
			camera.scroll(mousePosition)


			
			###############################################################################################
			# Game logics
			###############################################################################################
			newDirect = searchGraph.getDirection(goblin.pos_x, goblin.pos_y)
			if newDirect != None:
				direct = newDirect
			
			#print direct
			#print "creep at:", (goblin.pos_x, goblin.pos_y)
			
			goblin.move(direct)
						
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
			goblin.plot(screen,camera)
			
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
					if tile: screen.blit(tile, (x*tw - camera.pos_x, y*th - camera.pos_y))
			
class Camera(object):
	def __init__(self,display_dimensions,map_dimensions):
		self.display_width = display_dimensions[0]
		self.display_height = display_dimensions[1]
		
		self.pos_x = 0
		self.pos_y = 0
		
		self.margin = 25
		self.scrollspeed = 50
		
		self.map_width = map_dimensions[0]
		self.map_height = map_dimensions[1]
				
	def scroll(self,mousePosition):
			if mousePosition[0] < self.margin:
				if self.pos_x - self.scrollspeed >= 0:
					self.pos_x -= self.scrollspeed
				else:
					self.pos_x = 0
			elif mousePosition[0] > self.display_width - self.margin:
				if self.pos_x + self.display_width + self.scrollspeed <= self.map_width:
					self.pos_x += self.scrollspeed
				else:
					self.pos_x = self.map_width - self.display_width
				
			if mousePosition[1] < self.margin:
				if self.pos_y - self.scrollspeed >= 0:
					self.pos_y -= self.scrollspeed
				else:
					self.pos_y = 0
			elif mousePosition[1] > self.display_height - self.margin:
				if self.pos_y + self.display_height + self.scrollspeed <= self.map_height:
					self.pos_y += self.scrollspeed
				else:
					self.pos_y = self.map_height - self.display_height
					
class Creep(object):
	def __init__(self,unit_type,pos_x,pos_y):
		self.type = unit_type
		self.hp = 100
		self.speed = 5
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.direction = (0,0)
		
	def move(self, direction):
		self.direction = direction
		self.pos_x += direction[0] * self.speed
		self.pos_y += direction[1] * self.speed
		
	def plot(self,screen,camera):
		pygame.draw.circle(screen, pygame.Color(255,255,255,10), (int(self.pos_x - camera.pos_x),int(self.pos_y-camera.pos_y)), 5, 0)
		pygame.draw.line(screen, pygame.Color(0,255,0,255), (int(self.pos_x - camera.pos_x),int(self.pos_y - camera.pos_y)),  (int(self.pos_x + self.direction[0]*100 - camera.pos_x),int(self.pos_y + self.direction[1]*100 - camera.pos_y)), 1)

class Player(object):	
	def __init__(self):
		self.human = True


if __name__ == '__main__':
		pygame.init()
		screen = pygame.display.set_mode((800,600))
		Game().main(screen)
