from enum import Enum

left_wing = """ ___________/--
 ||||||||||||| 
 |________/--| 
 |            |"""

right_wing = """--\___________ 
|||||||||||||| 
|--\_________| 
|            | """

tyre = """ _____ 
|     |
|     |
|     |
|_____|"""

body = """      /  \      
     /    \     
----/      \----
---/        \---
  /          \  
 /            \ 
 |            | 
 |            | 
 |            | 
 \            / 
  \          /  
---|        |---
---|        |---
   |        |   """

rear_wing = """|------------------|
|------------------|
|------------------|"""


class Component(Enum):
    LeftWing = "left_wing"
    RightWing = "right_wing"
    FrontLeftTyre = "fl_tyre"
    FrontRightTyre = "fr_tyre"
    BackLeftTyre = "bl_tyre"
    BackRightTyre = "br_tyre"
    RearWing = "rear_wing"
    Body = "body"


class AsciiCar:
    def __init__(self):
        self.left_wing = left_wing
        self.right_wing = right_wing
        self.tyre = tyre
        self.body = body
        self.rear_wing = rear_wing

        self.left_wing_0 = None
        self.right_wing_0 = None
        self.fl_tyre_0 = None
        self.fr_tyre_0 = None
        self.br_tyre_0 = None
        self.bl_tyre_0 = None
        self.body_0 = None
        self.rear_wing_0 = None

        self._validate_car_design()

        self._set_component_coordinates()

    @property
    def components(self):
        return self.left_wing, self.right_wing, self.body, self.rear_wing, self.tyre

    @property
    def left_wing_width(self):
        return self.calc_component_width(self.left_wing)

    @property
    def left_wing_height(self):
        return self.calc_component_height(self.left_wing)

    @property
    def right_wing_width(self):
        return self.calc_component_width(self.right_wing)

    @property
    def right_wing_height(self):
        return self.calc_component_height(self.right_wing)

    @property
    def body_height(self):
        return self.calc_component_height(self.body)

    @property
    def body_width(self):
        return self.calc_component_width(self.body)

    @property
    def tyre_width(self):
        return self.calc_component_width(self.tyre)

    @property
    def tyre_height(self):
        return self.calc_component_height(self.tyre)

    @property
    def rear_wing_width(self):
        return self.calc_component_height(self.rear_wing)

    @staticmethod
    def calc_component_width(component: str):
        return len(component.splitlines()[0])

    @staticmethod
    def calc_component_height(component: str):
        return len(component.splitlines())

    def _validate_car_design(self):
        for c in self.components:
            split_comp = c.splitlines()
            if len({len(i) for i in split_comp}) != 1:
                raise ValueError("car design has non-square components")

    def _set_component_coordinates(self):
        self.left_wing_0 = (0, 0)
        self.right_wing_0 = (self.left_wing_width, 0)

        self.body_0 = (self.tyre_width, self.left_wing_height)

        self.fl_tyre_0 = (0, self.left_wing_height)
        self.fr_tyre_0 = (self.tyre_width + self.body_width, self.left_wing_height)
        self.bl_tyre_0 = (
            0,
            self.left_wing_height + self.body_height - self.tyre_height,
        )
        self.br_tyre_0 = (self.fr_tyre_0[0], self.bl_tyre_0[1])

        self.rear_wing_0 = (self.body_0[0] - 2, self.body_0[1] + self.body_height)
