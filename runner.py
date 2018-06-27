from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
import time
import thread
import Tkinter

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci

def run(mobilRoad, mobilTotal, speedRoad, speedMax):
    """execute the TraCI control loop"""
    step = 0
    vehicleNumber = 0
    speed = 0
    maxSpeed = 0
    multiplier = 1

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1
        vehicleNumber += traci.simulation.getDepartedNumber()
        speed = 0
        for vehc in traci.vehicle.getIDList():
            currSpeed = traci.vehicle.getSpeed(vehc)
            speed += currSpeed
            if currSpeed > maxSpeed:
                maxSpeed = currSpeed
        if vehicleNumber != 0:
            speed /= vehicleNumber
        mobilRoad.set(len(traci.vehicle.getIDList()))
        mobilTotal.set(vehicleNumber)
        speedRoad.set(round(speed * multiplier, 2))
        speedMax.set(round(maxSpeed * multiplier, 2))
    traci.close()
    sys.stdout.flush()

def report_gui():
    """Ngasih live report jalan raya"""
    master = Tkinter.Tk()
    
    mobilRoad = Tkinter.StringVar(value='0')
    mobilTotal = Tkinter.StringVar(value='0')
    speedRoad = Tkinter.StringVar(value='0')
    speedMax = Tkinter.StringVar(value='0')

    w1=25
    w2=10
    Tkinter.Label(master, width=w1, text='Jumlah mobil di jalan').grid(row=0,column=0)
    Tkinter.Label(master, width=w2, textvariable=mobilRoad).grid(row=0,column=1)
    Tkinter.Label(master, width=w1, text='Total mobil keluar').grid(row=1,column=0)
    Tkinter.Label(master, width=w2, textvariable=mobilTotal).grid(row=1,column=1)
    Tkinter.Label(master, width=w1, text='Kecepatan rata-rata di jalan').grid(row=2,column=0)
    Tkinter.Label(master, width=w2, textvariable=speedRoad).grid(row=2,column=1)
    Tkinter.Label(master, width=w1, text='Kecepatan tertinggi').grid(row=3,column=0)
    Tkinter.Label(master, width=w2, textvariable=speedMax).grid(row=3,column=1)

    thread.start_new_thread(run, (mobilRoad, mobilTotal, speedRoad, speedMax))
    master.mainloop()

def generate_routefile(timeSteps, maxMobil, remissionTime = 153):
    """Bikin file route.
    timeSteps: jumlah maksimal time ticks
    maxMobil: jumlah maksimal mobil
    remissionTime: pengampunan waktu, biar jumlah mobilnya sesuai keinginan
    """

    # Probability car summoned
    pMobil = 1. * maxMobil / (timeSteps - remissionTime)
    with open("data/cross.rou.xml", "w") as routes:
        # Red, green, ungu, yellow, cyan
        print("""<routes>
        <vType id="type1" accel="1.4" decel="6.5" sigma="0.5" length="8" minGap="2.5" maxSpeed="6" color="1,0,0" guiShape="passenger"/>
        <vType id="type2" accel="1.2" decel="7.5" sigma="0.5" length="7" minGap="2.5" maxSpeed="11" color="0,1,0" guiShape="passenger"/>
        <vType id="type3" accel="1.1" decel="6.5" sigma="0.5" length="6" minGap="2.5" maxSpeed="16" color="1,0,1" guiShape="passenger"/>
        <vType id="type4" accel="0.9" decel="5.5" sigma="0.5" length="6" minGap="2.5" maxSpeed="17" color="1,1,0" guiShape="passenger"/>
        <vType id="type5" accel="0.8" decel="4.5" sigma="0.5" length="4" minGap="2.5" maxSpeed="18" color="0,1,1" guiShape="passenger"/>

        <route id="right" edges="12 23 34" />""", file=routes)
        vehNr = 0
        for i in range(timeSteps):
            if random.uniform(0, 1) < pMobil:
                kelas = random.randint(1, 5)
                print('<vehicle id="right_%i" type="type%i" route="right" depart="%i" />' % (
                    vehNr, kelas, i), file=routes)
                vehNr += 1
                if (vehNr >= maxMobil):
                    break

        print("</routes>", file=routes)

if __name__ == "__main__":
    random.seed(42)  # make tests reproducible
    if len(sys.argv) < 3:
        print("usage: " + sys.argv[0] + " <waktu> <jumlah mobil>")
        sys.exit()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    sumoBinary = checkBinary('sumo')
    sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile(int(sys.argv[1]), int(sys.argv[2]))

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                             "--full-output", "output.xls", "--tripinfo-output", "tripinfo.xml"])
    report_gui()
