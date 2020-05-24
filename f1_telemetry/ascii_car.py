left_wing = """______/--
|      
|____/--|
|       |"""

right_wing = """--\______
        |
|--\____|
|       |"""

tyre = """ _____ 
|     |
|     |
|     |
|_____|"""

body = """      
      /  \      
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


class AsciiCar:
    def __init__(self):
        self.left_wing = left_wing
        self.right_wing = right_wing
        self.tyre = tyre
        self.body = body
        self.rear_wing = rear_wing

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

    @staticmethod
    def calc_component_width(component: str):
        return max(len(line) for line in component.splitlines())

    @staticmethod
    def calc_component_height(component: str):
        return len(component.splitlines())
