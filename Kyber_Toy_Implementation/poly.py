class Polynomial:
    def __init__(self, coefficients, q):
        self.coefficients = [c % q for c in coefficients]
        self.q = q

    def __add__(self, other):
        if self.q != other.q:
            raise ValueError("Polynomials must have the same modulus")
        max_len = max(len(self.coefficients), len(other.coefficients))
        result = [(self.coefficients[i] if i < len(self.coefficients) else 0) +
                  (other.coefficients[i] if i < len(other.coefficients) else 0)
                  for i in range(max_len)]
        return Polynomial(result, self.q)

    def __sub__(self, other):
        if self.q != other.q:
            raise ValueError("Polynomials must have the same modulus")
        max_len = max(len(self.coefficients), len(other.coefficients))
        result = [(self.coefficients[i] if i < len(self.coefficients) else 0) -
                  (other.coefficients[i] if i < len(other.coefficients) else 0)
                  for i in range(max_len)]
        return Polynomial(result, self.q)

    def __mul__(self, other):
        if self.q != other.q:
            raise ValueError("Polynomials must have the same modulus")
        result = [0] * (len(self.coefficients) + len(other.coefficients) - 1)
        for i in range(len(self.coefficients)):
            for j in range(len(other.coefficients)):
                result[i + j] += self.coefficients[i] * other.coefficients[j]
                result[i + j] %= self.q
        return Polynomial(result, self.q)

    def mulRq(self, other, n):
        if self.q != other.q:
            raise ValueError("Polynomials must have the same modulus")
        # Use the __mul__ method to multiply the polynomials
        product = self * other
        # Reduce modulo x^n + 1
        reduced_result = [0] * n
        for i in range(len(product.coefficients)):
            if i < n:
                reduced_result[i] = product.coefficients[i]
            else:
                reduced_result[i % n] -= product.coefficients[i]
            reduced_result[i % n] %= self.q
        return Polynomial(reduced_result, self.q)

    def __repr__(self):
        return "Polynomial({}, q={})".format(self.coefficients, self.q)
    
class PolynomialVector:
    def __init__(self, polynomials):
        self.polynomials = polynomials
        self.q = polynomials[0].q
        self.n = len(polynomials[0].coefficients)

    def __add__(self, other):
        if len(self.polynomials) != len(other.polynomials):
            raise ValueError("Vectors must have the same length")
        result = [self.polynomials[i] + other.polynomials[i] for i in range(len(self.polynomials))]
        return PolynomialVector(result)

    def __sub__(self, other):
        if len(self.polynomials) != len(other.polynomials):
            raise ValueError("Vectors must have the same length")
        result = [self.polynomials[i] - other.polynomials[i] for i in range(len(self.polynomials))]
        return PolynomialVector(result)

    def inner_product(self, other):
        if len(self.polynomials) != len(other.polynomials):
            raise ValueError("Vectors must have the same length")
        result = Polynomial([0] * self.n, self.q)
        for i in range(len(self.polynomials)):
            result = result + self.polynomials[i].mulRq(other.polynomials[i], self.n)
        return result

    def __repr__(self):
        return "PolynomialVector({})".format(self.polynomials)