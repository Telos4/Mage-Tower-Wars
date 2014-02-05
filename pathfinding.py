import pygame
import math
import numpy

class NodeGraph(object):
    def __init__(self, triggers):

        self.size_of_nodes = 32
        
        self.start_nodes = []
        self.end_nodes = []
        
        # generate grid
        nodes_x = triggers.width
        nodes_y = triggers.height
        
        walk_areas = []
        for trigger in triggers:
            if hasattr(trigger,'walkable'):
                walk_areas.append(trigger)
        
        self.nodes = {}
        
        # create node grid
        for i in range(0,nodes_x):
            for j in range(0,nodes_y):
                center = (i*32 + 16, j*32 + 16)
                for w in walk_areas:
                    if pygame.Rect(w.x, w.y, w.width, w.height).collidepoint(center):
                        self.nodes[(i,j)] = Node(center,32,len(self.nodes))
                        break

        # connect nodes on grid
        for k,v in self.nodes.iteritems():
            x = k[0]
            y = k[1]
            
            # connect to lower node
            n = self.nodes.get((x,y+1))
            if n != None:
                v.connect(n)         
            # connect to lower-right node
            n = self.nodes.get((x+1,y+1))
            if n != None:
                v.connect(n)
            # connect to right node
            n = self.nodes.get((x+1,y))
            if n != None:
                v.connect(n)
            # connect to upper-right node
            n = self.nodes.get((x+1,y-1))
            if n != None:
                v.connect(n)
            # connect to upper node
            n = self.nodes.get((x,y-1))
            if n != None:
                v.connect(n)
            # connect to upper-left node
            n = self.nodes.get((x-1,y-1))
            if n != None:
                v.connect(n)
            # connect to left node
            n = self.nodes.get((x-1,y))
            if n != None:
                v.connect(n)
            # connect to lower-left node
            n = self.nodes.get((x-1,y+1))
            if n != None:
                v.connect(n)
                                
        # mark start and end nodes
        for trigger in triggers:
            if hasattr(trigger,'spawn'):
                # create new node for start
                s = Node((trigger.x + trigger.width/2,trigger.y + trigger.height/2),self.size_of_nodes,len(self.nodes))
                
                # connect startnode to graph
                for n in self.nodes.itervalues():
                    if abs(n.rect.x - s.rect.x) <= 32 and abs(n.rect.y - s.rect.y) <= 32:
                        s.connect(n)
                        n.connect(s)
                        
                s.startnode = True
                self.start_nodes.append(s)
            if hasattr(trigger,'destination'):
                # create node for destination
                e = Node((trigger.x + trigger.width/2,trigger.y + trigger.height/2),self.size_of_nodes,len(self.nodes))
                
                # connect startnode to graph
                for n in self.nodes.itervalues():
                    if abs(n.rect.x - e.rect.x) <= 32 and abs(n.rect.y - e.rect.y) <= 32:
                        e.connect(n)
                        n.connect(e)
                        
                e.endnode = True
                self.end_nodes.append(e)
        
        # calculate optimal distances between nodes
        self.createPotentialField()
        
        # set optimal direction for each node        
        for node in self.nodes.itervalues():
            node.calcDirection()
        
        # calculate shortest path to end node
        #self.generateNewPaths()
            
    def getDirection(self,pos):
        for node in self.start_nodes:
            if node.rect.collidepoint(pos):
                return None

        for node in self.end_nodes:
            if node.rect.collidepoint(pos):
                    return (0,0)
        n = self.nodes.get((int(pos[0]/32), int(pos[1]/32)))
        if n != None and n.traversable == True:
            return n.direction
        else:
            return None
                        
    def createPotentialField(self):
        for node in self.nodes.itervalues():
            node.pathnode = False
            node.visited = False
            node.potential = 0
        
        # generate potential field (with bfs)
        for end in self.end_nodes:
            path = []
             
            node_queue = [end]
            end.visited = True
             
            i = 255
             
            while not len(node_queue) == 0:
                n = node_queue.pop(0)
                path.append(n)
                i *= 0.999
                n.potential = i
                if n.startnode == True:
                    print "done!"
                for c in n.neighbors:
                    if c.visited == False and c.traversable == True:
                        node_queue.append(c)
                        c.visited = True
                    
        #generate path
        for node in self.start_nodes:
            nextn = node
            while not nextn in self.end_nodes:
                nextn.pathnode = True
                nextn = nextn.getMaxNeighbor()
        
    def makeImpassable(self,pos):
        print "imp"
        print "pos: ", pos
        # find node at position
        for node in self.nodes.itervalues():
            if node.rect.collidepoint(pos):
                node.traversable = False
                print "node ", node.rect.center
        
        # update potential field
        self.createPotentialField()
        
        # set optimal direction for each node        
        for node in self.nodes.itervalues():
            node.calcDirection()
        
        # generate new path
        #self.generateNewPaths()
            
                
    def generateNewPaths(self):        
        # delete old path
        self.path = []
        for node in self.nodes:
            node.pathnode = False
        
        # find startnode 1
        current = self.start_nodes[0]
        
        # find best neighbor of every node until destination is reached
        while current.endnode == False:
            self.path.append(current)
            current.pathnode = True
            current = current.getMaxNeighbor()
            #if current.endnode = True:
        # add last node to path
        self.path.append(current)
        
        # find startnode 2
        current = self.start_nodes[1]
        
        # find best neighbor of every node until destination is reached
        while current.endnode == False:
            self.path.append(current)
            current.pathnode = True
            current = current.getMaxNeighbor()
            #if current.endnode = True:
        # add last node to path
        self.path.append(current)
        
    def handleCollision(self,pos,radius):
        for node in self.nodes.itervalues():
            if node.traversable == False:                
                # vector from center of unit to center of obstacle
                v = numpy.array(pos - node.rect.center)
                
                # distance between creep and center of node (= length of v)
                d = numpy.linalg.norm(v)
                # maximum allowed distance            
                m = radius + node.rect.size[0]/math.sqrt(2)
                
                # check if collision occurs
                if d <= m:
                    # if so calculate shift vector
                    e = v/d
                    v = e * (m-d)
                    
                    return v
        # if no collision occurs, return None
        return None
    
    def atEndNode(self,pos):
        for node in self.end_nodes:
            if node.rect.collidepoint(pos):
                print "endnode reached!"
                return True
        return False
        
                
    def plotNodes(self,screen,camera):
        for n in self.nodes.itervalues():
            n.plot(screen,camera)
            
        
class Node(object):
    def __init__(self,pos, size, identifier):
        self.rect = pygame.Rect(0,0,0,0)
        self.rect.size  = (size,size)
        self.rect.center = pos
        
        self.identifier = identifier
        self.neighbors = []
        
        self.traversable = True
        self.startnode = False
        self.endnode = False
        self.visited = False
        
        self.pathnode = False
        
        self.potential = 0
        
        self.direction = numpy.array((0,0))
        #print "id of node:", self.identifier      
        
                        
    def connect(self,other):
        self.neighbors.append(other)
                        
    def getMaxNeighbor(self):
        maxpot = 0
        for node in self.neighbors:
            if node.potential >= maxpot:
                maxnode = node
                maxpot = node.potential
        return maxnode
        
    def calcDirection(self):
        if self.endnode:
            self.direction = (0.0,0.0)
            return
        
        neighbor = self.getMaxNeighbor()
        if neighbor != None:
            x = neighbor.rect.x - self.rect.x
            y = neighbor.rect.y - self.rect.y
            abs_ = math.sqrt(x*x + y*y)
            self.direction = (x/abs_ , y/abs_)
        else:
            print "error: no neighbor at: " ,(self.pos_x, self.pos_y)
            print "node is not connected to graph!!"
                    
    def plot(self,screen,camera):
        #print "node pos: ", (self.pos_x,self.pos_y)
        #print "number of neighbors: ", len(self.neighbors)
        #pygame.draw.line(screen, pygame.Color(0,0,0,255), (self.rect.x - camera.pos_x,self.rect.y - camera.pos_y),  (self.rect.x + int(self.direction[0]*100) - camera.pos_x,self.rect.y + int(self.direction[1]*100) - camera.pos_y), 1)
        colorgradient = int(self.potential)
        c = pygame.Color(colorgradient,colorgradient,colorgradient,10)
        
        camx = camera.pos[0]
        camy = camera.pos[1]
        
        pygame.draw.circle(screen, c, (self.rect.centerx - camx,self.rect.centery-camy), self.rect.size[0]/2, 0)
        
        #pygame.draw.rect(screen,c,self.rect,0)

        #for n in self.neighbors:
            #pygame.draw.line(screen, pygame.Color(0,0,0,255), (self.rect.centerx - camx,self.rect.centery - camy),  (n.rect.centerx - camx,n.rect.centery - camy), 1)

        if self.pathnode == True:
            c = pygame.Color(0,0,0,10)
            #pygame.draw.rect(screen, c, ((self.rect.x - self.rect.w/2) - camera.pos_x,(self.rect.y - self.rect.w/2) - camera.pos_y,self.rect.w,self.rect.w), 0)
            pygame.draw.circle(screen, pygame.Color(0,128,0,10), (self.rect.centerx - camera.pos[0],self.rect.centery-camera.pos[1]), self.rect.w/2, 0)
            return
        
        return
        
        if self.startnode == False and self.endnode == False:
            colorgradient = int((self.potential)*255/10000)
            c = pygame.Color(colorgradient,255 - colorgradient,255 - colorgradient,10)
            #print colorgradient
            #pygame.draw.rect(screen, c, ((self.rect.x - self.rect.w/2) - camera.pos_x,(self.rect.y-self.rect.w/2) - camera.pos_y,self.rect.w,self.rect.w), 0)
            pygame.draw.circle(screen, pygame.Color(colorgradient,255 - colorgradient,255 - colorgradient,10), (self.pos_x - camera.pos_x,self.pos_y-camera.pos_y), self.radius/4, 0)
        elif self.startnode == True:
            pygame.draw.circle(screen, pygame.Color(0,0,255,10), (self.rect.x - camera.pos_x,self.rect.y-camera.pos_y), self.rect.w/2, 0)
        elif self.endnode == True:
            pygame.draw.circle(screen, pygame.Color(255,0,0,10), (self.rect.x - camera.pos_x,self.rect.y-camera.pos_y), self.rect.w/2, 0)
        
        
        pygame.draw.line(screen, pygame.Color(0,0,0,255), (self.rect.x - camera.pos_x,self.rect.y - camera.pos_y),  (self.rect.x + int(self.direction[0]*100) - camera.pos_x,self.rect.y + int(self.direction[1]*100) - camera.pos_y), 1)

        