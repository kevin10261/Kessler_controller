from kesslergame import KesslerController
from typing import Dict, Tuple
import math
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class Group12Controller(KesslerController):
    def __init__(self):
        super().__init__()

        # Step 1: Define Fuzzy Variables
        self.theta_delta = ctrl.Antecedent(np.arange(-6, 7, 0.1), 'theta_delta')  # [-6°, +6°]
        self.bullet_time = ctrl.Antecedent(np.arange(0, 10, 0.1), 'bullet_time')  # Time in seconds
        self.ship_turn = ctrl.Consequent(np.arange(-180, 181, 1), 'ship_turn')  # [-180°, +180°]
        self.ship_fire = ctrl.Consequent(np.arange(-1, 2, 1), 'ship_fire')  # Boolean (-1 to 1)

        # Step 2: Define Membership Functions
        # Theta Delta Memberships
        # Theta Delta Memberships (increased resolution)
        self.theta_delta['NL'] = fuzz.zmf(self.theta_delta.universe, -6, -3)  # Negative Large
        self.theta_delta['NM'] = fuzz.trimf(self.theta_delta.universe, [-5, -3, -1])  # Negative Medium
        self.theta_delta['NS'] = fuzz.trimf(self.theta_delta.universe, [-3, -1, 0])  # Negative Small
        self.theta_delta['Z'] = fuzz.trimf(self.theta_delta.universe, [-0.5, 0, 0.5])  # Zero
        self.theta_delta['PS'] = fuzz.trimf(self.theta_delta.universe, [0, 1, 3])  # Positive Small
        self.theta_delta['PM'] = fuzz.trimf(self.theta_delta.universe, [1, 3, 5])  # Positive Medium
        self.theta_delta['PL'] = fuzz.smf(self.theta_delta.universe, 3, 6)  # Positive Large

        # Bullet Time Memberships (increased resolution)
        self.bullet_time['S'] = fuzz.trimf(self.bullet_time.universe, [0, 1, 3])  # Small
        self.bullet_time['M'] = fuzz.trimf(self.bullet_time.universe, [2, 5, 8])  # Medium
        self.bullet_time['L'] = fuzz.trimf(self.bullet_time.universe, [4, 6, 10])  # Large

        # Ship Turn Memberships
        self.ship_turn['hard_left'] = fuzz.trimf(self.ship_turn.universe, [-180, -180, -90])
        self.ship_turn['soft_left'] = fuzz.trimf(self.ship_turn.universe, [-90, -45, 0])
        self.ship_turn['no_turn'] = fuzz.trimf(self.ship_turn.universe, [-10, 0, 10])
        self.ship_turn['soft_right'] = fuzz.trimf(self.ship_turn.universe, [0, 45, 90])
        self.ship_turn['hard_right'] = fuzz.trimf(self.ship_turn.universe, [90, 180, 180])

        # Ship Fire Memberships
        self.ship_fire['no_fire'] = fuzz.trimf(self.ship_fire.universe, [-1, -1, 0])
        self.ship_fire['fire'] = fuzz.trimf(self.ship_fire.universe, [0, 1, 1])

        # Step 3: Define Fuzzy Rules
        self.rules = [
            ctrl.Rule(self.theta_delta['Z'], self.ship_turn['no_turn']),
            ctrl.Rule(self.theta_delta['NS'], self.ship_turn['soft_left']),
            ctrl.Rule(self.theta_delta['PS'], self.ship_turn['soft_right']),
            ctrl.Rule(self.theta_delta['NM'] | self.theta_delta['NL'], self.ship_turn['hard_left']),
            ctrl.Rule(self.theta_delta['PM'] | self.theta_delta['PL'], self.ship_turn['hard_right']),
            ctrl.Rule(self.bullet_time['S'], self.ship_fire['fire']),
            ctrl.Rule(self.bullet_time['M'] & self.theta_delta['Z'], self.ship_fire['fire']),
            ctrl.Rule(self.bullet_time['L'], self.ship_fire['no_fire'])
        ]

        # Step 4: Create the Control System
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)


    def actions(self, ship_state: Dict, input_data: Dict) -> Tuple[float, float, bool, bool]:
        ship_x, ship_y = ship_state["position"]
        ship_heading = ship_state["heading"]
        bullet_speed = 800  # Fixed bullet speed in m/s
        closest_asteroid, min_distance = None, float('inf')

        # Find closest asteroid
        for asteroid in input_data["asteroids"]:
            asteroid_x, asteroid_y = asteroid["position"]
            distance = math.sqrt((asteroid_x - ship_x) ** 2 + (asteroid_y - ship_y) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_asteroid = asteroid

        if closest_asteroid:
            asteroid_x, asteroid_y = closest_asteroid["position"]
            asteroid_vx, asteroid_vy = closest_asteroid["velocity"]

            # Compute time to intercept (solve quadratic equation)
            dx, dy = asteroid_x - ship_x, asteroid_y - ship_y
            a = asteroid_vx ** 2 + asteroid_vy ** 2 - bullet_speed ** 2
            b = 2 * (dx * asteroid_vx + dy * asteroid_vy)
            c = dx ** 2 + dy ** 2
            discriminant = b ** 2 - 4 * a * c

            if discriminant >= 0:
                t1 = (-b + math.sqrt(discriminant)) / (2 * a)
                t2 = (-b - math.sqrt(discriminant)) / (2 * a)
                bullet_t = min(t for t in [t1, t2] if t > 0)

                # Compute intercept point
                intrcpt_x = asteroid_x + asteroid_vx * (bullet_t + 1 / 30)
                intrcpt_y = asteroid_y + asteroid_vy * (bullet_t + 1 / 30)
                theta1 = math.degrees(math.atan2(intrcpt_y - ship_y, intrcpt_x - ship_x))
                theta_delta = ((theta1 - ship_heading + 180) % 360) - 180

                # Input to fuzzy controller
                self.simulation.input['theta_delta'] = theta_delta
                self.simulation.input['bullet_time'] = bullet_t
                self.simulation.compute()

                turn_rate = self.simulation.output['ship_turn']
                fire = self.simulation.output['ship_fire'] > 0.5
            else:
                turn_rate, fire = 0.0, False
        else:
            turn_rate, fire = 0.0, False

        return 0.5, turn_rate, fire, False


    @property
    def name(self) -> str:
        return "Group 12 Controller"
