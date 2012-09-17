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
#
# This script manages the IPC and checks that all files and modules are available.
# 
#

from multiprocessing import Process, Pipe, Manager, Lock, Event
import dvbtgui
import backend
import create_opencl_files
import os, tempfile, sys
import subprocess

if __name__ == '__main__':
    # create all the opencl files if neccessary
    file_creator = create_opencl_files.file_creator()

    # IPC manager
    manager = Manager()

    # create a shared namespace for all processes
    Settings = manager.Namespace()
    
    tmpdir = tempfile.mkdtemp()
    ffmpegfifo = os.path.join(tmpdir, 'ffmpegfifo')

    try:
        os.mkfifo(ffmpegfifo)
    except OSError, e:
        print "Failed to create FIFO: %s" % e
        sys.exit(1)

    openglfifo = os.path.join(tmpdir, 'openglfifo')

    try:
        os.mkfifo(openglfifo)
    except OSError, e:
        print "Failed to create FIFO: %s" % e
        sys.exit(1)

    eventstop = Event()
    eventstart = Event()
    lock = Lock()

    Settings.ffmpegfifo = ffmpegfifo
    Settings.openglfifo = openglfifo

    process_gui = Process(target=dvbtgui.gui, args=(Settings,eventstart,eventstop,lock,), name="dvbtgui.py")
    process_server = Process(target=backend.startbackend, args=(Settings,eventstop,lock,), name="backend.py")
    process_gui.start()
    eventstart.wait()

    process_server.start()
    process_ffmpeg = subprocess.Popen("ffmpeg -i %s -f mpegts -vcodec mpeg2video -b %4.0dk -acodec mp2 -ac 2 -ab 128k -ar 44100 %s -y %s >/dev/null 2>&1" % (Settings.ffmpeginputfile,Settings.usablebitrate/1000,Settings.ffmpegargs,Settings.ffmpegfifo), shell=True)
    process_fifo2screen = subprocess.Popen("%s/fifo2screen %s -w" % (os.getcwd(),Settings.openglfifo), shell=True)

    process_gui.join()
    process_server.terminate()
    process_server.join()
    process_ffmpeg.terminate()
    process_ffmpeg.wait()
    process_fifo2screen.terminate()
    process_fifo2screen.wait()

    os.remove(ffmpegfifo)
    os.remove(openglfifo)
    os.rmdir(tmpdir)
    sys.exit(0)

       