import random
from typing import Tuple

class MathProblemGenerator:
    """Kelas untuk menghasilkan soal matematika acak dengan operator (+, -, *, /) dan hasil antara 0-10."""
    
    @staticmethod
    def generate_math_problem() -> Tuple[str, float]:
        """
        Menghasilkan soal matematika acak beserta jawabannya.
        
        Returns:
            Tuple[str, float]: Soal dalam bentuk string (misalnya, "2 + 3") dan jawaban dalam float.
        """
        # Memilih operator secara acak
        operators = ['+', '-', '*', '/']
        operator = random.choice(operators)
        
        # Membuat soal berdasarkan operator
        if operator == '+':
            result = random.randint(0, 10)
            num2 = random.randint(0, result)
            num1 = result - num2
        elif operator == '-':
            num1 = random.randint(0, 10)
            num2 = random.randint(0, num1)
        elif operator == '*':
            result = random.randint(0, 10)
            factors = [i for i in range(1, 11) if result % i == 0]
            num1 = random.choice(factors)
            num2 = result // num1
        else:  # Pembagian
            num2 = random.randint(1, 10)
            num1 = random.randint(0, 10) * num2
        
        # Membentuk string soal dan menghitung jawaban
        problem = f"{num1} {operator} {num2}"
        answer = eval(problem)
        return problem, float(answer)