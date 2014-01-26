import pygame

class Game(object):
	def main(self,screen):
		clock = pygame.time.Clock()

		# loading materials	
		from pytmx import tmxloader
		tmxdata = tmxloader.load_pygame("../materials/map.tmx", pixelalpha=True)

		soldier_pos_x = 0
		soldier_pos_y = 0
		
		#--------------------- background = Map("../materials/back.txt",tileset)
		#-------------------- foreground = Map("../materials/front.txt",tileset)

		while True:
			clock.tick(30)

			# Event handling
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return

				if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					return

			key = pygame.key.get_pressed()

			if key[pygame.K_w]:
				soldier_pos_y -= 10

			if key[pygame.K_s]:
				soldier_pos_y += 10

			if key[pygame.K_a]:
				soldier_pos_x -= 10

			if key[pygame.K_d]:
				soldier_pos_x += 10
			
			###############################################################################################
			# Game logics
			###############################################################################################
			
						
			###############################################################################################
			# Graphics
			###############################################################################################
			
			# set background color
			screen.fill((47,129,54))
			
			tw = tmxdata.tilewidth
			th = tmxdata.tileheight
			gt = tmxdata.getTileImage
						
			for l in xrange(0, len(tmxdata.tilelayers)):
				for y in xrange(0, tmxdata.height):
					for x in xrange(0, tmxdata.width):
						tile = gt(x, y, l)
						if tile: screen.blit(tile, (x*tw, y*th))
			
			# background tileset
			#---------------------------------------- background.drawMap(screen)
			pygame.display.flip()
			
class TileSet(object):
	def __init__(self):
		self.images = {}
		self.tiles = {}
		
	# function for adding tilesets from a file
	def addTileSet(self,filename,prefix):		
		newTiles = pygame.image.load(filename)
		dimensions = newTiles.get_rect().size
		
		# add image to dictionary of images
		self.images[prefix] = newTiles
		
		# find number of tiles (assuming tiles are 32x32 pixels)
		count_x = dimensions[0] / 32
		count_y = dimensions[1] / 32
		
		# add tile to dictionary of tiles
		for i in range(0,count_x):
			for j in range(0,count_y):
				self.tiles[prefix+str(i+count_x*j)] = (i*32,j*32)
	
	# function to blit a tile to a surface
	def blitTile(self,surface,pos,name):
		prefix = name[0]
		pos_of_tile = self.tiles[name]
		src_image = self.images[prefix]
		surface.blit(src_image,pos,pygame.Rect(pos_of_tile, (32, 32)))
			
class Map(object):
	def __init__(self,area,tileset):						
		self.area = [line.strip().split() for line in open(area)]
		self.tileset = tileset
		
	# function to draw the whole map on a surface
	def drawMap(self,surface):
		i = j = 0
		for row in self.area:
			for tilename in row:
				self.tileset.blitTile(surface, (j*32,i*32), tilename)
				j += 1
			i += 1
			j = 0

class Player(object):	
	def __init__(self):
		self.human = True


if __name__ == '__main__':
		pygame.init()
		screen = pygame.display.set_mode((1280,768))
		Game().main(screen)
