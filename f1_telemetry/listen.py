#! /usr/bin/env python

import curses
import socket
from datetime import timedelta

from f1_2019_telemetry.packets import (
    CarTelemetryData_V1,
    PacketCarTelemetryData_V1,
    PacketLapData_V1,
    PacketParticipantsData_V1,
    PacketSessionData_V1,
    unpack_udp_packet,
)

from f1_telemetry import server
from f1_telemetry.formatting import init_team_colour_pairs

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(("", 20777))

# server.serve()


class PacketProcessor:
    def __init__(self, socket):
        self.udp_socket = socket

        self.vehicle_index = {}
        self.team_index = {}

        self.renderer = Renderer()
        self.renderer.clear()

        self.my_id = None

    def process(self):
        while True:
            udp_packet = self.listen()
            packet = unpack_udp_packet(udp_packet)

            self.parse_packet(packet)

    def listen(self):
        return self.udp_socket.recv(2048)

    def parse_packet(self, packet):
        if isinstance(packet, PacketSessionData_V1):
            self.renderer.print_session_time(
                packet.sessionTimeLeft, packet.sessionDuration
            )

        elif isinstance(packet, PacketParticipantsData_V1):
            self.set_indices(packet)

        elif isinstance(packet, PacketLapData_V1) and self.is_initialised:
            positions = self.get_positions(packet)

            positions.sort(key=lambda x: x.current_position)
            for p in positions:
                self.renderer.print_position(
                    p.current_position,
                    self.vehicle_index[p.vehicle_idx],
                    self.team_index,
                )

        elif isinstance(packet, PacketCarTelemetryData_V1):
            if self.my_id is not None:
                car_data = packet.carTelemetryData[self.my_id]
                self.renderer.print_car_data(car_data)

        self.renderer.refresh()

    def set_indices(self, packet):
        for i, participant in enumerate(packet.participants):
            name = participant.name.decode()
            self.vehicle_index[i] = name
            self.team_index[name] = participant.teamId

            if participant.driverId == 15:  # Bottas
                self.my_id = i

    @staticmethod
    def get_positions(packet):
        return [
            Position(i, lap_data.carPosition)
            for i, lap_data in enumerate(packet.lapData)
        ]

    @property
    def is_initialised(self):
        return bool(self.vehicle_index)


class Renderer:
    def __init__(self):
        self.scr = curses.initscr()
        self.scr.leaveok(True)

        self._set_team_colours()

    def clear(self):
        self.scr.clear()
        self.refresh()

    def refresh(self):
        self.scr.refresh()

    def print_session_time(self, time_left: int, total_duration: int):
        duration = total_duration - time_left
        m, s = divmod(duration, 60)
        h, m = divmod(m, 60)

        self.scr.addstr(0, 0, f"SESSION TIME: {h:02d}:{m:02d}:{s:02d}")

    def print_position(self, position: int, name: str, team_index):
        self.scr.addstr(
            1 + position,
            0,
            f"{position:2d}. {name}",
            curses.color_pair(100 + team_index[name]),
        )
        self.scr.clrtoeol()

    def print_car_data(self, car_data: CarTelemetryData_V1):
        self.scr.addstr(
            23,
            0,
            f"{car_data.speed:3d} km/h | "
            f"{car_data.engineRPM:5d} RPM | "
            f"Gear: {self._format_gear(car_data.gear)}",
        )
        self.scr.clrtoeol()
        self.scr.addstr(
            24,
            0,
            f"Throttle: {round(car_data.throttle*100):3d}% | "
            f"Brake: {round(car_data.brake*100):3d}%",
        )
        self.scr.clrtoeol()

    def _format_gear(self, n):
        return {
            -1: "R",
            0: "N",
            1: "1st",
            2: "2nd",
            3: "3rd",
            4: "4th",
            5: "5th",
            6: "6th",
            7: "7th",
            8: "8th",
        }[n]

    def _set_team_colours(self):
        init_team_colour_pairs()


class Position:
    __slots__ = ["vehicle_idx", "current_position"]

    def __init__(self, vehicle_idx, current_position):
        self.vehicle_idx = vehicle_idx
        self.current_position = current_position


PacketProcessor(udp_socket).process()
