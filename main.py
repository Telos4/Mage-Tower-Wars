import pygame

class Game(object):
	def main(self,screen):
		clock = pygame.time.Clock()
		

		
		# loading materials	
		from pytmx import tmxloader
		tmxdata = tmxloader.load_pygame("../materials/map.tmx", pixelalpha=True)
		
		searchGraph = NodeGraph()
		
		for og in tmxdata.objectgroups:
			for o in og:
				if hasattr(o,'spawn'):
					print o
				if hasattr(o,'buildarea'):
					print (o.x, o.y, o.width, o.height)
				if hasattr(o,'walkable'):
					searchGraph.addNodes((o.x, o.y, o.width, o.height))
				if hasattr(o,'main'):
					print o.main
		
		# create map with tiles
		areaMap = Map(tmxdata)
		
		# set up camera
		camera = Camera(screen.get_size(),areaMap.getDimensions())

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
			
						
			###############################################################################################
			# Graphics
			###############################################################################################
			
			# set background color
			screen.fill((47,129,54))
			
			# draw map to screen, using the settings of the camera
			areaMap.drawMap(screen,camera)
			
			# plot nodes of search graph (for debugging purposes)
			searchGraph.plotNodes(screen,camera)
			
			# background tileset
			#---------------------------------------- background.drawMap(screen)
			pygame.display.flip()
			
class NodeGraph(object):
	def __init__(self):
		self.nodes = []
		self.radius_of_nodes = 20
		
	def addNodes(self,area):
		# work only for rectangular areas
		area_x = area[0]
		area_y = area[1]
		area_width = area[2]
		area_height = area[3]
		
		print area
		
		# problem: nodes are not equally distributed
		i = j = self.radius_of_nodes
		while i < area_width:
			while j < area_height:
				newNode = Node(area_x + i,area_y + j,self.radius_of_nodes,len(self.nodes))
				self.nodes.append(newNode)
				j += 2*self.radius_of_nodes
			j = self.radius_of_nodes
			i += 2*self.radius_of_nodes
			
		print "number of nodes:", len(self.nodes)
			
		# connect nodes that are close to each other
		for node1 in self.nodes:
			for node2 in self.nodes:
				node1.connect(node2)				
		# after the graph has been created it can be saved and loaded -> doesn't have to be created at every start of the game
				
	def plotNodes(self,screen,camera):
		for node in self.nodes:
			node.plot(screen,camera)
			
		
class Node(object):
	def __init__(self,pos_x, pos_y, radius, identifier):
		self.radius = radius
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.identifier = identifier
		self.neighbors = []
		self.traversable = True
		
		print "id of node:", self.identifier
		
	def connect(self,otherNode):
		if (self != otherNode):		
			# if otherNode is not already neighbor
			if not (otherNode in self.neighbors):
				# check if node is close enough for connection
				if (self.pos_x - otherNode.pos_x)*(self.pos_x - otherNode.pos_x) + (self.pos_y - otherNode.pos_y)*(self.pos_y - otherNode.pos_y) <= 9 * self.radius*self.radius:
						# register otherNode as neighbor
						self.neighbors.append(otherNode)
						# become neighbor of other node
						otherNode.connect(self)
					
	def plot(self,screen,camera):
		#print "node pos: ", (self.pos_x,self.pos_y)
		#print "number of neighbors: ", len(self.neighbors)
		pygame.draw.circle(screen, pygame.Color(255,255,0,10), (self.pos_x - camera.pos_x,self.pos_y-camera.pos_y), self.radius, 0)
		for neighbor in self.neighbors:
			#print "neighbor pos: ", (neighbor.pos_x,neighbor.pos_y)
			pygame.draw.line(screen, pygame.Color(0,0,0,255), (self.pos_x - camera.pos_x,self.pos_y - camera.pos_y),  (neighbor.pos_x - camera.pos_x,neighbor.pos_y - camera.pos_y), 1)
			
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
	def __init__(self,unit_type):
		self.type = unit_type
		self.hp = 100
		self.speed = 10
		self.pos_x = 10
		self.pos_y = 10
		
	def move(self,x,y):
		self.pos_x = x
		self.pos_y = y

class Player(object):	
	def __init__(self):
		self.human = True


if __name__ == '__main__':
		pygame.init()
		screen = pygame.display.set_mode((600,400))
		Game().main(screen)
