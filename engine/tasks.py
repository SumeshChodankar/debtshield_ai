from .models import Observation

class DebtGrader:
    @staticmethod
    def grade_easy(final: Observation, initial: Observation) -> float:
        """Success = Late fee waived."""
        return 1.0 if final.current_fee == 0 else 0.0

    @staticmethod
    def grade_medium(final: Observation, initial: Observation) -> float:
        """Success = APR reduced below 20%."""
        return 1.0 if final.current_apr < 20.0 else max(0.0, (initial.current_apr - final.current_apr) / 10.0)

    @staticmethod
    def grade_hard(final: Observation, initial: Observation) -> float:
        """Success = APR < 15% AND Fees = 0."""
        score = 0.0
        if final.current_apr < 15.0: score += 0.5
        if final.current_fee == 0: score += 0.5
        return score