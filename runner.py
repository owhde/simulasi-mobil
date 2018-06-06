

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random

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

def run():
    """execute the TraCI control loop"""
    step = 0

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1
    traci.close()
    sys.stdout.flush()

def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 900  # number of time steps
    # demand per second from different directions
    pWE = 1. / 25
    with open("data/cross.rou.xml", "w") as routes:
        # Red, green, ungu, yellow, cyan
        print("""<routes>
        <vType id="type1" accel="0.8" decel="5.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="5.55" color="1,0,0" guiShape="passenger"/>
        <vType id="type2" accel="0.9" decel="6.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="11.11" color="0,1,0" guiShape="passenger"/>
        <vType id="type3" accel="1.1" decel="7.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" color="1,0,1" guiShape="passenger"/>
        <vType id="type4" accel="1.2" decel="8.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="22.22" color="1,1,0" guiShape="passenger"/>
        <vType id="type5" accel="1.4" decel="9.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="27.78" color="0,1,1" guiShape="passenger"/>

        <route id="right" edges="12 23 34" />""", file=routes)
        lastVeh = 0
        vehNr = 0
        maxMobil = 100
        for i in range(N):
            if random.uniform(0, 1) < pWE:
                kelas = random.randint(1, 5)
                print('    <vehicle id="right_%i" type="type%i" route="right" depart="%i" />' % (
                    vehNr, kelas, i), file=routes)
                vehNr += 1
                if (vehNr >= maxMobil):
                    break
                lastVeh = i

        print("</routes>", file=routes)

if __name__ == "__main__":
    # options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    # if options.nogui:
    sumoBinary = checkBinary('sumo')
    # else:
    sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()