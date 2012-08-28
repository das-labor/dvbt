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

import subprocess
import os

def daemon(globalsettings,eventstart,eventstop,lock):
	print 'ffmpeg daemon alive!'

#ffmpeg -i file.mpg -c copy \
#     -mpegts_original_network_id 0x1122 \
#     -mpegts_transport_stream_id 0x3344 \
#     -mpegts_service_id 0x5566 \
#     -mpegts_pmt_start_pid 0x1500 \
#     -mpegts_start_pid 0x150 \
#     -metadata service_provider="Some provider" \
#     -metadata service_name="Some Channel" \
#     -y out.ts
        eventstart.wait()
        process = subprocess.Popen("ffmpeg -i %s -f mpegts -vcodec mpeg2video -b %4.0dk -acodec mp2 -ac 2 -ab 128k -ar 44100 %s -y %s >/dev/null 2>&1" % (globalsettings.ffmpeginputfile,globalsettings.usablebitrate/1000,globalsettings.ffmpegargs,globalsettings.ffmpegfifo), shell=True)
        #lock.acquire()
        #print process.communicate()
        #lock.release()
        eventstop.wait()