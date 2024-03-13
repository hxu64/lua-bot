import random
import math

def generate_expression(N):
  out = "x_x"
  odds = [False, False, False, False, False, False, False, True]
  odds.extend([True]*N)
  for i in range(N):
    for j in range(len(out)):
      if random.choice(odds) and out[j] == "x":
        # print(out)
        out = out[:j] + "(x_x)" + out[j+1:]
          
  exp  = ""
  for i in range(len(out)):
    if out[i] == "x":
      exp += random.choice(["True", "False"])
    elif out[i] == "_":
      exp += random.choice([" and ", " or "])
    else:
      exp += out[i]
  return (exp, eval(exp))

def generate_list(N):
  m = random.randint(1, N+1)
  lst = str(m)
  for i in range(N//2):
    k = random.randint(1, N+1)
    if k < m:
      m = k
    lst += " " + str(k)
  return (f"`{lst}`", m)
  
def generate_items(N):
  mp = {}
  for i in range(N):
    k = random.randint(1, N)
    mp[k] = math.floor(k * random.uniform(1, 2.5))
  # for key, value in mp.items():
  #   print(f"`{key}`: {value}")
  return (mp, math.floor(N*1.5))