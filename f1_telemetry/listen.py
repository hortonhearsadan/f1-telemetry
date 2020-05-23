import socket
from f1_2019_telemetry.packets import (
    unpack_udp_packet,
    PacketLapData_V1,
    PacketParticipantsData_V1,
)

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(("", 20777))


class PacketProcessor:
    def __init__(self, socket):
        self.udp_socket = socket

        self.vehicle_index = {}

    def process(self):
        while True:
            udp_packet = self.listen()
            packet = unpack_udp_packet(udp_packet)

            self.parse_packet(packet)

    def listen(self):
        return self.udp_socket.recv(2048)

    def parse_packet(self, packet):
        if isinstance(packet, PacketParticipantsData_V1):
            self.set_vehicle_indices(packet)

        elif isinstance(packet, PacketLapData_V1) and self.is_initialised:
            positions = self.get_positions(packet)

            positions.sort(key=lambda x: x.current_position)
            for p in positions:
                print(p.current_position, self.vehicle_index[p.vehicle_idx])

    def set_vehicle_indices(self, packet):
        for i, participant in enumerate(packet.participants):
            self.vehicle_index[i] = participant.name.decode()

    @staticmethod
    def get_positions(packet):
        return [
            Position(i, lap_data.carPosition)
            for i, lap_data in enumerate(packet.lapData)
        ]

    @property
    def is_initialised(self):
        return bool(self.vehicle_index)


class Position:
    __slots__ = ["vehicle_idx", "current_position"]

    def __init__(self, vehicle_idx, current_position):
        self.vehicle_idx = vehicle_idx
        self.current_position = current_position


PacketProcessor(udp_socket).process()
