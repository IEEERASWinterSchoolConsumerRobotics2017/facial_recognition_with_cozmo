#!/usr/bin/env python3
import asyncio
from random import randint
import sys
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps

#sys.path.append('../lib/')



#: The name that the owner's face is enrolled as (i.e. your username in the app)
#: When that face is seen, Cozmo will assume no other faces currently seen are intruders
OWNER_FACE_ENROLL_NAME = ""

async def add_face_core(robot):
   face_name = sys.argv[1] + " " + sys.argv[2]
   for visible_face in robot.world.visible_faces:
       #visible_face.rename_face(dsg.owner_name)
       #await visible_face.name_face(face_name).wait_for_completed()
       print(visible_face.expression)

async def add_face_func(robot):
    '''The core of the add_face_func program'''

    # Turn on image receiving by the camera
    robot.camera.image_stream_enabled = True

    for i in range(100):
        print(i)
        await add_face_core(robot)
        # Sleep to allow other things to run
        await asyncio.sleep(0.05)


async def run(sdk_conn):
    '''The run method runs once the Cozmo SDK is connected.'''
    robot = await sdk_conn.wait_for_robot()

    try:
        await add_face_func(robot)

    except KeyboardInterrupt:
        print("")
        print("Exit requested by user")


if __name__ == '__main__':
    assert len(sys.argv) == 3, "This should be run with 2 parameter.\nadd_face <Name of face>"
    print(str(sys.argv))
    OWNER_FACE_ENROLL_NAME = sys.argv[1] + " " + sys.argv[2]
    print(OWNER_FACE_ENROLL_NAME)

    if OWNER_FACE_ENROLL_NAME == "":
        sys.exit("You must fill in OWNER_FACE_ENROLL_NAME")

    cozmo.setup_basic_logging()
    cozmo.robot.Robot.drive_off_charger_on_connect = False  # Stay on charger until init
    try:
        cozmo.connect_with_tkviewer(run, force_on_top=True)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)

