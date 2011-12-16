#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import math
from gi.repository import Gtk as gtk, GObject as gobject
import cairo

def rounded_rectangle(cr, x, y, w, h, r=20):

    if r >= h / 2.0:
        r = h / 2.0

    cr.arc(x + r, y + r, r, math.pi, -.5 * math.pi)
    cr.arc(x + w - r, y + r, r, -.5 * math.pi, 0 * math.pi)
    cr.arc(x + w - r, y + h - r, r, 0 * math.pi, .5 * math.pi)
    cr.arc(x + r, y + h - r, r, .5 * math.pi, math.pi)
    cr.close_path()


class Countdown(gtk.Window):
    
    __gsignals__ = {
        'completed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }

    def __init__(self):

        gtk.Window.__init__(self)
        
        self.counter = 5
    
        self.set_size_request(320, 200)
        self.set_position(gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())
        
        self.connect('draw', self.draw_cb)

        
    def start(self):
    
        self.show()
        
        def update():
            self.draw()

            self.counter -= 1
            if self.counter >= 0:
                return True
            else:
                self.hide()
                self.emit('completed')
                return False
    
        gobject.timeout_add(1000, update)
        

    def draw(self):

        width, height = self.get_size()
        self.queue_draw_area(0, 0, width, height)

        
    def draw_cb(self, window, ctx):
        
        width, height = self.get_size()

        ctx.set_line_width(1)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.paint()
        
        ctx.set_operator(cairo.OPERATOR_OVER)
        
        ctx.translate(.5, .5)
        rounded_rectangle(ctx, 5, 5, width-10, height-10, 5)
        ctx.set_source_rgba(0, 0, 0, .8)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, .5)
        ctx.stroke()
        
        rounded_rectangle(ctx, 4, 4, width-8, height-8, 6)
        ctx.set_source_rgba(0, 0, 0, .4)
        ctx.stroke()
        
        rounded_rectangle(ctx, 3, 3, width-6, height-6, 7)
        ctx.set_source_rgba(0, 0, 0, .2)
        ctx.stroke()
        
        ctx.set_source_rgba(1, 1, 1, .8)
        
        if self.counter > 3:
            ctx.set_font_size(20)
            
            x_bearing, y_bearing, w, h = ctx.text_extents("In order to stop recording,")[:4]
            ctx.move_to((width - w) / 2 - x_bearing, (height - h) / 2 - y_bearing - 20)
            ctx.show_text("In order to stop recording,")
            ctx.stroke()
            
            x_bearing, y_bearing, w, h = ctx.text_extents("please press Ctrl+Del!")[:4]
            ctx.move_to((width - w) / 2 - x_bearing, (height - h) / 2 - y_bearing + 20)
            ctx.show_text("please press Ctrl+Del!")
            ctx.stroke()
        elif self.counter > 0:
            ctx.set_font_size(120)
            
            x_bearing, y_bearing, w, h = ctx.text_extents(str(self.counter))[:4]
            ctx.move_to((width - w) / 2 - x_bearing, 140)
            ctx.show_text(str(self.counter))
            ctx.stroke()
        elif self.counter == 0:
            ctx.set_font_size(40)
            
            x_bearing, y_bearing, w, h = ctx.text_extents("Recording.")[:4]
            ctx.move_to((width - w) / 2 - x_bearing, (height - h) / 2 - y_bearing)
            ctx.show_text("Recording")
            ctx.stroke()
        

if __name__ == '__main__':
    Countdown().start()
    loop = gobject.MainLoop()
    loop.run()
