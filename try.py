import random


def solve_problems(sam_problems, kelly_problems, days):
  for day in range(days):
    # Simulate Sam solving problems
    sam_problems += random.randint(1, 5)

    # Simulate Kelly solving problems (slightly faster)
    kelly_problems += random.randint(2, 6)

    # Check if Kelly has overtaken Sam
    if kelly_problems > sam_problems:
      return day + 1

  # If Kelly couldn't catch up within the allotted days, return -1
  return -1

# Set initial and maximum days
sam_problems = 3
kelly_problems = 5
days = 5

# Run the simulation and print the result
days_to_overtake = solve_problems(sam_problems, kelly_problems, days)
if days_to_overtake == -1:
  print("Kelly couldn't overtake Sam within", days, "days.")
else:
  print("Kelly overtook Sam on day", days_to_overtake)
