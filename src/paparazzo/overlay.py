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

import sys
import math
from gi.repository import Gtk as gtk, Gdk as gdk, GObject as gobject
import cairo

ICON_SIZE = 32

def rounded_rectangle(cr, x, y, w, h, r=20):

    if r >= h / 2.0:
        r = h / 2.0

    cr.arc(x + r, y + r, r, math.pi, -.5 * math.pi)
    cr.arc(x + w - r, y + r, r, -.5 * math.pi, 0 * math.pi)
    cr.arc(x + w - r, y + h - r, r, 0 * math.pi, .5 * math.pi)
    cr.arc(x + r, y + h - r, r, .5 * math.pi, math.pi)
    cr.close_path()


class Overlay(gtk.Window):
    
    __gsignals__ = {
        'trigger': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'cancel': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }

    def __init__(self):

        gtk.Window.__init__(self)
        
        self.display = gdk.Display.get_default()
        self.screen = self.display.get_default_screen()
        self.device_manager = self.display.get_device_manager()
        self.pointer = self.device_manager.get_client_pointer()
        
        width = self.screen.get_width()
        height = self.screen.get_height() 
        
        self.connect('map-event', self.map_cb)
    
        self._selection = (100, 100, width-200, height-200)
        print(self._selection)
        self._selecting = False
        self._selection_origin = (0, 0)

        self.set_type_hint(gdk.WindowTypeHint.DOCK)
        self.set_keep_above(True)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())
        self.fullscreen()
        
        self.set_events(self.get_events() | gdk.EventMask.POINTER_MOTION_MASK | gdk.EventMask.BUTTON_PRESS_MASK | gdk.EventMask.BUTTON_RELEASE_MASK)
        
        self.connect('draw', self.draw_cb)
        self.connect('button-press-event', self.button_press_cb)
        self.connect('button-release-event', self.button_release_cb)
        self.connect('motion-notify-event', self.motion_cb)

        self.set_size_request(width, height)

        self.move(0, 0)
        
        self.alignment = gtk.Alignment()
        self.alignment.set(.5, .8, .4, .01)
        self.add(self.alignment)
        
        self.layout = gtk.HBox()
        self.alignment.add(self.layout)
        
        self.label = gtk.Label()
        self.label.set_alignment(0, .5)
        self.label.set_size_request(300, -1)
        self.label.set_markup('<span foreground="white">Please select an area!</span>')
        self.layout.pack_start(self.label, False, True, 0)
        
        self.button_box = gtk.HButtonBox()
        self.button_box.set_spacing(10)
        self.layout.pack_end(self.button_box, False, True, 0)
        
        self.button_record = gtk.Button(stock=gtk.STOCK_MEDIA_RECORD)
        self.button_record.connect('button-release-event', lambda *args: self.trigger())
        self.button_box.pack_end(self.button_record, True, True, 10)
        
        self.button_cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.button_cancel.connect('button-release-event', lambda *args: sys.exit(0))
        self.button_box.pack_end(self.button_cancel, True, True, 0)
        
        self.show()
        
        
    def map_cb(self, *args):
        self.pointer.grab(self.get_window(), gdk.GrabOwnership.WINDOW, True, gdk.EventMask.ALL_EVENTS_MASK, None, gdk.CURRENT_TIME)
        
        
    def trigger(self):
    
        self.emit('trigger', self.get_selection())
        self.hide()
        
        
    def reset_selection(self):
        self._selection = None
        
    def get_selection(self):
        return self._selection
        
        
    def draw_cb(self, window, ctx):
    
        width, height = self.get_size()

        ctx.set_line_width(1)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.paint()
        
        ctx.set_operator(cairo.OPERATOR_OVER)

        selection = self.get_selection()
        if selection:
            ctx.set_operator(cairo.OPERATOR_OVER)
            ctx.set_source_rgba(0, 0, 0, 0.5)
            ctx.paint()

            ctx.set_operator(cairo.OPERATOR_CLEAR)
            ctx.rectangle(selection[0], selection[1], selection[2], selection[3])
            ctx.fill()

            ctx.set_source_rgba(1, 1, 1, .4)
            ctx.set_operator(cairo.OPERATOR_OVER)
            ctx.rectangle(selection[0] + .5, selection[1] + .5, selection[2]-1, selection[3]-1)
            ctx.stroke()
            
        box = self.layout.get_allocation()
        ctx.translate(.5, .5)
        
        rounded_rectangle(ctx, box.x-10, box.y-10, box.width+20, box.height+20, 5)
        ctx.set_source_rgba(0, 0, 0, .8)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, .5)
        ctx.stroke()
        
        rounded_rectangle(ctx, box.x-11, box.y-11, box.width+22, box.height+22, 6)
        ctx.set_source_rgba(0, 0, 0, .4)
        ctx.stroke()
        
        rounded_rectangle(ctx, box.x-12, box.y-12, box.width+24, box.height+24, 7)
        ctx.set_source_rgba(0, 0, 0, .2)
        ctx.stroke()
        

    def draw(self):

        width, height = self.get_size()
        self.queue_draw_area(0, 0, width, height)
            
            
    def button_press_cb(self, window, event):
            
        width, height = self.get_size()

        self._selecting = True

        self._selection = (int(event.x), int(event.y), 1, 1)
        self._selection_origin = int(event.x), int(event.y)
        self.label.set_markup('<span foreground="white">{0}, {1} - {2}x{3}</span>'.format(*self.get_selection()))
        self.draw()


    def button_release_cb(self, window, event):
    
        width, height = self.get_size()
        if self._selecting:
            self.draw()
            self._selecting = False


    def motion_cb(self, window, event):
    
        x, y = self.pointer.get_position()[1:3]
    
        box = self.layout.get_allocation()
    
        if x > box.x-10 and x < box.x + box.width + 10 and y > box.y-10 and y < box.y + box.height + 10:
            self.get_window().set_cursor(gdk.Cursor(gdk.CursorType.LEFT_PTR))
        else:
            self.get_window().set_cursor(gdk.Cursor(gdk.CursorType.CROSSHAIR))
    
        if self._selecting and self._selection:
            sel = self._selection
            
            self._selection = (min(int(self._selection_origin[0]), int(x)), min(int(self._selection_origin[1]), int(y)), abs(int(x - self._selection_origin[0])) + 1, abs(int(y - self._selection_origin[1]))+1)
            
            self.label.set_markup('<span foreground="white">{0}, {1} - {2}x{3}</span>'.format(*self.get_selection()))
            self.draw()

