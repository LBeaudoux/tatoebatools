from .tatoeba import Tatoeba

# Tatoeba is imported so that other things can import
# them from here. Suppress the flake8 warning.
Tatoeba = Tatoeba
