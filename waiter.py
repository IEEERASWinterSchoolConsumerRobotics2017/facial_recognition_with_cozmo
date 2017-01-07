#!/usr/bin/env python3

import asyncio
from random import randint
import sys
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps

from waiter_guard import WaiterGuard
from robot_action import greeting, did_occur_recently, walk_around, process_intruder, waiting


WORKING_HEAD_ANGLE = degrees(10)#10/180.0 * 3.14

async def query_item(robot, dsg:WaiterGuard):
    
    items = dsg.query_requested_items()
    msg_str = "You ordered "
    if items is not None:
        for item in items:
            msg_str += item
        await robot.say_text(msg_str).wait_for_completed()
        print(msg_str)


async def process_raw_face(robot, dsg:WaiterGuard):
    ''''''

    # Check which faces can be seen, and if any are the guest or an intruder

    guest_face = None
    intruder_face = None
    for visible_face in robot.world.visible_faces:

        if visible_face.name == dsg.maid_name:
            dsg.check_for_item_flag = True

        elif visible_face.name in dsg.guest_name:
            dsg.current_name = visible_face.name
            if guest_face:
                print("Multiple faces with name %s seen - %s and %s!" %
                      (dsg.guest_name, guest_face, visible_face))
            guest_face = visible_face
        else:
            # just use the first intruder seen
            if not intruder_face:
                intruder_face = visible_face

    # Update times first/last seen guest or an intruder

    if guest_face:

        print("guest's face!")
        dsg.time_last_observed_guest = guest_face.last_observed_time
        if dsg.time_first_observed_guest is None:
            dsg.time_first_observed_guest = dsg.time_last_observed_guest

    if intruder_face:
        print("not guest's face!")
        if dsg.time_last_observed_intruder is None or \
                        intruder_face.last_observed_time > dsg.time_last_observed_intruder:
            dsg.time_last_observed_intruder = intruder_face.last_observed_time

        if dsg.time_first_observed_intruder is None:
            dsg.time_first_observed_intruder = dsg.time_last_observed_intruder

    # Check if there's anything to investigate

    can_see_guest = did_occur_recently(dsg.time_last_observed_guest, 1.0)
    can_see_intruders = did_occur_recently(dsg.time_last_observed_intruder, 1.0)

    if not can_see_intruders:
        dsg.time_first_observed_intruder = None

    if can_see_guest and guest_face is not None:

        # If robot can see the guest then look at and greet them occasionally
        await greeting(robot, dsg, guest_face)

    elif can_see_intruders:
        await process_intruder(robot, dsg, intruder_face)
    else:
        robot.set_backpack_lights_off()

#def random_explore(robot):
   # 

async def waiter_guard(robot):
    '''The core of the waiter_guard program'''

    # Turn on image receiving by the camera
    robot.camera.image_stream_enabled = True


    # Create our security guard
    dsg = WaiterGuard()
    dsg.query_guest_name()
    print(dsg.guest_name)

    # Make sure Cozmo is clear of the charger
    if robot.is_on_charger:
        # Drive fully clear of charger (not just off the contacts)
        await robot.drive_off_charger_contacts().wait_for_completed()
        await robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()

    # Tilt head up to look for people
    await robot.set_head_angle(WORKING_HEAD_ANGLE).wait_for_completed()

    initial_pose_angle = robot.pose_angle

    patrol_offset = 0  # middle
    max_pose_angle = 45  # offset from initial pose_angle (up to +45 or -45 from this)

    # Time to wait between each turn and patrol, in seconds
    time_between_turns = 2.5
    time_between_patrols = 20
    time_between_req_item = 5

    time_for_next_turn = time.time() + time_between_turns
    time_for_next_patrol = time.time() + time_between_patrols
    time_for_next_req_items = time.time() + time_between_req_item
    while True:

        # Handle any external requests to arm or disarm Cozmo
        if not dsg.is_armed:
            print("Alarm Armed")
            dsg.is_armed = True

        
        if dsg.is_waiting:
            await waiting(robot, dsg, time_for_next_turn, time_for_next_patrol,
                          initial_pose_angle,
                          patrol_offset,
                          max_pose_angle,
                          time_between_turns,
                          time_between_patrols)
        else:
            await walk_around(robot, dsg, time_for_next_turn, time_for_next_patrol,
                              initial_pose_angle,
                              patrol_offset,
                              max_pose_angle,
                              time_between_turns,
                              time_between_patrols)

            # Queue up the next time to patrol
        time_for_next_patrol = time.time() + time_between_patrols
        time_for_next_turn = time.time() + time_between_turns

        # look for intruders

        await process_raw_face(robot, dsg)

        # Sleep to allow other things to run

        await asyncio.sleep(0.5)

        can_see_guest = True#did_occur_recently(dsg.time_last_observed_guest, 1.0)
        # If robot can see the guest then look at and greet them occasionally


        # check for items
        print(dsg.check_for_item_flag)
        if dsg.check_for_item_flag and time.time() > time_for_next_req_items:
            #print("queried??")
            await query_item(robot, dsg)
            time_for_next_req_items = time.time() + time_between_req_item
            #items = dsg.query_requested_items()
            #msg_str = "You ordered "
            #if items is not None:
                #for item in items:
                    #msg_str += item
                #await robot.say_text(msg_str).wait_for_completed()
                #print(msg_str)

async def run(sdk_conn):
    '''The run method runs once the Cozmo SDK is connected.'''
    robot = await sdk_conn.wait_for_robot()

    try:
        await waiter_guard(robot)

    except KeyboardInterrupt:
        print("")
        print("Exit requested by user")


if __name__ == '__main__':
    cozmo.setup_basic_logging()
    cozmo.robot.Robot.drive_off_charger_on_connect = False  # Stay on charger until init
    try:
        cozmo.connect_with_tkviewer(run, force_on_top=True)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)

