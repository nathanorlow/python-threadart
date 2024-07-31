import numpy as np
from line import Line

#assumes -1 to 1 coordinates
class Circle(object):
    #PI = np.pi #todo: how to use constant
    def __init__(self,pin_count):
        self.x_coord = []
        self.y_coord = []
        self.pin_count = pin_count
        self.half_pin_count = round(pin_count/2) #ideally pin_count is even
        #self.x_coord are the x coord of the circle
        #self.y_coord are the y coord of the circle
        for i in range(self.pin_count):
            (circle_x, circle_y) = self.circle_xy_by_1d_index(i, self.pin_count)
            #print("appending " + str(circle_x) + " x and y " + str(circle_y))
            self.x_coord.append(circle_x)
            self.y_coord.append(circle_y)

    #index starts at 0 (1,0)
    def circle_xy_by_1d_index(self, index, total):
        #print(self.pin_count)
        theta = (2 * np.pi * index) / total
        circle_x = np.cos(theta)
        circle_y = np.sin(theta)
        return (circle_x, circle_y)
    
    def line_coord_by_index(self, index_one, index_two):
        #print("Looking up index " + str(index_one) + " and " + str(index_two))
        return Line(self.x_coord[index_one], self.y_coord[index_one], self.x_coord[index_two], self.y_coord[index_two])
