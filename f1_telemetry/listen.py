#! /usr/bin/env python

import curses
import signal
import socket
import threading
import time

from f1_2019_telemetry.packets import (
    CarTelemetryData_V1,
    LapData_V1,
    PacketCarTelemetryData_V1,
    PacketLapData_V1,
    PacketParticipantsData_V1,
    PacketSessionData_V1,
    unpack_udp_packet,
    PacketCarStatusData_V1,
)

from f1_telemetry.render import Renderer

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(("", 20777))


class PacketProcessor:
    def __init__(self, socket):
        self.udp_socket = socket
        socket.settimeout(0)

        self.vehicle_index = {}
        self.team_index = {}

        self._renderer = None
        self.my_id = None

        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            raise Exception("Processor already running")

        t = threading.Thread(target=self.process)
        self._thread = t
        self._running = True

        self._renderer = Renderer()
        self._renderer.clear()

        t.start()

    def stop(self):
        if not self._running:
            raise Exception("Processor not running")

        self._running = False

        self._thread.join()
        self._thread = None

        self._renderer.destroy()
        self._renderer = None

    def handle_signal(self, _signum, _stackframe):
        self.stop()

    def process(self):
        while self._running:
            udp_packet = self.listen()
            if not udp_packet:
                time.sleep(0.1)
                continue
            packet = unpack_udp_packet(udp_packet)

            self.parse_packet(packet)

    def listen(self):
        try:
            data = self.udp_socket.recv(2048)
        except BlockingIOError:
            return None

        return data

    def parse_packet(self, packet):

        if isinstance(packet, PacketParticipantsData_V1):
            self.set_indices(packet)

        self._render_session_info(packet)

        self._render_lap_data(packet)

        self._render_car_data(packet)

        self._render_damage_data(packet)

        self._renderer.refresh()

    def set_indices(self, packet):
        for i, participant in enumerate(packet.participants):
            name = participant.name.decode()
            self.vehicle_index[i] = name
            self.team_index[name] = participant.teamId

        self.my_id = packet.header.playerCarIndex

    @staticmethod
    def get_positions(packet):
        return [Position(i, lap_data) for i, lap_data in enumerate(packet.lapData)]

    @property
    def is_initialised(self):
        return bool(self.vehicle_index)

    def _render_session_info(self, packet):
        if isinstance(packet, PacketSessionData_V1):
            self._renderer.print_session_info(packet)

    def _render_lap_data(self, packet):
        if isinstance(packet, PacketLapData_V1) and self.is_initialised:
            positions = self.get_positions(packet)

            positions.sort(key=lambda x: x.position)
            self._renderer.print_lap_data_header()
            for p in positions:
                self._renderer.print_lap_data(
                    p, self.vehicle_index[p.vehicle_idx], self.team_index,
                )

    def _render_car_data(self, packet):
        if isinstance(packet, PacketCarTelemetryData_V1):
            if self.my_id is not None:
                car_data = packet.carTelemetryData[self.my_id]
                self._renderer.print_car_data(car_data)

    def _render_damage_data(self, packet):
        if isinstance(packet, PacketCarStatusData_V1):
            if self.my_id is not None:
                car_status = packet.carStatusData[self.my_id]
                self._renderer.print_damage_data(car_status)


class Position:
    def __init__(self, vehicle_idx, lap_data: LapData_V1):
        self.vehicle_idx = vehicle_idx
        self.position = lap_data.carPosition
        self.current_lap_time = lap_data.currentLapTime
        self.last_lap_time = lap_data.lastLapTime
        self.best_lap_time = lap_data.bestLapTime


def main():
    p = PacketProcessor(udp_socket)
    signal.signal(signal.SIGINT, p.handle_signal)
    p.start()


if __name__ == "__main__":
    main()
