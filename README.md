# Symbolic ODE Solver

## Overview
This project is a Python-based computational utility designed for solving 1st and 2nd-order Ordinary Differential Equations (ODEs) that possess known analytical solution methods. 

*The program performs the following steps:*

1. Reads the user input- 
- The equation and initial conditions are entered by the user as strings.
2. Classifies the differential equation- 
- The program identifies the type of equation.
- Displays the equation classification
- The detected type of equation is shown to the user.
3. Solves the equation analytically-
- The program first finds the general solution without using the initial conditions.
- The program then applies the initial conditions
- The constants in the general solution are calculated using the given initial conditions.
- The program displays the particular solution
- The final solution that satisfies the initial conditions is shown to the user.
4. Finds the domain of the solution- 
- The program determines the maximal interval where the solution is defined and valid.
5. Plots the solution
- The solution function is plotted over its valid domain.
6. Verifies the solution
- The program substitutes the solution back into the original differential equation to confirm that it satisfies the equation.

---

## Supported Equation Types & Solution Strategies
The framework is engineered to identify and execute closed-form solution paths for the following mathematical classifications:

*   **1st-Order Separable Equations:** $N(y) \frac{dy}{dx} = M(x) \implies \int N(y) dy = \int M(x) dx + C$
*   **1st-Order Linear Equations:** $\frac{dy}{dx} + P(x)y = Q(x)$, systematically normalized and resolved via an Integrating Factor: $\mu(x) = e^{\int P(x)dx}$.
*   **1st-Order Exact Equations:** $M(x,y)dx + N(x,y)dy = 0$ where $\frac{\partial M}{\partial y} = \frac{\partial N}{\partial x}$, solved via potential function evaluation.
*   **1st-Order Bernoulli Equations:** $\frac{dy}{dx} + P(x)y = Q(x)y^n$, linearized using the non-linear substitution $u = y^{1-n}$.
*   **2nd-Order Linear Constant-Coefficient Equations:** $a \frac{d^2y}{dx^2} + b \frac{dy}{dx} + cy = g(x)$, evaluated via characteristic equations and the method of undetermined coefficients or variation of parameters.

---

## Input & Output Specifications

### Input Format
The user interfaces with the program by providing the differential equation and the initial value conditions (IVPs) in a simple, structured string format via the command line.

### Expected Output
*   **Mathematical Classification:** Terminal text identifying the taxonomy of the equation.
*   **Symbolic Solutions:** Clear printouts of both the *General Solution* (with constants $C_1, C_2$) and the *Particular Solution* (evaluated for the IVP).
*   **Maximal Domain of Existence:** The continuous interval $(a, b)$ wrapping around $x_0$ where the solution holds true.
*   **Verification Status:** A strict boolean verification report confirming that back-substitution yields an exact identity (`TRUE`).
*   **Visual Trajectory:** A 2D rendering of the solution curve, strictly bounded within its valid domain.

## Example
*Input:*

Equation: "y' + 2*x*y = x"
Initial Condition: "y(0) = 1"

*Output may include:*

Equation type: First-order linear differential equation

General solution:
y(x) = C1*exp(-x**2) + 1/2

Particular solution:
y(x) = 1/2 + 1/2*exp(-x**2)

Domain:
(-∞, ∞)

Verification:
The solution satisfies the differential equation.

A graph of the solution is then displayed.

---

## Project Structure
```text
ODE_Solver_Project/
│
├── main.py
├── parser.py
├── classifier.py
├── solver.py
├── verifier.py
├── plotter.py
├── utils.py
├── requirements.txt
└── README.md
```
---

## Technologies Used

The project is written in Python and uses the following libraries:

sympy — symbolic mathematics and analytical solving
numpy — numerical calculations
matplotlib — plotting graphs
re — parsing user input strings

--- 

## How to Run the Program
1. Install Python

Make sure Python is installed.

2. Install Required Libraries

Install the required packages using:

pip install -r requirements.txt

Or manually:

pip install sympy numpy matplotlib
3. Run the Program

Run the main Python file:

python main.py
4. Enter the Equation

Example:

Enter equation:
y' + 2*x*y = x

Enter initial condition:
y(0) = 1

---

## Limitations
The program is designed to solve only ODEs that belong to the supported categories.
It may not solve equations that require numerical methods or more advanced analytical techniques.

Unsupported cases may include:

1. Nonlinear second-order equations
2. Systems of differential equations
3. Partial differential equations
4. Equations without a closed-form analytical solution
5. Equations with singularities that are difficult to detect automatically
6. and more...

---

## Author
This project was created as part of a Python programming course final project at the Weizmann Institute of Science.

*Link to the course:* https://github.com/Code-Maven/wis-python-course-2026-03/