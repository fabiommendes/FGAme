from FGAme.screen import Canvas
from FGAme.input import Input
from FGAme.mainloop import MainLoop


class EmptyCanvas(Canvas):
    def __do_nothing(self, *args, **kwds):
        pass

    show = flip = \
        draw_raw_aabb_solid = draw_raw_aabb_border = \
        draw_raw_circle_solid = draw_raw_circle_border = \
        draw_raw_poly_solid = draw_raw_poly_border = \
        draw_raw_segment = \
        draw_raw_texture = \
        paint_pixel = \
        clear_background = __do_nothing


class EmptyInput(Input):
    def poll(self):
        pass
