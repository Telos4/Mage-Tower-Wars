import pygame

class Game(object):
	def main(self,screen):
		clock = pygame.time.Clock()
		
		# loading materials	
		from pytmx import tmxloader
		tmxdata = tmxloader.load_pygame("../materials/map.tmx", pixelalpha=True)
		
		# create map with tiles
		areaMap = Map(tmxdata)
		
		# set up camera
		disp_info = pygame.display.Info()
		camera = Camera((disp_info.current_w,disp_info.current_h),areaMap.getDimensions())

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

class Player(object):	
	def __init__(self):
		self.human = True


if __name__ == '__main__':
		pygame.init()
		screen = pygame.display.set_mode((1280,768))
		Game().main(screen)
