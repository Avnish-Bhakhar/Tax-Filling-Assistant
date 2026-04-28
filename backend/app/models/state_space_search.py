"""
State-Space Search Module — A* Algorithm for Tax Filing Navigation
==================================================================
Models the tax filing process as a state-space search problem where:
- States: Each step in the tax filing journey
- Actions: Transitions between steps (collecting data, computing, etc.)
- Heuristic: Estimated completion based on data completeness
- Goal: Complete, verified tax filing

This implements A* search to find the optimal path through
the tax filing process based on user's current data state.
"""

import heapq
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class FilingStep(Enum):
    """Tax filing steps represented as states."""
    START = "start"
    PERSONAL_INFO = "personal_info"
    INCOME_SALARY = "income_salary"
    INCOME_OTHER = "income_other"
    INCOME_CAPITAL_GAINS = "income_capital_gains"
    INCOME_HOUSE_PROPERTY = "income_house_property"
    HRA_CALCULATION = "hra_calculation"
    DEDUCTIONS_80C = "deductions_80c"
    DEDUCTIONS_80D = "deductions_80d"
    DEDUCTIONS_OTHER = "deductions_other"
    REGIME_SELECTION = "regime_selection"
    TAX_COMPUTATION = "tax_computation"
    TDS_VERIFICATION = "tds_verification"
    TAX_PAYMENT = "tax_payment"
    VERIFICATION = "verification"
    FILING_COMPLETE = "filing_complete"


@dataclass
class FilingState:
    """
    Represents a state in the tax filing state space.

    Attributes:
        step: Current filing step
        data_collected: Set of data fields already collected
        completeness: Percentage of data completion (0-100)
        errors: List of validation errors
    """
    step: FilingStep
    data_collected: Set[str] = field(default_factory=set)
    completeness: float = 0.0
    errors: List[str] = field(default_factory=list)

    def __hash__(self):
        return hash((self.step, frozenset(self.data_collected)))

    def __eq__(self, other):
        return self.step == other.step and self.data_collected == other.data_collected

    def __lt__(self, other):
        return self.completeness < other.completeness


@dataclass
class SearchNode:
    """Node in the A* search tree."""
    state: FilingState
    parent: Optional['SearchNode'] = None
    action: str = ""
    g_cost: float = 0.0  # Cost from start
    h_cost: float = 0.0  # Heuristic (estimated cost to goal)

    @property
    def f_cost(self) -> float:
        """Total estimated cost: f(n) = g(n) + h(n)"""
        return self.g_cost + self.h_cost

    def __lt__(self, other):
        return self.f_cost < other.f_cost


class TaxFilingStateSpace:
    """
    A* Search implementation for intelligent tax filing navigation.

    The search space models the tax filing process as a graph where:
    - Nodes are filing steps (states)
    - Edges are valid transitions with associated costs
    - The heuristic estimates remaining work based on missing data
    """

    # Data requirements for each step
    STEP_REQUIREMENTS = {
        FilingStep.PERSONAL_INFO: {
            'name', 'pan', 'dob', 'email', 'phone', 'address', 'employment_type'
        },
        FilingStep.INCOME_SALARY: {
            'basic_salary', 'hra_received', 'special_allowance', 'annual_income'
        },
        FilingStep.INCOME_OTHER: {
            'interest_income', 'rental_income', 'freelance_income'
        },
        FilingStep.INCOME_CAPITAL_GAINS: {
            'stcg', 'ltcg', 'equity_gains', 'property_gains'
        },
        FilingStep.INCOME_HOUSE_PROPERTY: {
            'property_type', 'rental_income_hp', 'municipal_tax', 'home_loan_interest'
        },
        FilingStep.HRA_CALCULATION: {
            'rent_paid', 'metro_city', 'basic_salary', 'hra_received'
        },
        FilingStep.DEDUCTIONS_80C: {
            'ppf', 'elss', 'lic', 'epf', 'nsc', 'tuition_fees', 'home_loan_principal'
        },
        FilingStep.DEDUCTIONS_80D: {
            'health_insurance_self', 'health_insurance_parents', 'preventive_checkup'
        },
        FilingStep.DEDUCTIONS_OTHER: {
            'nps_80ccd', 'education_loan_interest', 'donations_80g', 'savings_interest_80tta'
        },
        FilingStep.REGIME_SELECTION: {
            'regime_choice'
        },
        FilingStep.TAX_COMPUTATION: set(),  # Computed automatically
        FilingStep.TDS_VERIFICATION: {
            'tds_salary', 'tds_other', 'advance_tax_paid'
        },
        FilingStep.TAX_PAYMENT: {
            'tax_due_verified'
        },
        FilingStep.VERIFICATION: {
            'declaration_accepted'
        },
        FilingStep.FILING_COMPLETE: set()
    }

    # Valid transitions with costs
    TRANSITIONS = {
        FilingStep.START: [
            (FilingStep.PERSONAL_INFO, 1.0, "Collect personal information")
        ],
        FilingStep.PERSONAL_INFO: [
            (FilingStep.INCOME_SALARY, 1.0, "Enter salary income details"),
            (FilingStep.INCOME_OTHER, 1.5, "Enter other income details")
        ],
        FilingStep.INCOME_SALARY: [
            (FilingStep.HRA_CALCULATION, 0.5, "Calculate HRA exemption"),
            (FilingStep.INCOME_OTHER, 1.0, "Enter other income"),
            (FilingStep.INCOME_CAPITAL_GAINS, 1.0, "Enter capital gains"),
            (FilingStep.DEDUCTIONS_80C, 1.0, "Enter Section 80C deductions")
        ],
        FilingStep.INCOME_OTHER: [
            (FilingStep.INCOME_CAPITAL_GAINS, 1.0, "Enter capital gains"),
            (FilingStep.INCOME_HOUSE_PROPERTY, 1.0, "Enter house property income"),
            (FilingStep.DEDUCTIONS_80C, 1.0, "Enter deductions")
        ],
        FilingStep.INCOME_CAPITAL_GAINS: [
            (FilingStep.DEDUCTIONS_80C, 1.0, "Enter Section 80C deductions"),
            (FilingStep.INCOME_HOUSE_PROPERTY, 1.0, "Enter house property income")
        ],
        FilingStep.INCOME_HOUSE_PROPERTY: [
            (FilingStep.DEDUCTIONS_80C, 1.0, "Enter deductions")
        ],
        FilingStep.HRA_CALCULATION: [
            (FilingStep.INCOME_OTHER, 1.0, "Enter other income"),
            (FilingStep.DEDUCTIONS_80C, 1.0, "Enter deductions")
        ],
        FilingStep.DEDUCTIONS_80C: [
            (FilingStep.DEDUCTIONS_80D, 0.8, "Enter medical insurance details"),
            (FilingStep.DEDUCTIONS_OTHER, 0.8, "Enter other deductions"),
            (FilingStep.REGIME_SELECTION, 1.0, "Choose tax regime")
        ],
        FilingStep.DEDUCTIONS_80D: [
            (FilingStep.DEDUCTIONS_OTHER, 0.8, "Enter other deductions"),
            (FilingStep.REGIME_SELECTION, 1.0, "Choose tax regime")
        ],
        FilingStep.DEDUCTIONS_OTHER: [
            (FilingStep.REGIME_SELECTION, 1.0, "Choose tax regime")
        ],
        FilingStep.REGIME_SELECTION: [
            (FilingStep.TAX_COMPUTATION, 0.5, "Compute tax liability")
        ],
        FilingStep.TAX_COMPUTATION: [
            (FilingStep.TDS_VERIFICATION, 0.8, "Verify TDS details"),
        ],
        FilingStep.TDS_VERIFICATION: [
            (FilingStep.TAX_PAYMENT, 0.5, "Pay remaining tax"),
        ],
        FilingStep.TAX_PAYMENT: [
            (FilingStep.VERIFICATION, 0.3, "Final verification")
        ],
        FilingStep.VERIFICATION: [
            (FilingStep.FILING_COMPLETE, 0.1, "Submit ITR")
        ]
    }

    # Step descriptions for the chatbot
    STEP_DESCRIPTIONS = {
        FilingStep.START: "Welcome! Let's begin your tax filing journey.",
        FilingStep.PERSONAL_INFO: "I need your basic details: name, PAN, date of birth, and contact information.",
        FilingStep.INCOME_SALARY: "Let's record your salary income. Please share your basic salary, HRA, and other allowances.",
        FilingStep.INCOME_OTHER: "Do you have income from interest, freelancing, or other sources?",
        FilingStep.INCOME_CAPITAL_GAINS: "Have you sold any stocks, mutual funds, or property this year?",
        FilingStep.INCOME_HOUSE_PROPERTY: "Do you own any property? Let's calculate house property income.",
        FilingStep.HRA_CALCULATION: "Let me calculate your HRA exemption based on your rent and salary.",
        FilingStep.DEDUCTIONS_80C: "Time to maximize your tax savings! What investments have you made under 80C?",
        FilingStep.DEDUCTIONS_80D: "Do you have health insurance? Let's claim Section 80D deduction.",
        FilingStep.DEDUCTIONS_OTHER: "Any other deductions? NPS, education loan, or donations?",
        FilingStep.REGIME_SELECTION: "I'll now compare both tax regimes and recommend the best one for you.",
        FilingStep.TAX_COMPUTATION: "Computing your tax liability under the selected regime...",
        FilingStep.TDS_VERIFICATION: "Let's verify your TDS and advance tax payments.",
        FilingStep.TAX_PAYMENT: "Time to pay any remaining tax due.",
        FilingStep.VERIFICATION: "Please review all details before final submission.",
        FilingStep.FILING_COMPLETE: "Congratulations! Your tax filing is complete! 🎉"
    }

    def __init__(self):
        self.all_required_fields = set()
        for fields in self.STEP_REQUIREMENTS.values():
            self.all_required_fields.update(fields)

    def heuristic(self, state: FilingState) -> float:
        """
        A* Heuristic: Estimates the cost to reach the goal state.

        The heuristic considers:
        1. Number of remaining steps
        2. Data completeness (missing fields)
        3. Complexity of remaining steps

        This heuristic is admissible (never overestimates) and consistent.
        """
        step_order = list(FilingStep)
        current_idx = step_order.index(state.step)
        goal_idx = step_order.index(FilingStep.FILING_COMPLETE)

        # Remaining steps cost
        remaining_steps = max(0, goal_idx - current_idx)

        # Data completeness penalty
        total_fields = len(self.all_required_fields)
        collected = len(state.data_collected)
        missing_ratio = 1 - (collected / total_fields) if total_fields > 0 else 1

        # Error penalty
        error_penalty = len(state.errors) * 0.5

        # Combined heuristic (admissible)
        h = remaining_steps * 0.7 + missing_ratio * 3.0 + error_penalty

        return h

    def get_successors(
        self, state: FilingState, user_data: Dict
    ) -> List[Tuple[FilingState, str, float]]:
        """
        Generate successor states from current state.

        Returns list of (new_state, action_description, cost) tuples.
        """
        successors = []

        if state.step not in self.TRANSITIONS:
            return successors

        for next_step, base_cost, action_desc in self.TRANSITIONS[state.step]:
            # Calculate new data collected
            new_data = state.data_collected.copy()
            required = self.STEP_REQUIREMENTS.get(state.step, set())

            # Check which required fields are available in user_data
            for field in required:
                if field in user_data and user_data[field] is not None:
                    new_data.add(field)

            # Calculate completeness
            total = len(self.all_required_fields)
            completeness = (len(new_data) / total * 100) if total > 0 else 0

            # Adjust cost based on data availability
            missing = required - new_data
            cost_modifier = len(missing) * 0.3 if missing else -0.2

            new_state = FilingState(
                step=next_step,
                data_collected=new_data,
                completeness=completeness,
                errors=[]
            )

            total_cost = base_cost + max(0, cost_modifier)
            successors.append((new_state, action_desc, total_cost))

        return successors

    def a_star_search(
        self, user_data: Dict, current_step: FilingStep = FilingStep.START
    ) -> List[Dict]:
        """
        Perform A* search to find the optimal filing path.

        Args:
            user_data: Dictionary of currently available user data
            current_step: The step to start from

        Returns:
            List of steps (dicts) representing the optimal filing path
        """
        initial_state = FilingState(step=current_step)

        # Add already available data
        for field in self.all_required_fields:
            if field in user_data and user_data[field] is not None:
                initial_state.data_collected.add(field)

        start_node = SearchNode(
            state=initial_state,
            g_cost=0,
            h_cost=self.heuristic(initial_state)
        )

        # Priority queue (min-heap)
        open_set: List[SearchNode] = []
        heapq.heappush(open_set, start_node)

        # Closed set
        closed_set: Set[FilingState] = set()

        # Search statistics
        nodes_explored = 0
        max_nodes = 1000  # Safety limit

        while open_set and nodes_explored < max_nodes:
            current = heapq.heappop(open_set)
            nodes_explored += 1

            # Goal check
            if current.state.step == FilingStep.FILING_COMPLETE:
                return self._reconstruct_path(current, nodes_explored)

            if current.state in closed_set:
                continue
            closed_set.add(current.state)

            # Expand successors
            for new_state, action, cost in self.get_successors(current.state, user_data):
                if new_state in closed_set:
                    continue

                g_cost = current.g_cost + cost
                h_cost = self.heuristic(new_state)

                child = SearchNode(
                    state=new_state,
                    parent=current,
                    action=action,
                    g_cost=g_cost,
                    h_cost=h_cost
                )

                heapq.heappush(open_set, child)

        # No path found (shouldn't happen with valid state space)
        return [{"error": "No valid filing path found", "nodes_explored": nodes_explored}]

    def _reconstruct_path(self, goal_node: SearchNode, nodes_explored: int) -> List[Dict]:
        """Reconstruct the path from start to goal."""
        path = []
        current = goal_node

        while current is not None:
            step_info = {
                "step": current.state.step.value,
                "step_name": current.state.step.name.replace('_', ' ').title(),
                "description": self.STEP_DESCRIPTIONS.get(current.state.step, ""),
                "action": current.action,
                "completeness": round(current.state.completeness, 1),
                "g_cost": round(current.g_cost, 2),
                "h_cost": round(current.h_cost, 2),
                "f_cost": round(current.f_cost, 2),
                "required_fields": list(self.STEP_REQUIREMENTS.get(current.state.step, set())),
                "data_collected_count": len(current.state.data_collected)
            }
            path.append(step_info)
            current = current.parent

        path.reverse()

        return {
            "optimal_path": path,
            "total_steps": len(path),
            "total_cost": round(goal_node.g_cost, 2),
            "nodes_explored": nodes_explored,
            "algorithm": "A* Search",
            "heuristic": "Admissible heuristic based on remaining steps + data completeness"
        }

    def get_next_step(self, current_step: FilingStep, user_data: Dict) -> Dict:
        """Get the recommended next step using A* from current position."""
        result = self.a_star_search(user_data, current_step)

        if isinstance(result, dict) and "optimal_path" in result:
            path = result["optimal_path"]
            # Find current step in path and return the next one
            for i, step in enumerate(path):
                if step["step"] == current_step.value and i + 1 < len(path):
                    next_step = path[i + 1]
                    return {
                        "current_step": current_step.value,
                        "next_step": next_step["step"],
                        "next_step_name": next_step["step_name"],
                        "description": next_step["description"],
                        "required_fields": next_step["required_fields"],
                        "remaining_steps": len(path) - i - 1,
                        "completeness": next_step["completeness"]
                    }

        return {
            "current_step": current_step.value,
            "next_step": "filing_complete",
            "description": "All steps completed!",
            "remaining_steps": 0,
            "completeness": 100.0
        }

    def get_step_questions(self, step: FilingStep) -> List[Dict]:
        """Get the questions to ask for a specific step."""
        questions = {
            FilingStep.PERSONAL_INFO: [
                {"field": "name", "question": "What is your full name (as per PAN)?", "type": "text"},
                {"field": "pan", "question": "What is your PAN number?", "type": "text"},
                {"field": "dob", "question": "What is your date of birth?", "type": "date"},
                {"field": "email", "question": "What is your email address?", "type": "email"},
                {"field": "phone", "question": "What is your phone number?", "type": "tel"},
                {"field": "address", "question": "What is your residential address?", "type": "text"},
                {"field": "employment_type", "question": "Are you salaried or self-employed?", "type": "select", "options": ["salaried", "self_employed"]}
            ],
            FilingStep.INCOME_SALARY: [
                {"field": "basic_salary", "question": "What is your annual basic salary?", "type": "number"},
                {"field": "hra_received", "question": "How much HRA do you receive annually?", "type": "number"},
                {"field": "special_allowance", "question": "What are your other allowances?", "type": "number"},
                {"field": "annual_income", "question": "What is your total gross annual income?", "type": "number"}
            ],
            FilingStep.INCOME_OTHER: [
                {"field": "interest_income", "question": "What is your total interest income (savings, FD)?", "type": "number"},
                {"field": "rental_income", "question": "Do you have any rental income? If yes, how much?", "type": "number"},
                {"field": "freelance_income", "question": "Any freelance or side income?", "type": "number"}
            ],
            FilingStep.DEDUCTIONS_80C: [
                {"field": "ppf", "question": "How much did you invest in PPF?", "type": "number"},
                {"field": "elss", "question": "How much did you invest in ELSS mutual funds?", "type": "number"},
                {"field": "lic", "question": "What is your life insurance premium?", "type": "number"},
                {"field": "epf", "question": "What is your EPF contribution?", "type": "number"},
                {"field": "nsc", "question": "Any NSC investments?", "type": "number"},
                {"field": "tuition_fees", "question": "Children's tuition fees paid?", "type": "number"},
                {"field": "home_loan_principal", "question": "Home loan principal repayment?", "type": "number"}
            ],
            FilingStep.DEDUCTIONS_80D: [
                {"field": "health_insurance_self", "question": "Health insurance premium for self & family?", "type": "number"},
                {"field": "health_insurance_parents", "question": "Health insurance premium for parents?", "type": "number"},
                {"field": "preventive_checkup", "question": "Preventive health check-up expenses?", "type": "number"}
            ],
            FilingStep.DEDUCTIONS_OTHER: [
                {"field": "nps_80ccd", "question": "NPS contribution under 80CCD(1B)?", "type": "number"},
                {"field": "education_loan_interest", "question": "Education loan interest paid?", "type": "number"},
                {"field": "donations_80g", "question": "Donations under Section 80G?", "type": "number"},
                {"field": "savings_interest_80tta", "question": "Savings account interest (for 80TTA)?", "type": "number"}
            ]
        }

        return questions.get(step, [])


# Module-level instance
tax_search = TaxFilingStateSpace()
