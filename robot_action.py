import asyncio
from random import randint
import sys
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps

def did_occur_recently(event_time, max_elapsed_time):
    '''Did event_time occur and was it within the last max_elapsed_time seconds?'''
    if event_time is None:
        return False
    elapsed_time = time.time() - event_time
    return elapsed_time < max_elapsed_time

async def greeting(robot, dsg, guest_face):
    # If robot can see the guest then look at and greet them occasionally

    # check for items
    if dsg.guest_identified == False:
        print("guest is identified")
        msg_str = "Hello " + dsg.guest_name
        await robot.say_text(msg_str).wait_for_completed()
        dsg.set_guest_identified()

    robot.set_all_backpack_lights(cozmo.lights.green_light)
    if not did_occur_recently(dsg.time_last_announced_guest, 60.0):
        await robot.play_anim_trigger(cozmo.anim.Triggers.NamedFaceInitialGreeting).wait_for_completed()
        dsg.time_last_announced_guest = time.time()
    else:
        await robot.turn_towards_face(guest_face).wait_for_completed()

async def process_intruder(robot, dsg, intruder_face):
    # Don't react unless this is a confirmed intruder

    is_confirmed_intruder = dsg.has_confirmed_intruder()
    if is_confirmed_intruder:
        # Definitely an intruder - turn backpack red to indicate
        robot.set_all_backpack_lights(cozmo.lights.red_light)
        
        # Tweet a photo (every X seconds)
        if not did_occur_recently(dsg.time_last_uploaded_photo, 15.0):
            latest_image = robot.world.latest_image
            if latest_image is not None:
                status_text = " Intruder Detected"
                print(status_text)
                dsg.time_last_uploaded_photo = time.time()
            else:
                print("No camera image available to tweet!")

        # Sound an alarm (every X seconds)
        if not did_occur_recently(dsg.time_last_announced_intruder, 10):
            await robot.say_text("Intruder Alert").wait_for_completed()
            await robot.say_text("Intruder Alert").wait_for_completed()
            await robot.say_text("Security is on the way").wait_for_completed()
            dsg.time_last_announced_intruder = time.time()

        # Pounce at intruder (every X seconds)
        if not did_occur_recently(dsg.time_last_pounced_at_intruder, 10.0):
            await robot.play_anim_trigger(cozmo.anim.Triggers.CubePouncePounceNormal).wait_for_completed()
            dsg.time_last_pounced_at_intruder = time.time()

        # Turn towards the intruder to keep them in view
        await robot.turn_towards_face(intruder_face).wait_for_completed()
    else:
        # Possibly an intruder - turn backpack blue to indicate, and play
        # suspicious animation (if not played recently)

        robot.set_all_backpack_lights(cozmo.lights.blue_light)
        if not did_occur_recently(dsg.time_last_suspicious, 10.0):
            await robot.play_anim_trigger(cozmo.anim.Triggers.HikingInterestingEdgeThought).wait_for_completed()
            dsg.time_last_suspicious = time.time()
        else:
            # turn robot towards intruder face slightly to get a better look at them
            await robot.turn_towards_face(intruder_face).wait_for_completed()

async def watch_door(robot, dsg):
    pass





async def waiting(robot, dsg, time_for_next_turn, time_for_next_patrol,
                      initial_pose_angle,
                      patrol_offset,
                      max_pose_angle,
                      time_between_turns,
                      time_between_patrols):

    await robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
    # Turn head every few seconds to cover a wider field of view
    # Only do this if not currently investigating an intruder

    if (time.time() > time_for_next_turn):
        # pick a random amount to turn
        angle_to_turn = randint(0,15)

        ## 50% chance of turning in either direction
        if randint(0,10) > 0:
            angle_to_turn = -angle_to_turn

        # Clamp the amount to turn

        face_angle = (robot.pose_angle - initial_pose_angle).degrees

        face_angle += angle_to_turn
        if face_angle > max_pose_angle:
            angle_to_turn -= (face_angle - max_pose_angle)
        elif face_angle < -max_pose_angle:
            angle_to_turn -= (face_angle + max_pose_angle)

        # Turn left/right
        await robot.turn_in_place(degrees(angle_to_turn)).wait_for_completed()

        # Turn to face forwards again

        face_angle = (robot.pose_angle - initial_pose_angle).degrees





async def walk_around(robot, dsg, time_for_next_turn, time_for_next_patrol,
                      initial_pose_angle,
                      patrol_offset,
                      max_pose_angle,
                      time_between_turns,
                      time_between_patrols):

    await robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
    # Turn head every few seconds to cover a wider field of view
    # Only do this if not currently investigating an intruder

    if (time.time() > time_for_next_turn) and not dsg.is_investigating_intruder():
        # pick a random amount to turn
        angle_to_turn = randint(10,40)

        ## 50% chance of turning in either direction
        #if randint(0,1) > 0:
            #angle_to_turn = -angle_to_turn

        # Clamp the amount to turn

        face_angle = (robot.pose_angle - initial_pose_angle).degrees

        face_angle += angle_to_turn
        if face_angle > max_pose_angle:
            angle_to_turn -= (face_angle - max_pose_angle)
        elif face_angle < -max_pose_angle:
            angle_to_turn -= (face_angle + max_pose_angle)

        # Turn left/right
        await robot.turn_in_place(degrees(angle_to_turn)).wait_for_completed()

        # Tilt head up/down slightly
        #await robot.set_head_angle(degrees(randint(30,44))).wait_for_completed()

        # Queue up the next time to look around

    # Every now and again patrol left and right between 3 patrol points

    if (time.time() > time_for_next_patrol) and not dsg.is_investigating_intruder():

        # Check which way robot is facing vs initial pose, pick a new patrol point

        face_angle = (robot.pose_angle - initial_pose_angle).degrees
        drive_right = (patrol_offset < 0) or ((patrol_offset == 0) and (face_angle > 0))

        # Turn to face the new patrol point

        if drive_right:
            await robot.turn_in_place(degrees(90 - face_angle)).wait_for_completed()
            patrol_offset += 1
        else:
            await robot.turn_in_place(degrees(-90 - face_angle)).wait_for_completed()
            patrol_offset -= 1

        # Drive to the patrol point, playing animations along the way

        await robot.drive_wheels(20, 20)
        for i in range(1,4):
            await robot.play_anim("anim_hiking_driving_loop_0" + str(i)).wait_for_completed()

        # Stop driving

        robot.stop_all_motors()

        # Turn to face forwards again

        face_angle = (robot.pose_angle - initial_pose_angle).degrees
        if face_angle > 0:
            await robot.turn_in_place(degrees(-90)).wait_for_completed()
        else:
            await robot.turn_in_place(degrees(90)).wait_for_completed()


async def goto_door(robot, dsg):
    pass
