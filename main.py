#
#    DVB-T Encoder written in python and opencl
#    Copyright (C) 2012  Patrick Rudolph <siro@das-labor.org>
#
#    This program is free software; you can redistribute it and/or modify it under the terms 
#    of the GNU General Public License as published by the Free Software Foundation; either version 3 
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
#    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#    See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program; 
#    if not, see <http://www.gnu.org/licenses/>.




from multiprocessing import Process, Pipe, Manager, Lock, Event
import dvbtgui
import ffmpeg
import backend
import os, tempfile, sys

if __name__ == '__main__':
    manager = Manager()
    Settings = manager.Namespace()
    
    tmpdir = tempfile.mkdtemp()
    ffmpegfifo = os.path.join(tmpdir, 'myfifo')
    try:
        os.mkfifo(ffmpegfifo)
    except OSError, e:
        print "Failed to create FIFO: %s" % e
        sys.exit(1)

    eventstop = Event()
    eventstart = Event()
    lock = Lock()
    Settings.ffmpegfifo = ffmpegfifo

    gui = Process(target=dvbtgui.gui, args=(Settings,eventstart,eventstop,lock,))
    server = Process(target=backend.startbackend, args=(Settings,eventstart,eventstop,lock,))
    ffmpeg = Process(target=ffmpeg.daemon, args=(Settings,eventstart,eventstop,lock,))
    gui.start()
    eventstart.wait()
    server.start()
    ffmpeg.start()

    gui.join()
    server.terminate()
    server.join()
    ffmpeg.terminate()
    ffmpeg.join()
    os.remove(ffmpegfifo)
    os.rmdir(tmpdir)
    sys.exit(0)