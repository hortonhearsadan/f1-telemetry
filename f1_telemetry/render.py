import curses

from f1_2019_telemetry.packets import (
    CarTelemetryData_V1,
    PacketSessionData_V1,
    TrackIDs,
)

from f1_telemetry.ascii_car import Component, AsciiCar
from f1_telemetry.formatting import (
    STATUS_COLOUR_OFFSET,
    TEAM_COLOUR_OFFSET,
    format_name,
    get_damage_colour,
    init_colours,
)
from f1_telemetry.lapStatus import LapStatus


class Renderer:
    def __init__(self):
        self.scr = curses.initscr()
        self._cursor_mode = curses.curs_set(0)

        self.scr.leaveok(True)

        self.h, self.w = self.scr.getmaxyx()

        self._set_colours()

        self.car = AsciiCar()

        self._session_y_offset = 0
        self._lap_data_header_y_offset = 3
        self._lap_data_y_offset = 5
        self._current_car_data_y_offset = 26
        self._car_x_offset = 85

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
        track_name = self._format_track_id(session.trackId)
        session_duration = self._format_time(session.sessionDuration)
        session_time = f"{session_elapsed} / {session_duration}"

        self.scr.move(self._session_y_offset, 0)
        self.scr.clrtoeol()

        session_string = session_name + " - " + track_name
        x = self._center(session_string)
        self.scr.addstr(self._session_y_offset, x, session_string)

        x = self._center(session_time)
        self.scr.addstr(self._session_y_offset + 1, x, session_time)
        self.scr.clrtoeol()

    def print_lap_data_header(self):
        msg = f" P. NAME                 | CURRENT LAP  | LAST LAP     | BEST LAP     | STATUS"

        self.scr.addstr(self._lap_data_header_y_offset, 2, msg)

    def print_lap_data(self, lap_data, name: str, team_index: dict):
        pos = self._get_position_value(lap_data)
        clt = self._format_time(lap_data.current_lap_time, with_millis=True)
        llt = self._format_time(lap_data.last_lap_time, with_millis=True)
        blt = self._format_time(lap_data.best_lap_time, with_millis=True)
        status = self._format_status(lap_data)
        msg = f"{pos:<3s} {format_name(name):20s} | {clt} | {llt} | {blt} | {status}"

        self.scr.addstr(
            self._lap_data_y_offset + lap_data.position - 1,
            2,
            msg,
            self._get_team_colour(team_index, name),
        )
        self.scr.clrtoeol()

    def print_car_data(self, car_data: CarTelemetryData_V1):
        self.scr.addstr(
            self._current_car_data_y_offset, 2, f"{car_data.speed:3d} km/h | "
        )
        self.scr.addstr(
            self._current_car_data_y_offset,
            15,
            f"{car_data.engineRPM:5d} RPM | ",
            self._get_rpm_color(car_data.revLightsPercent),
        )
        self.scr.addstr(
            self._current_car_data_y_offset,
            30,
            f"Gear: {self._format_gear(car_data.gear)}",
        )

        self.scr.clrtoeol()

        throttle, _ = divmod(round(car_data.throttle * 100), 5)
        brake, _ = divmod(round(car_data.brake * 100), 5)
        self.scr.addstr(self._current_car_data_y_offset + 2, 2, "Throttle :")
        self.scr.addstr(self._current_car_data_y_offset + 3, 2, "Brake    :")
        self.scr.addstr(self._current_car_data_y_offset + 4, 2, "RPM      :")

        self.scr.addstr(
            self._current_car_data_y_offset + 2,
            13,
            "|" * throttle,
            curses.color_pair(STATUS_COLOUR_OFFSET),
        )

        self.scr.clrtoeol()

        self.scr.addstr(
            self._current_car_data_y_offset + 3,
            13,
            "|" * brake,
            curses.color_pair(STATUS_COLOUR_OFFSET + 1),
        )

        self.scr.clrtoeol()

        if car_data.revLightsPercent > 1:
            yellow_revs, _ = divmod(min(round(car_data.revLightsPercent), 70), 5)
            green_revs, _ = divmod(
                max(min(round(car_data.revLightsPercent), 90) - 70, 0), 5
            )
            red_revs, _ = divmod(
                max(min(round(car_data.revLightsPercent), 100) - 90, 0), 5
            )

            self.scr.addstr(
                self._current_car_data_y_offset + 4, 13, "|" * yellow_revs,
            )
            self.scr.clrtoeol()

            self.scr.addstr(
                self._current_car_data_y_offset + 4,
                13 + 14,
                "|" * green_revs,
                curses.color_pair(STATUS_COLOUR_OFFSET + 2),
            )
            self.scr.clrtoeol()
            #
            self.scr.addstr(
                self._current_car_data_y_offset + 4,
                13 + 18,
                "|" * red_revs,
                curses.color_pair(STATUS_COLOUR_OFFSET + 1),
            )

            self.scr.clrtoeol()

    def print_damage_data(self, car_status):
        damage_data = {
            Component.LeftWing: car_status.frontLeftWingDamage,
            Component.RightWing: car_status.frontRightWingDamage,
            Component.RearWing: car_status.rearWingDamage,
            Component.BackLeftTyre: car_status.tyresDamage[0],
            Component.BackRightTyre: car_status.tyresDamage[1],
            Component.FrontLeftTyre: car_status.tyresDamage[2],
            Component.FrontRightTyre: car_status.tyresDamage[3],
            Component.Body: 0,
        }
        self.render_car(damage_data)

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
            9: "One-Shot Qualifying",
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

    def _set_colours(self):
        init_colours()

    def _get_rpm_color(self, percentage):
        if percentage > 90:
            return curses.color_pair(STATUS_COLOUR_OFFSET + 1)
        elif percentage > 70:
            return curses.color_pair(STATUS_COLOUR_OFFSET)
        return curses.color_pair(0)

    def _get_team_colour(self, team_index, name):
        return curses.color_pair(TEAM_COLOUR_OFFSET + team_index[name]) | curses.A_BOLD

    def render_car(self, damage_data):
        self._render_fl_tyre(get_damage_colour(damage_data[Component.FrontLeftTyre]))
        self._render_fr_tyre(get_damage_colour(damage_data[Component.FrontRightTyre]))
        self._render_bl_tyre(get_damage_colour(damage_data[Component.BackLeftTyre]))
        self._render_br_tyre(get_damage_colour(damage_data[Component.BackRightTyre]))

        self._render_body(get_damage_colour(damage_data[Component.Body]))
        self._render_left_wing(get_damage_colour(damage_data[Component.LeftWing]))
        self._render_right_wing(get_damage_colour(damage_data[Component.RightWing]))
        self._render_rear_wing(get_damage_colour(damage_data[Component.RearWing]))

    def _render_ascii(self, ascii_string, y_offset, x_offset, colour):
        extra_y_offset = self._lap_data_y_offset
        extra_x_offset = self._car_x_offset
        for y, line in enumerate(ascii_string.splitlines()):
            self.scr.addstr(
                y_offset + extra_y_offset + y, x_offset + extra_x_offset, line, colour
            )

    def _render_left_wing(self, colour):
        x, y = self.car.left_wing_0
        self._render_ascii(self.car.left_wing, y, x, colour)

    def _render_right_wing(self, colour):
        x, y = self.car.right_wing_0
        self._render_ascii(self.car.right_wing, y, x, colour)

    def _render_body(self, colour):
        x, y = self.car.body_0
        self._render_ascii(
            self.car.body, y, x, colour,
        )

    def _render_rear_wing(self, colour):
        x, y = self.car.rear_wing_0
        self._render_ascii(self.car.rear_wing, y, x, colour)

    def _render_fl_tyre(self, colour):
        x, y = self.car.fl_tyre_0
        self._render_ascii(self.car.tyre, y, x, colour)

    def _render_fr_tyre(self, colour):
        x, y = self.car.fr_tyre_0
        self._render_ascii(self.car.tyre, y, x, colour)

    def _render_bl_tyre(self, colour):
        x, y = self.car.bl_tyre_0
        self._render_ascii(self.car.tyre, y, x, colour)

    def _render_br_tyre(self, colour):
        x, y = self.car.br_tyre_0
        self._render_ascii(self.car.tyre, y, x, colour)

    def _get_position_value(self, lap_data):
        if lap_data.status == LapStatus.Retired:
            return "RET"
        elif lap_data.status == LapStatus.NotClassified:
            return "N/C"
        elif lap_data.status == LapStatus.Disqualified:
            return "DSQ"
        return str(lap_data.position)+"."

    def _format_status(self, lap_data):
        pit = "P" if lap_data.in_pit else " "
        penalties = str(lap_data.penalties)

        return pit + "+" + str(penalties)

    def _format_track_id(self, track_id):
        return TrackIDs.get(track_id, "Unknown")
