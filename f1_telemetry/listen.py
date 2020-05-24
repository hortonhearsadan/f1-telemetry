#! /usr/bin/env python

import curses
import signal
import socket
import threading
import time
from datetime import timedelta

from f1_2019_telemetry.packets import (
    CarTelemetryData_V1,
    LapData_V1,
    PacketCarTelemetryData_V1,
    PacketLapData_V1,
    PacketParticipantsData_V1,
    PacketSessionData_V1,
    unpack_udp_packet,
)

from f1_telemetry import server

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(("", 20777))

# server.serve()


class PacketProcessor:
    def __init__(self, socket):
        self.udp_socket = socket
        socket.settimeout(0)

        self.vehicle_index = {}

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
        if isinstance(packet, PacketSessionData_V1):
            self._renderer.print_session_info(packet)

        elif isinstance(packet, PacketParticipantsData_V1):
            self.set_vehicle_indices(packet)

        elif isinstance(packet, PacketLapData_V1) and self.is_initialised:
            positions = self.get_positions(packet)

            positions.sort(key=lambda x: x.position)
            self._renderer.print_lap_data_header()
            for p in positions:
                self._renderer.print_lap_data(p, self.vehicle_index[p.vehicle_idx])

        elif isinstance(packet, PacketCarTelemetryData_V1):
            if self.my_id is not None:
                car_data = packet.carTelemetryData[self.my_id]
                self._renderer.print_car_data(car_data)

        self._renderer.refresh()

    def set_vehicle_indices(self, packet):
        for i, participant in enumerate(packet.participants):
            self.vehicle_index[i] = participant.name.decode()

            if participant.driverId == 15:  # Bottas
                self.my_id = i

    @staticmethod
    def get_positions(packet):
        return [Position(i, lap_data) for i, lap_data in enumerate(packet.lapData)]

    @property
    def is_initialised(self):
        return bool(self.vehicle_index)


class Renderer:
    def __init__(self):
        self.scr = curses.initscr()
        self._cursor_mode = curses.curs_set(0)

        self.scr.leaveok(True)

        self.h, self.w = self.scr.getmaxyx()

        self._session_y_offset = 0
        self._lap_data_header_y_offset = 3
        self._lap_data_y_offset = 5
        self._current_car_data_y_offset = 26

    def destroy(self):
        curses.curs_set(self._cursor_mode)
        curses.endwin()

    def clear(self):
        self.scr.clear()
        self.refresh()

    def refresh(self):
        self.scr.refresh()

    def print_session_info(self, session: PacketSessionData_V1):
        session_name = self._format_session_type(session.sessionType)
        session_elapsed = self._format_time(
            session.sessionDuration - session.sessionTimeLeft
        )
        session_duration = self._format_time(session.sessionDuration)
        session_time = f"{session_elapsed} / {session_duration}"

        x = self._center(session_name)
        self.scr.addstr(self._session_y_offset, x, session_name)
        self.scr.clrtoeol()

        x = self._center(session_time)
        self.scr.addstr(self._session_y_offset + 1, x, session_time)
        self.scr.clrtoeol()

    def print_lap_data_header(self):
        msg = f" P. NAME                 | CURRENT LAP  | LAST LAP     | BEST LAP"

        self.scr.addstr(self._lap_data_header_y_offset, 2, msg)

    def print_lap_data(self, lap_data: "Position", name: str):
        pos = lap_data.position
        clt = self._format_time(lap_data.current_lap_time, with_millis=True)
        llt = self._format_time(lap_data.last_lap_time, with_millis=True)
        blt = self._format_time(lap_data.best_lap_time, with_millis=True)

        msg = f"{pos:2d}. {name:20s} | {clt} | {llt} | {blt}"

        self.scr.addstr(self._lap_data_y_offset + pos - 1, 2, msg)
        self.scr.clrtoeol()

    def print_car_data(self, car_data: CarTelemetryData_V1):
        self.scr.addstr(
            self._current_car_data_y_offset,
            2,
            f"{car_data.speed:3d} km/h | "
            f"{car_data.engineRPM:5d} RPM | "
            f"Gear: {self._format_gear(car_data.gear)}",
        )
        self.scr.clrtoeol()
        self.scr.addstr(
            self._current_car_data_y_offset + 1,
            2,
            f"Throttle: {round(car_data.throttle*100):3d}% | "
            f"Brake: {round(car_data.brake*100):3d}%",
        )
        self.scr.clrtoeol()

    def _center(self, s: str) -> int:
        return (self.w - len(s)) // 2

    def _format_session_type(self, type_):
        return {
            0: "Unknown",
            1: "Free Practice 1",
            2: "Free Practice 2",
            3: "Free Practice 3",
            4: "Free Practice (Short)",
            5: "Qualification 1",
            6: "Qualification 2",
            7: "Qualification 3",
            8: "Qualification (Short)",
            9: "OSQ?",
            10: "Race",
            11: "Race 2",
            12: "Time Trial",
        }[type_]

    def _format_time(self, nsecs, with_millis=False):
        if with_millis:
            millis = round((nsecs - int(nsecs)) * 1000)
        else:
            millis = 0

        nsecs = int(nsecs)

        m, s = divmod(nsecs, 60)
        h, m = divmod(m, 60)

        if with_millis:
            return f"{h:02d}:{m:02d}:{s:02d}.{millis:03d}"
        else:
            return f"{h:02d}:{m:02d}:{s:02d}"

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
