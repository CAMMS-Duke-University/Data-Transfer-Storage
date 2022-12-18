FROM python:3

COPY receive_from_serial_port.py .

RUN pip3 install pyserial pymongo

CMD ["python3", "./receive_from_serial_port.py"]
