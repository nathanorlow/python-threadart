import numpy as np
class Line(object):
    TOLERANCE = .001

    INDEX_TOLERANCE = 2

    def __init__(self, x_one, y_one, x_two, y_two):
        self.x_one = x_one
        self.y_one = y_one
        self.x_two = x_two
        self.y_two = y_two
        self.compute_ax_by_c()
        self.is_vertical = abs(self.x_one - self.x_two) < self.TOLERANCE
        self.is_horizontal = abs(self.y_one - self.y_two) < self.TOLERANCE
        if (not self.is_vertical):
            self.slope = (self.y_two - self.y_one) / (self.x_two - self.x_one)
        
    def index_to_coord(self, index, pixel_width):
        return (pixel_width * index) - 1

    def coord_to_ind(self, coord, pixel_width): #note may not be integer
        return (coord + 1) / pixel_width

    def y_index_near_line_for_x_index(self, x_index, y_index_to_check, pixel_width):
        if(self.is_vertical): 
            return True
        x_coord = self.index_to_coord(x_index, pixel_width)
        y_coord = self.y_one + (x_coord - self.x_one) * self.slope
        y_ind =   self.coord_to_ind(y_coord, pixel_width)
        return (y_index_to_check - self.INDEX_TOLERANCE <= y_ind <= y_index_to_check + self.INDEX_TOLERANCE)


    def x_range_by_index(self, pixel_width, pixel_count):
        smaller_x= min(self.x_one, self.x_two)
        larger_x = max(self.x_one, self.x_two)
        x_min_index = max(0, np.floor((smaller_x + 1) / pixel_width) - self.INDEX_TOLERANCE)
        x_max_index_plus_one = min(pixel_count, np.ceil((larger_x + 1) / pixel_width) + self.INDEX_TOLERANCE + 1 )
        #print(str(x_min_index) + " to " + str(x_max_index_plus_one))
        return range(int(x_min_index), int(x_max_index_plus_one))
    
    def compute_ax_by_c(self):
        self.a = self.y_one - self.y_two
        self.b = self.x_two - self.x_one
        self.c = self.y_two * self.x_one - self.x_two * self.y_one
        #print("a=" + str(self.a) + ", b=" + str(self.b) + ", c=" + str(self.c))

    def distance_to_line(self, x, y):
        numerator = abs(self.a * x + self.b * y + self.c)
        denominator = np.sqrt(self.a * self.a + self.b * self.b)
        return numerator/denominator

    def distance_to_vertical_line(self, center_x):
        return min(abs(self.x_one - center_x), abs(self.x_two - center_x))

    def distance_to_horizontal_line(self, center_y):
        return min(abs(self.y_one - center_y), abs(self.y_two - center_y))
    
    def point_outside_line(self, point_x, point_y):
        if(self.not_in_order_ends_unequal(self.x_one, point_x, self.x_two)):
            return True
        if(self.not_in_order_ends_unequal(self.y_one, point_y, self.y_two)):
            return True
        return False
    
    #Note if ends equal, gives true (ignore part of horizontal or vertical case)
    #if roughly in order, returns true
    def not_in_order_ends_unequal(self, value_one, value_two, value_three) :
        if(abs(value_one - value_three) < self.TOLERANCE):
            return False
        if(((value_one - value_two) > self.TOLERANCE) and ((value_two - value_three) > self.TOLERANCE )):
            return False
        if(((value_one - value_two) < -self.TOLERANCE) and ((value_two - value_three) < -self.TOLERANCE )):
            return False   
        return True

    #centers now should be coordinate values 
    def weight_for_center(self, center_x, center_y, pixel_width) :
        if( self.point_outside_line(center_x, center_y)):
            return 0
        distance = self.distance_to_line(center_x, center_y) 
        #print("pixel width " + str(pixel_width))
        #print("x " + str(center_x) + " y " + str(center_y) + " distance is " + str(distance))
        scaled_distance = distance/(pixel_width * np.sqrt(2))
        weight = (0 if (scaled_distance > 1) else (1 - scaled_distance)) #maybe weight can be done in square
        #print("weight is " + str(weight))
        return weight

