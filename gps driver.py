#!/usr/bin/env python3.8
import rospy 
import serial 
import sys
import utm
import std_msgs.msg
from math import sin, pi
from gps_driver.msg import gps_msg

def get_time(time):
    secs = float(time[0.2])*3600 + secs + float(time[2.4])*60 + float(time[4:])
    return secs

if __name__ == '__main__': 

    rospy.init_node('gpsdata')
    serial_port = sys.argv[1]
    #data from port
    port = serial.Serial(serial_port, 4800, timeout = 5)
    pub = rospy.Publisher('gps', gps_msg, queue_size=10)
    gps_msg_data = gps_msg()
    gps_msg.Header.frame_ID = "GPS1_Frame"
    splitline = port.split(',')
    # parsing data
    while not rospy.is_shutdown(): 
        init_line = port.readline() 
        line = init_line.decode('utf-8')
        splitline = port.split(',')
        if splitline[0] == '$GPGGA':
            latitude = splitline[2]
            lat_dir = splitline[3]
            longitude = splitline[4]
            long_dir = splitline[5]
            altitude = splitline[9]
            t_secs = splitline[1]
            secs = rospy.Time.from_sec(t_secs)
            
            #Lat lon degree conversion
            lat_ary = latitude.split('.')
            temp1 = lat_ary[0][-2:]
            deg_lat = lat_ary[0][:-2]
            temp2 = temp1+'.'+lat_ary[1]

            lag_ary = longitude.split('.')
            temp3 = lag_ary[0][-2:]
            temp4 = temp3+'.'+lag_ary[1]

            deg_log = lag_ary[0][:-2]

            lat_min = (float(temp2)/60)
            log_min = (float(temp4)/60)

            final_lat = float(deg_lat) + float(lat_min)
            final_long = float(deg_log) + float(log_min)
            if(long_dir == 'W'):
                final_long = final_long * -1

            if(lat_dir == 'S'):
                final_lat = final_lat * -1

            #print('final lat '+str(final_lat))
            #print('final log'+str(final_long))

            #utm data conversion
            utm_data = utm.from_latlon(final_lat,final_long)
		    #The return has the form (EASTING, NORTHING, ZONE_NUMBER, ZONE_LETTER).
            #ROS custom msg parameters
            gps_msg_data = gps_msg()
            gps_msg_data.frame_ID = 'GPS1_Frame'
            gps_msg_data.Header.stamp = secs
            gps_msg_data.latitude = final_lat  
            gps_msg_data.logitude = final_long
            gps_msg_data.altitude = float(splitline[9])
            gps_msg_data.UTM_easting = float(utm_data[0])
            gps_msg_data.UTM_northing = float(utm_data[1])
            gps_msg_data.Zone = int(utm_data[2])
            gps_msg_data.Letter = utm_data[3]
            
            pub.publish(gps_msg_data)   #gps_msg_data is ROS topic

else:
    rospy.ROSInterruptException; 
    port.close() 

