import pygame
import math

class NodeGraph(object):
    def __init__(self, triggers):
        self.nodes = []
        self.radius_of_nodes = 40
        
        self.start_nodes = []
        self.end_nodes = []
        
        # create nodes    
        for trigger in triggers:
            if hasattr(trigger,'walkable'):
                self.addNodes((trigger.x, trigger.y, trigger.width, trigger.height))
            #if hasattr(trigger,'poly'):
                #print (trigger.x,trigger.y)
                #print trigger.points
        
        # mark start and end nodes
        for trigger in triggers:
            if hasattr(trigger,'spawn'):
                # create new node for start
                newNode = Node(trigger.x + trigger.width/2,trigger.y + trigger.height/2,self.radius_of_nodes,len(self.nodes))
                newNode.startnode = True
                self.nodes.append(newNode)
                self.start_nodes.append(newNode)
            if hasattr(trigger,'destination'):
                # create node for destination
                newNode = Node(trigger.x + trigger.width/2,trigger.y + trigger.height/2,self.radius_of_nodes,len(self.nodes))
                newNode.endnode = True
                self.nodes.append(newNode)
                self.end_nodes.append(newNode)
        
        # connect nodes that are close to each other
        for node1 in self.nodes:
            for node2 in self.nodes:
                node1.connect(node2)                
        # once the graph has been created it can be saved and loaded -> doesn't have to be created at every start of the game

        self.createPotentialField()

        # set optimal direction for each node        
        for node in self.nodes:
            node.calcDirection()
            
    def getDirection(self,pos_x,pos_y):
        nearestNode = None
        for node in self.path:
            x = pos_x - node.pos_x
            y = pos_y - node.pos_y
            r = self.radius_of_nodes
            if x*x + y*y <= r*r/16:
                #print "near node: ", node.pos_x, node.pos_y
                nearestNode = node
        if nearestNode != None:
            #print "pointing to ", nearestNode.direction
            # go in the direction the node is pointing            
            return nearestNode.direction
        else:
            #print "no node nearby"
            # keep going the old direction
            return None
        
    def addNodes(self,area):
        # works only for rectangular areas
        area_x = area[0]
        area_y = area[1]
        area_width = area[2]
        area_height = area[3]
        
        # number of nodes in the x dimension
        nodes_x = 1 + area_width / (2*self.radius_of_nodes)
        
        # number of nodes in the y dimension
        nodes_y = 1 + area_height / (2*self.radius_of_nodes)
                
        margin_x = (nodes_x * 2 * self.radius_of_nodes - area_width)/2
        margin_y = (nodes_y * 2 * self.radius_of_nodes - area_height)/2
        
        
        # generate nodes on walkable space
        i = self.radius_of_nodes - margin_x
        j = self.radius_of_nodes - margin_y
        while i < area_width + margin_x:
            while j < area_height + margin_y:
                newNode = Node(area_x + i,area_y + j,self.radius_of_nodes,len(self.nodes))
                self.nodes.append(newNode)
                j += 2*self.radius_of_nodes
            j = self.radius_of_nodes - margin_y
            i += 2*self.radius_of_nodes
                        
    def createPotentialField(self):
        for i in range(0,500):
            for node in self.nodes:
                node.spreadPotential()
                
    def generateNewPaths(self):
        self.path = []
        
        # find startnode
        current = self.start_nodes[0]
        
        # find best neighbor of every node until destination is reached
        while current.endnode == False:
            self.path.append(current)
            current.pathnode = True
            current = current.getMaxNeighbor()
            #if current.endnode = True:
                
        
                
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
        self.startnode = False
        self.endnode = False
        
        self.pathnode = False
        
        self.potential = 0
        
        self.direction = (0.0,0.0)   
        #print "id of node:", self.identifier
        
    def spreadPotential(self):
        if self.traversable == False:
            # TODO: something meaningful
            return
        elif self.startnode == True:
            self.potential = -10000
        elif self.endnode == True:
            self.potential = 10000
        else:
            sum_of_neighbors = 0
            for n in self.neighbors:
                sum_of_neighbors += n.potential
            self.potential = sum_of_neighbors/len(self.neighbors)            
        
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
                        
    def getMaxNeighbor(self):
        maxpot = -10000
        for node in self.neighbors:
            if node.potential > maxpot:
                maxnode = node
                maxpot = node.potential
        return maxnode
    
    def calcDirection(self):
        neighbor = self.getMaxNeighbor()
        if neighbor != None:
            x = neighbor.pos_x - self.pos_x
            y = neighbor.pos_y - self.pos_y
            abs_ = math.sqrt(x*x + y*y)
            self.direction = (x/abs_ , y/abs_)
        else:
            print "error: no neighbor at: " ,(self.pos_x, self.pos_y)
            print "node is not connected to graph!!"
                    
    def plot(self,screen,camera):
        #print "node pos: ", (self.pos_x,self.pos_y)
        #print "number of neighbors: ", len(self.neighbors)
        pygame.draw.line(screen, pygame.Color(0,0,0,255), (self.pos_x - camera.pos_x,self.pos_y - camera.pos_y),  (self.pos_x + int(self.direction[0]*100) - camera.pos_x,self.pos_y + int(self.direction[1]*100) - camera.pos_y), 1)

        
        if self.pathnode == True:
            pygame.draw.circle(screen, pygame.Color(0,0,0,10), (self.pos_x - camera.pos_x,self.pos_y-camera.pos_y), self.radius/4, 0)
            return
        
        if self.startnode == False and self.endnode == False:
            colorgradient = int((self.potential+10000)*255/20000)
            #print colorgradient
            pygame.draw.circle(screen, pygame.Color(colorgradient,255 - colorgradient,255 - colorgradient,10), (self.pos_x - camera.pos_x,self.pos_y-camera.pos_y), self.radius/4, 0)
        elif self.startnode == True:
            pygame.draw.circle(screen, pygame.Color(0,0,255,10), (self.pos_x - camera.pos_x,self.pos_y-camera.pos_y), self.radius/4, 0)
        elif self.endnode == True:
            pygame.draw.circle(screen, pygame.Color(255,0,0,10), (self.pos_x - camera.pos_x,self.pos_y-camera.pos_y), self.radius/4, 0)
        