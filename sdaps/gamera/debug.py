

from gi.repository import Gtk

def show_surface(surface):
    dialog = Gtk.MessageDialog()

    def draw_image(widget, cr):
        cr.set_source_surface(surface)
        cr.paint()

    area = Gtk.DrawingArea()
    area.set_size_request(surface.get_width(), surface.get_height())
    area.connect("draw", draw_image)

    scroll = Gtk.ScrolledWindow()
    scroll.set_size_request(min(surface.get_width(), 700), min(surface.get_height(), 500))
    view = Gtk.Viewport()
    scroll.add(view)
    dialog.set_image(scroll)

    view.add(area)

    dialog.show_all()

    dialog.run()
    dialog.destroy()

