#!/usr/bin/python3

import os
import serial
import time
import json
import pymongo
from pymongo import MongoClient

#----- MongoDB Local Server parameters
global host_address
global host_name
global host_password
global host_port
global db_name
global db_collection_name

#----- STM32 Microcontroller parameters
global serial_port
global serial_baudrate
global serial_bytesize
global serial_parity
global serial_stopbits
global serial_timeout

# Connect to the mongoDB sever local network to store database
def MongoDB_Connection(hostname_strval, username_strval, password_strval, port_val):
    client_connection = None
    try:
        client_connection = MongoClient(
            host = hostname_strval, #establishes connection to the host and port (27017), from docker
            username = username_strval,
            password = password_strval,
            port= port_val)
    except Error as err:
        return (f"Error: '{err}'")
    return client_connection

# Serial Port STM32 receibe dataset
def Serial_Connection(port_stval, baudrate_val, bytesize_par, parity_par, stopbits_par, rtscts_bool, timeout_val):
    serial_port = None
    try:
        serial_port = serial.Serial(port= port_stval,
                            baudrate= baudrate_val,
                            bytesize= bytesize_par,
                            parity= parity_par,
                            stopbits= stopbits_par,
                            rtscts= rtscts_bool,
                            timeout= timeout_val)
    except Error as err:
        return (f"Error: '{err}'")
    return serial_port

def main():
    #--------- Connect to MongoDB Server
    host_address = os.environ['HOSTADDRESS']
    host_name = os.environ['DBNAME']
    host_password = os.environ['DBPASSWORD']
    host_port = os.environ['HOSTPORT']
    client = MongoDB_Connection(host_address, host_name, host_password, host_port)

    #--------- Connect to a particular db for storing sensor data
    db_name = os.environ['DBNANE']
    db_collection_name = os.environ['DBCOLLECTIONNAME']
    # Connect to a particular db
    my_db = client[db_name] # Important ---> In MongoDB, a database is not created until it gets content!
    # To create a collection in MongoDB
    my_col = my_db[db_collection_name] # Important ---> In MongoDB, a collection is not created until it gets content!

    #--------- Connect to the STM32 Microcontroller
    serial_port = os.environ['SERIALPORT']
    serial_baudrate = os.environ['SERIALBAUDRATE']
    serial_bytesize = os.environ['SERIALBYTESIZE']
    serial_parity = os.environ['SERIALPARITY']
    serial_stopbits = os.environ['SERIALSTOPBITS']
    serial_timeout = os.environ['SERIALTIMEOUT']
    serial_port = Serial_Connection(serial_port, serial_baudrate, serial_bytesize, serial_parity, serial_stopbits, serial_timeout)
    print("Port Status:", serial_port.is_open)

    #--------- Read and Store loop
    while (serial_port.is_open):
        received_raw_data = serial_port.readline()  # raw data we receive
        json_string = received_raw_data[3:-3] # clear duffer data b'\x00jsonSTRINGDATA \r\n'
        json_string = json_string.replace("'", "\"") # we send json as single quotes we need double quotes in order for json package to function
        json_data = json.loads(json_string) # parse json_string with datatype dict
        #To insert a record, or document as it is called in MongoDB, into a collection, we use the insert_one() method.
        insert_result = my_col.insert_one(json_data)
        print(insert_result.inserted_id)
    serial_port.close()
    
if __name__ == "__main__":
    main()
