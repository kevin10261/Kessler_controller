#  Group 15 AI Controller for Kessler Game

## Overview
Welcome to the **Group 15 AI Controller**, a Generative AI-powered fuzzy logic controller designed for the **Kessler Game**. This intelligent system autonomously navigates, avoids obstacles, fires at asteroids, and strategically deploys bombs based on real-time game dynamics.

##  Powered by Generative AI & Fuzzy Logic
This controller utilizes **Fuzzy Logic Control (FLC)** and **Generative AI techniques** to make intelligent, human-like decisions in a dynamic space environment. The AI continuously evaluates game states, optimizes decisions, and adapts its strategies in real-time.

### Key Features:
✅ **Fuzzy Logic Decision Making** - Implements a rule-based system for ship thrust, turning, firing, and bomb deployment.
✅ **Generative AI-Inspired Adaptation** - AI-driven optimization for fuzzy rules, improving performance dynamically.
✅ **Autonomous Navigation & Combat** - Reacts to asteroid distances, bullet timing, and bomb placement effectively.
✅ **Efficient Threat Analysis** - Predicts asteroid movement and determines the best time to fire and evade threats.

##  Implementation Details
The AI controller is built using **Python** and leverages the following libraries:
- `skfuzzy` - Fuzzy logic control system
- `numpy` - Numerical computations
- `math` - Trigonometric and algebraic operations
- `time` - Game state timing management

###  How It Works:
1. **Game State Processing** - The AI retrieves ship and asteroid positions, velocities, and bullet impact times.
2. **Fuzzy Logic Evaluation** - Inputs are fed into fuzzy variables (e.g., `theta_delta`, `asteroid_distance`, `bullet_time`).
3. **Rule-Based Decision Making** - AI determines ship thrust, rotation, firing status, and bomb deployment.
4. **Real-Time Adaptation** - AI continuously updates its strategy based on the evolving game state.

##  Fuzzy Logic System
The fuzzy logic controller consists of multiple **Antecedents (Inputs)** and **Consequents (Outputs):

###  Inputs (Antecedents):
- **Theta Delta**: Angle difference between the ship's heading and the asteroid interception point.
- **Asteroid Distance**: Distance to the closest asteroid.
- **Bullet Time**: Time required for a bullet to reach the asteroid.
- **Bomb Distance**: Distance of the ship to nearby bombs.

###  Outputs (Consequents):
- **Ship Turn**: Adjusts rotation (-180° to 180°).
- **Ship Thrust**: Controls acceleration and deceleration.
- **Ship Fire**: Determines when to shoot bullets.
- **Bomb Drop**: Decides when to deploy bombs strategically.

##  Sample Fuzzy Rules
- If `theta_delta` is **zero**, then **no turn** is needed.
- If `asteroid_distance` is **far** and `bomb_distance` is **far**, then apply **Hard Thrust**.
- If `asteroid_distance` is **close**, then apply **Soft Brake**.
- If `bullet_time` is **short**, then **fire** the weapon.
- If `bomb_distance` is **close**, then **drop a bomb**.

##  Why Use This AI Controller?
This AI system is designed to **mimic human intuition** in a chaotic space environment using **fuzzy logic** and **Generative AI-inspired techniques**. It is a great example of how AI can be used in **game development, robotics, and autonomous systems**.

##  Installation & Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/kessler-ai-controller.git
   cd kessler-ai-controller
   ```
2. Install dependencies:
   ```bash
   pip install numpy scikit-fuzzy
   ```
3. Run the controller inside the **Kessler Game** environment.

## 📜 License
This project is licensed under the **MIT License**.

---
 **Developed by Group 15 | AI for Intelligent Systems** 

