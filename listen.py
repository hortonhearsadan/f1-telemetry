import socket
from ctypes import *
from f1_2019_telemetry.packets import unpack_udp_packet, PacketLapData_V1, PacketParticipantsData_V1

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(('', 20777))

vehicle_index = {}


class PacketProcessor:
    def __init__(self, udp_socket):
        self.udp_socket = udp_socket

        self.vehicle_index = {}

    def process(self):
        while True:
            udp_packet = self.listen()
            packet = unpack_udp_packet(udp_packet)

            self.parse_packet(packet)
            if isinstance(packet, PacketParticipantsData_V1):
                # for f in packet.lapData:
                #     print(f.currentLapTime)
                for i, d in enumerate(packet.participants):
                    vehicle_index[i] = d.name.decode()
                    print(d.name.decode())
                pass
            print()

    def listen(self):
        return self.udp_socket.recv(2048)

    def parse_packet(self, packet):
        if isinstance(packet, PacketParticipantsData_V1):
            # for f in packet.lapData:
            #     print(f.currentLapTime)
            self.set_vehicle_indices(packet)

        if isinstance(packet, PacketLapData_V1):
            positions = []
            for i, data in enumerate(packet.lapData):
                positions.append((i, data.carPosition))

            positions.sort(key=lambda x: x[1])
            for p in positions:
                print(p[1], vehicle_index[p[0]])
            print()

    def set_vehicle_indices(self, packet):
        for i, participant in enumerate(packet.participants):
            self.vehicle_index[i] = participant.name.decode()
