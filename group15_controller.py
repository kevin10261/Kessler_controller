from kesslergame import KesslerController
from typing import Dict, Tuple
import math, time
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class Group15Controller(KesslerController):
    def __init__(self):
        super().__init__()
        self.eval_frames = 0
        self.last_bomb_time = 0 

        # Step 1: Define Fuzzy Variables
        # Shared Variables
        self.theta_delta = ctrl.Antecedent(np.arange(-6, 7, 0.1), 'theta_delta')  # [-6°, +6°]
        self.bullet_time = ctrl.Antecedent(np.arange(0, 10, 0.1), 'bullet_time')  # Time in seconds
        self.asteroid_distance = ctrl.Antecedent(np.arange(0, 1001, 1), 'asteroid_distance')  # Distance to astroid
        self.act_bomb_distance = ctrl.Antecedent(np.arange(0, 1001, 1), 'act_bomb_distance')  #distance to astroid


        self.ship_turn = ctrl.Consequent(np.arange(-180, 181, 1), 'ship_turn')  # [-180°, +180°]
        self.ship_fire = ctrl.Consequent(np.arange(-1, 2, 1), 'ship_fire')  # Boolean (-1 to 1)
        self.ship_thrust = ctrl.Consequent(np.arange(-100, 101, 1), 'ship_thrust')  # [-100, 100]

        # Step 2: Define Membership Functions
        # Theta Delta Memberships
        self.theta_delta['NL'] = fuzz.zmf(self.theta_delta.universe, -6, -3)
        self.theta_delta['NM'] = fuzz.trimf(self.theta_delta.universe, [-5, -3, -1])
        self.theta_delta['NS'] = fuzz.trimf(self.theta_delta.universe, [-3, -1, 0])
        self.theta_delta['Z'] = fuzz.trimf(self.theta_delta.universe, [-0.5, 0, 0.5])
        self.theta_delta['PS'] = fuzz.trimf(self.theta_delta.universe, [0, 1, 3])
        self.theta_delta['PM'] = fuzz.trimf(self.theta_delta.universe, [1, 3, 5])
        self.theta_delta['PL'] = fuzz.smf(self.theta_delta.universe, 3, 6)

        self.asteroid_distance['close'] = fuzz.zmf(self.asteroid_distance.universe, 0, 190)
        self.asteroid_distance['medium'] = fuzz.trimf(self.asteroid_distance.universe, [185, 210, 310])
        self.asteroid_distance['far'] = fuzz.smf(self.asteroid_distance.universe, 300, 1000)



        self.bullet_time['S'] = fuzz.trimf(self.bullet_time.universe, [0, 1, 3])
        self.bullet_time['M'] = fuzz.trimf(self.bullet_time.universe, [2, 5, 8])
        self.bullet_time['L'] = fuzz.trimf(self.bullet_time.universe, [4, 6, 10])

        self.ship_turn['hard_left'] = fuzz.trimf(self.ship_turn.universe, [-180, -180, -90])
        self.ship_turn['soft_left'] = fuzz.trimf(self.ship_turn.universe, [-90, -45, 0])
        self.ship_turn['no_turn'] = fuzz.trimf(self.ship_turn.universe, [-10, 0, 10])
        self.ship_turn['soft_right'] = fuzz.trimf(self.ship_turn.universe, [0, 45, 90])
        self.ship_turn['hard_right'] = fuzz.trimf(self.ship_turn.universe, [90, 180, 180])

        self.ship_fire['no_fire'] = fuzz.trimf(self.ship_fire.universe, [-1, -1, 0])
        self.ship_fire['fire'] = fuzz.trimf(self.ship_fire.universe, [0, 1, 1])

        self.ship_thrust['Hard Brake'] = fuzz.trimf(self.ship_thrust.universe, [-100, -100, -50])
        self.ship_thrust['Soft Brake'] = fuzz.trimf(self.ship_thrust.universe, [-60, -30, -0])
        self.ship_thrust['Zero Thrust'] = fuzz.trimf(self.ship_thrust.universe, [-10, 0, 10])
        self.ship_thrust['Soft Thrust'] = fuzz.trimf(self.ship_thrust.universe, [10, 30, 60])
        self.ship_thrust['Hard Thrust'] = fuzz.trimf(self.ship_thrust.universe, [50, 100, 100])
        
        # Bomb rules
        self.bomb_rules()

        # Step 3: Define Fuzzy Rules
        self.rules = [
            # Turning Rules
            ctrl.Rule(self.theta_delta['Z'], self.ship_turn['no_turn']),
            ctrl.Rule(self.theta_delta['NS'], self.ship_turn['soft_left']),
            ctrl.Rule(self.theta_delta['PS'], self.ship_turn['soft_right']),
            ctrl.Rule(self.theta_delta['NM'] | self.theta_delta['NL'], self.ship_turn['hard_left']),
            ctrl.Rule(self.theta_delta['PM'] | self.theta_delta['PL'], self.ship_turn['hard_right']),
            # Firing Rules
            ctrl.Rule(self.bullet_time['S'], self.ship_fire['fire']),
            ctrl.Rule(self.bullet_time['M'] & self.theta_delta['Z'], self.ship_fire['fire']),
            ctrl.Rule(self.bullet_time['L'], self.ship_fire['no_fire']),
            # Thrust Rules 
            #'''
            #ctrl.Rule(self.asteroid_distance['close'] & self.theta_delta['Z'], self.ship_thrust['Zero Thrust']),
            #ctrl.Rule(self.asteroid_distance['close'] & (self.theta_delta['NS'] | self.theta_delta['PS']), self.ship_thrust['Soft Brake']),
            #ctrl.Rule(self.asteroid_distance['close'] & (self.theta_delta['NL'] | self.theta_delta['PL']), self.ship_thrust['Hard Brake']),
            #ctrl.Rule(self.asteroid_distance['medium'] & self.theta_delta['Z'], self.ship_thrust['Soft Thrust']),
            #ctrl.Rule(self.asteroid_distance['medium'] & (self.theta_delta['NS'] | self.theta_delta['PS']), self.ship_thrust['Zero Thrust']),
            #ctrl.Rule(self.asteroid_distance['medium'] & (self.theta_delta['NL'] | self.theta_delta['PL']), self.ship_thrust['Soft Brake']),
            #ctrl.Rule(self.asteroid_distance['far'] & self.theta_delta['Z'], self.ship_thrust['Hard Thrust']),
            #ctrl.Rule(self.asteroid_distance['far'] & (self.theta_delta['NS'] | self.theta_delta['PS']), self.ship_thrust['Soft Thrust']),
            #ctrl.Rule(self.asteroid_distance['far'] & (self.theta_delta['NL'] | self.theta_delta['PL']), self.ship_thrust['Zero Thrust']),
            #'''



            ctrl.Rule(self.asteroid_distance['far'] & self.act_bomb_distance['far'], self.ship_thrust['Hard Thrust']),
            ctrl.Rule(self.asteroid_distance['medium'] & self.act_bomb_distance['far'], self.ship_thrust['Soft Thrust']),
            ctrl.Rule(self.asteroid_distance['close'] & self.act_bomb_distance['far'], self.ship_thrust['Soft Brake']),

            ctrl.Rule(self.asteroid_distance['far'] & self.act_bomb_distance['medium'], self.ship_thrust['Soft Brake']),
            ctrl.Rule(self.asteroid_distance['medium'] & self.act_bomb_distance['medium'], self.ship_thrust['Soft Brake']),
            ctrl.Rule(self.asteroid_distance['close'] & self.act_bomb_distance['medium'], self.ship_thrust['Soft Brake']),

            ctrl.Rule(self.asteroid_distance['far'] & self.act_bomb_distance['close'], self.ship_thrust['Hard Brake']),
            ctrl.Rule(self.asteroid_distance['medium'] & self.act_bomb_distance['close'], self.ship_thrust['Hard Brake']),
            ctrl.Rule(self.asteroid_distance['close'] & self.act_bomb_distance['close'], self.ship_thrust['Hard Brake']),


            # Bullet Time Rules
            #ctrl.Rule(self.bullet_time['S'] & self.theta_delta['Z'], self.ship_thrust['Zero Thrust']),
            #ctrl.Rule(self.bullet_time['S'] & (self.theta_delta['NS'] | self.theta_delta['PS']), self.ship_thrust['Soft Brake']),
            #ctrl.Rule(self.bullet_time['S'] & (self.theta_delta['NL'] | self.theta_delta['PL']), self.ship_thrust['Hard Brake']),
            #ctrl.Rule(self.bullet_time['M'] & self.theta_delta['Z'], self.ship_thrust['Soft Thrust']),
            #ctrl.Rule(self.bullet_time['M'] & (self.theta_delta['NS'] | self.theta_delta['PS']), self.ship_thrust['Zero Thrust']),
            #ctrl.Rule(self.bullet_time['M'] & (self.theta_delta['NL'] | self.theta_delta['PL']), self.ship_thrust['Soft Brake']),
            #ctrl.Rule(self.bullet_time['L'] & self.theta_delta['Z'], self.ship_thrust['Hard Thrust']),
            #ctrl.Rule(self.bullet_time['L'] & (self.theta_delta['NS'] | self.theta_delta['PS']), self.ship_thrust['Soft Thrust']),
            #ctrl.Rule(self.bullet_time['L'] & (self.theta_delta['NL'] | self.theta_delta['PL']), self.ship_thrust['Zero Thrust']),
            
            # Combined Edge Cases
            #ctrl.Rule(self.asteroid_distance['close'] & self.bullet_time['S'], self.ship_thrust['Hard Brake']),
            #ctrl.Rule(self.asteroid_distance['far'] & self.bullet_time['L'] & self.theta_delta['Z'], self.ship_thrust['Hard Thrust']),
            #ctrl.Rule(self.asteroid_distance['far'] & self.bullet_time['L'] & (self.theta_delta['NS'] | self.theta_delta['PS']), self.ship_thrust['Soft Thrust']),
            #ctrl.Rule(self.asteroid_distance['medium'] & self.bullet_time['M'] & self.theta_delta['Z'], self.ship_thrust['Soft Thrust']),
            #ctrl.Rule(self.asteroid_distance['medium'] & self.bullet_time['M'] & (self.theta_delta['PL'] | self.theta_delta['NL']), self.ship_thrust['Soft Brake']),


        ]
        #bomb rules
        self.rules.extend([
            ctrl.Rule(self.bomb_distance['close'], self.bomb_action['drop']),
            ctrl.Rule(self.bomb_distance['medium'], self.bomb_action['no_drop']),
            ctrl.Rule(self.bomb_distance['far'], self.bomb_action['no_drop']),
        ])


        # Step 4: Create the Control System
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def bomb_rules(self):
        self.bomb_distance = ctrl.Antecedent(np.arange(0, 1001, 1), 'bomb_distance')  # Distance in to astroids
        self.bomb_action = ctrl.Consequent(np.arange(-1, 2, 1), 'bomb_action')  # Boolean (-1 to 1)

        self.bomb_distance['close'] = fuzz.zmf(self.bomb_distance.universe, 0, 150)
        self.bomb_distance['medium'] = fuzz.trimf(self.bomb_distance.universe, [100, 350, 550])
        self.bomb_distance['far'] = fuzz.smf(self.bomb_distance.universe, 500, 1000)

        self.act_bomb_distance['close'] = fuzz.zmf(self.act_bomb_distance.universe, 0, 160)
        self.act_bomb_distance['medium'] = fuzz.trimf(self.act_bomb_distance.universe, [150, 200, 250])
        self.act_bomb_distance['far'] = fuzz.smf(self.act_bomb_distance.universe, 240, 1000)

        self.bomb_action['no_drop'] = fuzz.trimf(self.bomb_action.universe, [-1, -1, 0])
        self.bomb_action['drop'] = fuzz.trimf(self.bomb_action.universe, [0, 1, 1])


    def actions(self, ship_state: Dict, game_state: Dict) -> Tuple[float, float, bool, bool]:
        ship_x, ship_y = ship_state["position"]
        ship_heading = ship_state["heading"]
        bullet_speed = 800  # Fixed bullet speed in m/s
        closest_asteroid, min_distance = None, float('inf')
        current_time = time.time()
        min_bomb_distance = 500

        for asteroid in game_state["asteroids"]:
            asteroid_x, asteroid_y = asteroid["position"]
            distance = math.sqrt((asteroid_x - ship_x) ** 2 + (asteroid_y - ship_y) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_asteroid = asteroid

        for bomb in game_state['mines']:
            bomb_x, bomb_y = bomb["position"]
            bomb_distance = math.sqrt((bomb_x - ship_x) ** 2 + (bomb_y - ship_y) ** 2)
            if bomb_distance < min_bomb_distance:
                min_bomb_distance = bomb_distance

        if closest_asteroid:
            asteroid_x, asteroid_y = closest_asteroid["position"]
            asteroid_vx, asteroid_vy = closest_asteroid["velocity"]

            dx, dy = asteroid_x - ship_x, asteroid_y - ship_y
            a = asteroid_vx ** 2 + asteroid_vy ** 2 - bullet_speed ** 2
            b = 2 * (dx * asteroid_vx + dy * asteroid_vy)
            c = dx ** 2 + dy ** 2
            discriminant = b ** 2 - 4 * a * c

            if discriminant >= 0:
                t1 = (-b + math.sqrt(discriminant)) / (2 * a)
                t2 = (-b - math.sqrt(discriminant)) / (2 * a)
                bullet_t = min(t for t in [t1, t2] if t > 0)

                intrcpt_x = asteroid_x + asteroid_vx * (bullet_t + 1 / 30)
                intrcpt_y = asteroid_y + asteroid_vy * (bullet_t + 1 / 30)
                theta1 = math.degrees(math.atan2(intrcpt_y - ship_y, intrcpt_x - ship_x))
                theta_delta = ((theta1 - ship_heading + 180) % 360) - 180

                self.simulation.input['theta_delta'] = theta_delta
                self.simulation.input['bullet_time'] = bullet_t
                self.simulation.input['asteroid_distance'] = min_distance
                self.simulation.input['bomb_distance'] = min_distance # ------------------------------bomb
                print(f"{min_distance}, {min_bomb_distance}")
                self.simulation.input['act_bomb_distance'] = min_bomb_distance
                self.simulation.compute()

                turn_rate = self.simulation.output['ship_turn']
                fire = self.simulation.output['ship_fire'] > 0.5 and abs(theta_delta) <= 10
                thrust = self.simulation.output['ship_thrust']*2
                bomb_drop = self.simulation.output['bomb_action'] > 0.5
                # check cooldown
                if bomb_drop and (current_time - self.last_bomb_time > 8):
                    self.last_bomb_time = current_time
                else: 
                    bomb_drop = False
            else:
                turn_rate, fire, thrust = 0.0, False, 0.0

                bomb_drop = False
        else:
            turn_rate, fire, thrust = 0.0, bomb_drop, 0.0
        
        self.eval_frames +=1

        return thrust, turn_rate, fire, bomb_drop

    @property
    def name(self) -> str:
        return "Group 15 Controller"
