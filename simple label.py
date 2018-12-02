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
import mysql.connector
from mysql.connector import Error
from xml.dom import minidom

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
 
def connect():
    """ Connect to MySQL database """
    global Eksekusi,conn
    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='skripsi',
                                       user='root',
                                       password='iimsemok')
        if conn.is_connected():
            print('Connected to MySQL database')
        
        Eksekusi = conn.cursor()
        # sql = "select * from hasil"
        # cursor.execute(sql)

    except Error as e:
        print(e)
 

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

    # print("ave ",speed1, veh1, avespeedveh1)
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
    Tkinter.Label(master, width=w1, text='Jumlah per Kelas Kendaraan').grid(row=4,column=0)
    Tkinter.Label(master, width=w1, text='Kelas 1').grid(row=5,column=0)
    Tkinter.Label(master, width=w2, text=kls1).grid(row=5,column=1)
    Tkinter.Label(master, width=w1, text='Kelas 2').grid(row=6,column=0)
    Tkinter.Label(master, width=w2, text=kls2).grid(row=6,column=1)
    Tkinter.Label(master, width=w1, text='Kelas 3').grid(row=7,column=0)
    Tkinter.Label(master, width=w2, text=kls3).grid(row=7,column=1)
    Tkinter.Label(master, width=w1, text='Kelas 4').grid(row=8,column=0)
    Tkinter.Label(master, width=w2, text=kls4).grid(row=8,column=1)
    Tkinter.Label(master, width=w1, text='Kelas 5').grid(row=9,column=0)
    Tkinter.Label(master, width=w2, text=kls5).grid(row=9,column=1)
    thread.start_new_thread(run, (mobilRoad, mobilTotal, speedRoad, speedMax))
    master.mainloop()

def report_rekap():
    master2 = Tkinter.Tk()
   
    w1=20
    w2=20
    w3=20
    w4=20
    Tkinter.Label(master2, width=50, text='Rekapitulasi Per Kelas Kendaraan').grid(row=0,column=0)
    Tkinter.Label(master2, width=w1, text='Kelas Kendaraan').grid(row=1,column=0)
    Tkinter.Label(master2, width=w2, text='Jumlah').grid(row=1,column=1)
    Tkinter.Label(master2, width=w3, text='Rata2 Kecepatan').grid(row=1,column=2)
    Tkinter.Label(master2, width=w4, text='Rata2 WaktuTempuh').grid(row=1,column=3)
    brs=0

    bacahsl = "SELECT * from hasil"
    try :
        Eksekusi.execute(bacahsl)
        hslbaca = Eksekusi.fetchall()
        # baca data
        for row in hslbaca :
            Tkinter.Label(master2, width=w1, text=row[0]).grid(row=2+brs,column=0)
            Tkinter.Label(master2, width=w2, text=row[1]).grid(row=2+brs,column=1)
            Tkinter.Label(master2, width=w3, text=row[2]).grid(row=2+brs,column=2)
            Tkinter.Label(master2, width=w4, text=row[3]).grid(row=2+brs,column=3)
            brs += 1
    except :
        print("error fetch data")
    conn.commit()

    master2.mainloop()

def generate_routefile(timeSteps, maxMobil, remissionTime = 153):
    """Bikin file route.
    timeSteps: jumlah maksimal time ticks
    maxMobil: jumlah maksimal mobil
    remissionTime: pengampunan waktu, biar jumlah mobilnya sesuai keinginan
    """
    global kls1
    global kls2
    global kls3
    global kls4
    global kls5
    global kelas

    kls1 = 0
    kls2 = 0
    kls3 = 0
    kls4 = 0
    kls5 = 0

    # Probability car summoned
    pMobil = 1. * maxMobil / (timeSteps - remissionTime)
    with open("data/cross.rou.xml", "w") as routes:
        # Red, green, ungu, yellow, cyan
        print("""<routes>
        <vType id="type1" accel="0.8" decel="6.5" sigma="0.5" length="8" minGap="2.5" maxSpeed="6" color="red" guiShape="passenger"/>
        <vType id="type2" accel="0.9" decel="7.5" sigma="0.5" length="7" minGap="2.5" maxSpeed="11" color="green" guiShape="passenger"/>
        <vType id="type3" accel="1.1" decel="6.5" sigma="0.5" length="6" minGap="2.5" maxSpeed="16" color="blue" guiShape="passenger"/>
        <vType id="type4" accel="1.2" decel="5.5" sigma="0.5" length="6" minGap="2.5" maxSpeed="17" color="yellow" guiShape="passenger"/>
        <vType id="type5" accel="1.4" decel="4.5" sigma="0.5" length="4" minGap="2.5" maxSpeed="18" color="orange" guiShape="passenger"/>

        <route id="right" edges="12 23 34" />""", file=routes)
        vehNr = 0
        for i in range(timeSteps):
            if random.uniform(0, 1) < pMobil:
                kelas = random.randint(1,5)
                dLane = random.randint(0,1)
                print('<vehicle id="right_%i" type="type%i" route="right" depart="%i" departLane="%i" />' % (
                    vehNr, kelas, i, dLane), file=routes)
                if (vehNr >= maxMobil):
                    break

                if (kelas==1):
                    kls1 += 1
                elif (kelas==2):
                    kls2 += 1
                elif kelas==3:
                    kls3 += 1
                elif kelas==4:
                    kls4 += 1
                elif kelas==5:
                    kls5 += 1
                vehNr += 1

        print("</routes>", file=routes)

if __name__ == "__main__":
    connect()

    # hapus data dari tabel hasil
    hpshsl = "delete from hasil"
    Eksekusi.execute(hpshsl)
    conn.commit()

    # random.seed(1)  # make tests reproducible
    if len(sys.argv) < 4:
        print("usage: " + sys.argv[0] + " <waktu> <jumlah mobil> <jumlah lajur>")
        sys.exit()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    sumoBinary = checkBinary('sumo')
    sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    xmlFile = "tripinfo.xml"
    if sys.argv[3]==1:
        traci.start([sumoBinary, "-c", "data/cross1.sumocfg",
                             "--full-output", "output.xls", "--tripinfo-output", xmlFile])

    if sys.argv[3]==2:
        traci.start([sumoBinary, "-c", "data/cross2.sumocfg",
                             "--full-output", "output.xls", "--tripinfo-output", xmlFile])

    if sys.argv[3]==3:
        traci.start([sumoBinary, "-c", "data/cross3.sumocfg",
                             "--full-output", "output.xls", "--tripinfo-output", xmlFile])

    if sys.argv[3]==4:
        traci.start([sumoBinary, "-c", "data/cross4.sumocfg",
                             "--full-output", "output.xls", "--tripinfo-output", xmlFile])
    report_gui()

    xmldoc = minidom.parse(xmlFile)
    trips = xmldoc.getElementsByTagName('tripinfo')
    print(len(trips))
    length = 780
    avgSpeed = {'type1': 0.0, 'type2': 0.0, 'type3': 0.0, 'type4': 0.0, 'type5': 0.0}
    vehCount = {'type1': 0, 'type2': 0, 'type3': 0, 'type4': 0, 'type5': 0}
    vehDurat = {'type1': 0, 'type2': 0, 'type3': 0, 'type4': 0, 'type5': 0}
    for trip in trips:
        duration = float(trip.attributes['duration'].value)
        speed = length / duration
        vType = trip.attributes['vType'].value
        avgSpeed[vType] += speed
        vehCount[vType] += 1
        vehDurat[vType] += duration
    
    print('rata rata kecepatan')
    for kelas in ['type1', 'type2', 'type3', 'type4', 'type5']:
        vehcoun = vehCount[kelas]
        rataspe = (avgSpeed[kelas] / vehCount[kelas])
        ratadur = (vehDurat[kelas] / vehCount[kelas])
        print(kelas, ': ',vehcoun,': ',rataspe,': ',ratadur)
        
        # simpan data
        savehsl = "INSERT INTO hasil(kelas,jumlah,ratakec,ratatempuh) VALUES(%s,%s,%s,%s)"
        datahsl = (kelas,vehcoun,rataspe,ratadur)
        Eksekusi.execute(savehsl,datahsl)
        conn.commit()

    report_rekap()
