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

import os
import signal
import subprocess
import threading
from tempfile import mkstemp
from gi.repository import Gtk as gtk, GObject as gobject, Gdk as gdk, Keybinder as keybinder, Gio as gio, GLib as glib
import cairo

from paparazzo.overlay import Overlay
from paparazzo.countdown import Countdown

loop = gobject.MainLoop()
glib.threads_init()

class Subprocess(gobject.GObject):
    """
    GObject API for handling child processes.

    :param command: The command to be run as a subprocess.
    :param fork: If `True` this process will be detached from its parent and
                 run independent. This means that no excited-signal will be emited.

    :type command: `list`
    :type fork: `bool`
    """

    __gtype_name__ = 'Subprocess'
    __gsignals__ = {
        'exited': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT))
        }

    def __init__(self, command, name=None):

        gobject.GObject.__init__(self)

        self.process = None
        self.pid = None
        
        self.stdout = True
        self.stderr = True

        self.command = command
        self.name = name


    def run(self):
        """ Run the process. """

        """
        process_data = gobject.spawn_async(self.command,
                flags=gobject.SPAWN_SEARCH_PATH|gobject.SPAWN_DO_NOT_REAP_CHILD,
                standard_output=self.stdout,
                standard_error=self.stderr
                )
        """
        
        self.process = subprocess.Popen(self.command)
        
        self.pid = self.process.pid

        #self.stdout = os.fdopen(process_data[2])
        #self.stderr = os.fdopen(process_data[3])
        
        self.watch = gobject.child_watch_add(self.pid, self.exited_cb)

        return self.pid
        
        
    def stop(self):
    
        self.process.send_signal(signal.SIGINT)


    def exited_cb(self, pid, condition):
        self.emit('exited', pid, condition)


class Recorder:
    
    def __init__(self):
    
        self.path = None
        self.proc = None
        
    
    def start(self, x, y, width, height):

        self.path = mkstemp(suffix='.avi')[1]
        
        even = lambda x: x+1 if x%2 != 0 else x

        self.proc = Subprocess('ffmpeg -y -f x11grab -r 25 -s {0},{1} -i :0.0+{2},{3} -vcodec libx264 {4}'.format(even(width), even(height), x, y, self.path).split(' '))
        self.proc.run()
        

    def stop(self):
        self.proc.stop()
        
        
    def get_path(self):
        return self.path


class Screencast:
    
    def __init__(self):
    
        self.recorder = Recorder()
            
        keybinder.init()
        keybinder.bind('<Control>Escape', self.callback, None)
        
        self.overlay = Overlay()
        self.overlay.connect('trigger', lambda *args: self.start_recording(*self.overlay.get_selection()))
        self.overlay.show_all()
    
    
    def start_recording(self, x, y, width, height):
        
        def completed_cb(*args):
            #loop.quit()
            self.recorder.start(x, y, width, height)
    
        countdown = Countdown()
        countdown.connect('completed', completed_cb)
        countdown.start()
    
        
    def callback(self, key, data):
    
        def copy(src, dst):
            source = gio.File.new_for_path(src)
            dest = gio.File.new_for_uri(dst)
            
            global c
            c = 0

            def progress_cb(level, overall, data):
                global c
                progress = level/overall
                if c%100 == 0:
                    gdk.threads_enter()
                    self.progress_bar.set_fraction(progress)
                    self.progress_bar.set_text("{0}%".format(int(progress*100)))
                    while loop.get_context().pending():
                        loop.get_context().iterate()
                    gdk.threads_leave()
                if progress == 1:
                    self.progress_dialog.hide()
                c += 1

            source.copy(dest, gio.FileCopyFlags.OVERWRITE, None, progress_cb, None)
            loop.quit()
            
    
        self.recorder.stop()
        
        filechooser = gtk.FileChooserDialog("Save", self.overlay, gtk.FileChooserAction.SAVE, buttons=(gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL, gtk.STOCK_OPEN, gtk.ResponseType.ACCEPT))
        filechooser.set_current_name('Screencast.avi')
        filechooser.set_type_hint(gdk.WindowTypeHint.NORMAL)
        filechooser.set_urgency_hint(True)
        res = filechooser.run()
        
        filechooser.hide()
        
        self.progress_dialog = gtk.Dialog("Saving…", buttons=(gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL))
        self.progress_dialog.get_action_area().get_children()[0].connect('button-release-event', lambda *args: loop.quit())
        self.progress_dialog.set_type_hint(gdk.WindowTypeHint.NORMAL)
        
        self.progress_bar = gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_size_request(320, -1)
        
        content_area = self.progress_dialog.get_content_area().add(self.progress_bar)
        
        if res == gtk.ResponseType.ACCEPT:
            self.progress_dialog.show_all()
            thread = threading.Thread(target=copy, args=(self.recorder.get_path(), filechooser.get_uri()))
            thread.daemon = True
            thread.start()
        else:
            loop.quit()
        

Screencast()
loop.run()
