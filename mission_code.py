import asyncio
import math
import subprocess
import time

from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)
import random
from mavsdk.telemetry import LandedState

async def run_tshark(time_start, count, process_list):
    print(f"Starting packet capture {count}...")
    ports = {5600, 13030, 14280, 18570, 14540, 4560, 14580, 14550, 14558}
    #5600 = ; 13030 = ; 14280 = ; 18570 = ; 14540 = ; 4560 = ; 14580 = ; 14550 = ; 14550 = ;
    port_filter = " or ".join([f"(tcp port {port} or udp port {port})" for port in ports])
    command = f"tshark -i any -f '{port_filter}' -w capture_{count}.pcap"

    process = await asyncio.create_subprocess_shell(command)

    await asyncio.sleep(5)  # Allow some time for tshark to start capturing data

    try:
        while time.monotonic() < time_start + 210:
            await asyncio.sleep(1)  # Check every second if the time has elapsed
    except asyncio.CancelledError:
        pass
    finally:
        process.terminate()
        await process.wait()

        # Ensure that the process is in the list before attempting to remove it
        if process in process_list:
            process_list.remove(process)

        print(f"Packet capture {count} complete.")


async def run(index):
    drone = System()
    print("connecting ?")
    await drone.connect(system_address="udp://:14540")
    param2 = drone.param
    print("connected")
    await param2.set_param_float('MPC_LAND_SPEED', round(random.uniform(0.6, 1.2), 1))
    mpc_land_speed = await param2.get_param_float('MPC_LAND_SPEED')
    print(f"MPC_LAND_SPEED value: {mpc_land_speed}")

    await param2.set_param_float('MIS_TAKEOFF_ALT', round(random.uniform(20, 75), 0))
    mis_takeoff_alt = await param2.get_param_float('MIS_TAKEOFF_ALT')
    print(f"MIS_TAKEOFF_ALT value: {mis_takeoff_alt}")

    await param2.set_param_float('MPC_TKO_SPEED', round(random.uniform(1, 5), 1))
    mpc_tko_speed = await param2.get_param_float('MPC_TKO_SPEED')
    print(f"MPC_TKO_SPEED value: {mpc_tko_speed}")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print_mission_progress_task = asyncio.ensure_future(
        print_mission_progress(drone))

    running_tasks = [print_mission_progress_task]
    termination_task = asyncio.ensure_future(
        observe_is_in_air(drone, running_tasks))
    x_coord = []
    y_coord = []
    mission_items = []
    movement = 0.00028076684748779
    starting_x = 37.52280 # 47.398039859999997
    starting_y = -122.255604 # 8.5455725400000002
    speed = 20
    b = 0
    mission_count = 1
    mission_total = 3
    if index == -1:
        for t in range(0, mission_total, 1):
            # Calculate the x and y coordinates using parametric equations
            x_coord.append(starting_x + (((1.5 * t * math.cos(math.pi * t)) / 15) * movement * random.uniform(0.5, 1.5)))
            y_coord.append(starting_y + (movement * t) * random.uniform(0.5, 1.5))
            print(x_coord[b])
            print(y_coord[b])
            print("-------------------")
            b += 1

        for i in range(0, mission_total, 1):
            mission_items.append(MissionItem(x_coord[i],
                                             y_coord[i],
                                             random.uniform(1, 1.5) * .15 * i * math.cos(math.pi * i) + 30,
                                             speed,
                                             True,
                                             float('nan'),
                                             float('nan'),
                                             MissionItem.CameraAction.NONE,
                                             float('nan'),
                                             float('nan'),
                                             float('nan'),
                                             (math.cos(i * math.pi) * random.randint(10, 40)),
                                             float('nan')))
            print(f"Missions completed: {mission_count}/{mission_total}")
            mission_count += 1
    else:
        for t in range(0, 5, 1):
            x_coord.append(starting_x + (movement * t * random.uniform(0.5, 1.5)))
            y_coord.append(starting_y + (movement * t * random.uniform(0.5, 1.5)))
            print(x_coord[b])
            print(y_coord[b])
            print("-------------------")
            b += 1
        for i in range(5):
            altitude = random.uniform(20, 75)
            speed = random.uniform(1, 5)
            mission_items.append(MissionItem(x_coord[i], y_coord[i], altitude, speed, True,
                                             float('nan'),
                                             float('nan'),
                                             MissionItem.CameraAction.NONE,
                                             float('nan'),
                                             float('nan'),
                                             float('nan'),
                                             (math.cos(i * math.pi) * random.randint(10, 40)),
                                             float('nan')))
            print(f"Missions completed: {mission_count}/{mission_total}")
            mission_count += 1

    mission_plan = MissionPlan(mission_items)

    await drone.mission.set_return_to_launch_after_mission(True)

    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()
    
    

    print("-- Starting mission")
    await drone.mission.start_mission()
    
    
    
    
    await termination_task

    print("-- Disarming")
    await drone.action.disarm()


async def print_mission_progress(drone):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")


async def observe_is_in_air(drone, running_tasks):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()

            return



"""async def main():
    time_stop = time.monotonic() + 210
    time_start = time_stop - 210
    count = 0
    process_list = []

    while time.monotonic() < time_stop:
        count += 1
        loop = asyncio.get_event_loop()
        process_list.append(loop.create_task(run_tshark(time_start, count, process_list)))  # Run tshark concurrently
        await run()
        print(f"Time lapsed: {time.monotonic() - time_start}")

    for process in process_list:
        process.cancel()
        try:
            await process
        except asyncio.CancelledError:
            pass

    print(f"Total mission ran: {count}")

if __name__ == "__main__":
    asyncio.run(main())"""

async def main():
    total_time = (60 * 60 * 18) # in seconds
    time_stop = time.monotonic() + total_time
    time_start = time_stop - total_time
    count = 0
    process_list = []
    index = -1

    while time.monotonic() < time_stop:
        count += 1
        loop = asyncio.get_event_loop()
        process_list.append(loop.create_task(run_tshark(time_start, count, process_list)))  # Run tshark concurrently
        index = math.pow(index, count - 1)
        await run(index)
        print(f"Time lapsed: {time.monotonic() - time_start}")

    await asyncio.gather(*process_list, return_exceptions=True)  # Wait for all tasks to complete

    print(f"Total mission ran: {count}")

if __name__ == "__main__":
    asyncio.run(main())
