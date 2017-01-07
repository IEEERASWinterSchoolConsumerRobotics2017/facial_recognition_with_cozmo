import asyncio
from random import randint
import sys
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
#from tcp_funcs import *
import tcp_funcs

class WaiterGuard:
    '''Container for Waiter Guard status'''

    def __init__(self):
        self.guest_name = None
        self.maid_name = "Guoxiang Zhang"#"Cole Mortensen"
        self.current_name = None
        self.guest_identified = False

        # This will be True after guest check-in and before cozmo get a list of items
        self.check_for_item_flag = False
        self.is_waiting = True

        self.is_armed = True

        self.time_first_observed_intruder = None
        self.time_last_observed_intruder = None

        self.time_first_observed_guest = None
        self.time_last_observed_guest = None

        self.time_last_suspicious = None
        self.time_last_announced_intruder = None
        self.time_last_pounced_at_intruder = None
        self.time_last_announced_guest = None
        self.time_last_uploaded_photo = None

    def query_guest_name(self):
        '''Query name of guest from server'''
        names = ["Dylan Wallace"]
        self.guest_name = names
        return names

    def set_guest_identified(self):
        assert self.guest_name is not None, "guest name should be queried at this point"
        self.guest_identified = True
        #self.check_for_item_flag = True
        tcp_funcs.guest_entered_room()
        self.is_waiting = False

    def query_requested_items(self):
        '''Query whether guest required some items'''
        self.check_for_item_flag = False

        items = tcp_funcs.tcp_get_items()
        return items#["a bottle of water"]

    def query_voice_output(self):
        '''query potential'''
        pass

    def is_investigating_intruder(self):
        '''Has an unknown face recently been seen?'''
        return self.time_first_observed_intruder is not None

    def has_confirmed_intruder(self):
        '''The robot has seen an intruder for long enough that it's pretty sure it's not the guest.'''
        if self.time_first_observed_intruder:
            elapsed_time = time.time() - self.time_first_observed_intruder
            if elapsed_time > 3.0:
                tcp_funcs.tcp_intruder_found()
            return elapsed_time > 2.0
        return False
