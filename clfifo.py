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

import pyopencl as cl
import numpy
import threading

class Fifo:
    # opencl lock, buffer-type, buffer-size
    def __init__(self,ctx, queue, lock, type, size):
        # store the settings
        self.fifo_buffer_size = (size * type.itemsize)
        self.type = type
        self.cl_thread_lock = lock
        self.ctx = ctx
        self.queue = queue
        self.inputevent = threading.Event()
        self.outputevent = threading.Event()
        # holds a cl.Buffer
        self.cl_fifo_bufferA = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=self.fifo_buffer_size)

        # holds a cl.Buffer
        self.cl_fifo_bufferB = cl.Buffer(self.ctx , cl.mem_flags.READ_WRITE, size=self.fifo_buffer_size)

        # self active buffer 0 == A, 1 == B
        self.active_buffer = 0

        # current data stored in buffer
        self.fifo_buffer_length = 0

        # thread lock
        self.thread_lock = threading.Lock()

    def append(self, data, size):
        while (self.space_left() < size):
            self.inputevent.clear()
            self.inputevent.wait(1.0)

        size *= self.type.itemsize
        self.thread_lock.acquire()

        self.cl_thread_lock.acquire()
        if self.active_buffer == 0:
            appendevent = cl.enqueue_copy(self.queue, self.cl_fifo_bufferA, data, byte_count=size, src_offset=0, dest_offset=self.fifo_buffer_length)
        elif self.active_buffer == 1:
            appendevent = cl.enqueue_copy(self.queue, self.cl_fifo_bufferB, data, byte_count=size, src_offset=0, dest_offset=self.fifo_buffer_length)

        self.fifo_buffer_length += size
        self.cl_thread_lock.release()
        self.thread_lock.release()
        appendevent.wait()
        self.outputevent.set()

    def pop(self,clbuffer, size):
        while (self.len() < size):
            self.outputevent.clear()
            self.outputevent.wait(1.0)

        size *= self.type.itemsize
        self.thread_lock.acquire()

        self.cl_thread_lock.acquire()
        # read data from the beginning of the buffer
        if self.active_buffer == 0:
            popevent = cl.enqueue_copy(self.queue, clbuffer, self.cl_fifo_bufferA, byte_count=size, src_offset=0, dest_offset=0)
        else:
            popevent = cl.enqueue_copy(self.queue, clbuffer, self.cl_fifo_bufferB, byte_count=size, src_offset=0, dest_offset=0)

        self.fifo_buffer_length -= size

        if self.fifo_buffer_length > 0:
            # copy all data to the beginning of the buffer
            if self.active_buffer == 0:
                 cl.enqueue_copy(self.queue, self.cl_fifo_bufferB, self.cl_fifo_bufferA, byte_count=self.fifo_buffer_length, src_offset=size, dest_offset=0)
                 self.active_buffer = 1
            else:
                 cl.enqueue_copy(self.queue, self.cl_fifo_bufferA, self.cl_fifo_bufferB, byte_count=self.fifo_buffer_length, src_offset=size, dest_offset=0)
                 self.active_buffer = 0

            # copy all data to the beginning of the buffer
            #cl.enqueue_copy(self.queue, self.cl_fifo_bufferA, self.cl_fifo_bufferB, byte_count=self.fifo_buffer_length, src_offset=0, dest_offset=0)

        self.cl_thread_lock.release()
        self.thread_lock.release()
        popevent.wait()
        self.inputevent.set()

    def len(self):
        self.thread_lock.acquire()
        if self.type.itemsize > 0:
            ret_val = self.fifo_buffer_length / self.type.itemsize
        else:
            ret_val = 0
        self.thread_lock.release()
        return ret_val

    def space_left(self):
        self.thread_lock.acquire()
        if self.type.itemsize > 0:
            ret_val = (self.fifo_buffer_size - self.fifo_buffer_length ) / self.type.itemsize
        else:
            ret_val = 0
        self.thread_lock.release()
        return ret_val

        

