import numpy as np
class Square(object):
    def __init__(self, PIXEL_COUNT):
        self.PIXEL_COUNT = PIXEL_COUNT
        self.HALF_PIXEL_COUNT = round(PIXEL_COUNT / 2)
        self.CO_SIZE = 2 #coordinate width / graph width #this may depend on half pixel, and - 1 -- see circle
        self.PIXEL_WIDTH = self.CO_SIZE / PIXEL_COUNT

    def center_by_index(self, x_index, y_index) :
        center_x = ((x_index + .5) * self.CO_SIZE / self.PIXEL_COUNT) - 1
        center_y = ((y_index + .5) * self.CO_SIZE / self.PIXEL_COUNT) - 1
        return (center_x, center_y)

    def get_pixel_width(self):
        return self.PIXEL_WIDTH
    
    def get_pixel_count(self):
        return self.PIXEL_COUNT
