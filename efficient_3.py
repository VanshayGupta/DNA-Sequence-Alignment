from resource import *
import time
import psutil
import sys

file = sys.argv[1]

#read from input file
def reading_inputs(file):
  with open(file) as f:
    data = f.readlines()
  data = [x.strip('\n') for x in data]
  s1, s2 = filter(lambda x: (x.isalpha() == True), data)
  l1 = [int(x) for x in data[1:data.index(s2)]]
  l2 = [int(x) for x in data[data.index(s2)+1:]]
  return s1, s2, l1, l2

#string generator function
def string_generate(s1,positions):
  for i in positions:
    temp=s1
    s1 = s1[:i+1]+temp+s1[i+1:]
  return s1

#penalty for character mismatch
mismatch_penalty = [[0, 110, 48, 94], [110, 0, 118, 48], [48, 118, 0, 110], [94, 48, 110, 0]]

#penalty for introducing a gap character
gap_penalty = 30

#mapping characters to matrix
matrix_dictionary = {"A":0, "C":1,  "G":2, "T":3}

def process_memory():
  process = psutil.Process()
  memory_info = process.memory_info()
  memory_consumed = int(memory_info.rss/1024)
  return memory_consumed

def calculate_cost(x, y, mismatch_penalty, gap_penalty, matrix_dictionary):
  
  #calculating string lengths
  m = len(x)
  n = len(y)
  #defining cost array for all possible paths
  cost_array = [[0 for i in range(n+1)] for j in range(m+1)]
  
  for i in range(m+1):
    cost_array[i][0] = i*gap_penalty
  for i in range(n+1):
    cost_array[0][i] = i*gap_penalty
  
  #filling in the cost array using dynamic programming
  for i in range(1, m+1):
    for j in range(1, n+1):
      #checking if the current elements of both strings match
      if (x[i-1] == y[j-1]):
        cost_array[i][j] = cost_array[i-1][j-1]
      else:
        cost_array[i][j] = min(cost_array[i-1][j-1] + mismatch_penalty[matrix_dictionary[x[i-1]]][matrix_dictionary[y[j-1]]], cost_array[i-1][j] + gap_penalty, cost_array[i][j-1] + gap_penalty)
  
  #calculating total cost of aligning the two strings
  alignment_cost = cost_array[m][n]
  return cost_array, alignment_cost

def compute_alignment(cost_array, x, y):
  
  #calculating string lengths
  m = len(x)
  n = len(y)
  
  #defining aligned output strings
  x_aligned = ""
  y_aligned = ""

  #computing aligned sequence using backtracking
  while (m>0 or n>0):
    if (m>0 and n>0 and cost_array[m][n] == cost_array[m-1][n-1] + mismatch_penalty[matrix_dictionary[x[m-1]]][matrix_dictionary[y[n-1]]]):
      x_aligned= x[m-1] + x_aligned
      y_aligned = y[n-1] + y_aligned
      m = m-1
      n = n-1

    elif (m > 0 and cost_array[m][n] == cost_array[m-1][n] + gap_penalty):
      x_aligned= x[m-1] + x_aligned
      y_aligned = "_" + y_aligned
      m = m-1
    
    else:
      x_aligned = "_" + x_aligned
      y_aligned = y[n-1] + y_aligned
      n = n-1

  return x_aligned, y_aligned

def basic_algorithm(x, y, mismatch_penalty, gap_penalty, matrix_dictionary):

  cost_array, alignment_cost = calculate_cost(x, y, mismatch_penalty, gap_penalty, matrix_dictionary)

  x_aligned, y_aligned = compute_alignment(cost_array, x, y)

  return alignment_cost, x_aligned, y_aligned

def efficient_algorithm(x, y, mismatch_penalty, gap_penalty, matrix_dictionary):
    
    #calculating string lengths
    m = len(x)
    n = len(y)

    #defining aligned output strings
    x_aligned = ""
    y_aligned = ""

    #checking if the first string has no characters
    if (m == 0):
        for i in range(n):
            x_aligned = x_aligned + '_'
            y_aligned = y_aligned + y[i]

    #checking if the second string has no characters
    elif (n == 0):
        for i in range(m):
            x_aligned = x_aligned + x[i]
            y_aligned = y_aligned + '_'

    #checking if either string has a single character, in this case we use the basic algorithm to compute alignment
    elif (m == 1 or n == 1):
        alignment_cost, s1, s2 = basic_algorithm(x, y, mismatch_penalty, gap_penalty, matrix_dictionary)
        x_aligned = s1
        y_aligned = s2
     
    else:
        mid_x = round(m/2)
        
        #calculating the alignment cost for the first half of string 1 and string 2
        left_score = calculate_cost(x[:mid_x], y, mismatch_penalty, gap_penalty, matrix_dictionary)[0][-1]
        
        #calculating the alignment cost for the second half of string 1 and string 2
        right_score = calculate_cost(x[mid_x:][::-1], y[::-1], mismatch_penalty, gap_penalty, matrix_dictionary)[0][-1][::-1]

        temp = [i+j for (i,j) in zip(left_score, right_score)]
        mid_y = temp.index(min(temp))

        #divide and conquer to get the optimal alignment sequence
        x_aligned = x_aligned + efficient_algorithm(x[:mid_x], y[:mid_y], mismatch_penalty, gap_penalty, matrix_dictionary)[1] + efficient_algorithm(x[mid_x:], y[mid_y:], mismatch_penalty, gap_penalty, matrix_dictionary)[1]
        y_aligned = y_aligned + efficient_algorithm(x[:mid_x], y[:mid_y], mismatch_penalty, gap_penalty, matrix_dictionary)[2] + efficient_algorithm(x[mid_x:], y[mid_y:], mismatch_penalty, gap_penalty, matrix_dictionary)[2]

    #calculating alignment cost
    alignment_cost = 0
    for i in range(len(x_aligned)):
        if x_aligned[i] == '_' or y_aligned[i] == '_':
            alignment_cost = alignment_cost + gap_penalty
        else:
            alignment_cost = alignment_cost + mismatch_penalty[matrix_dictionary[x_aligned[i]]][matrix_dictionary[y_aligned[i]]]

    return alignment_cost, x_aligned, y_aligned

#Efficient Algorithm Execution
s1, s2, l1, l2 = reading_inputs(file)
gene1 = string_generate(s1, l1)
gene2 = string_generate(s2, l2)
start_time = time.time()
alignment_cost, x_aligned, y_aligned = efficient_algorithm(gene1, gene2, mismatch_penalty, gap_penalty, matrix_dictionary)
end_time = time.time()
memory = process_memory()
time_taken = (end_time - start_time)*1000

output_file = sys.argv[2]

content = [alignment_cost, x_aligned, y_aligned, time_taken, memory]

#writing to output file
output = open(output_file, "w")
for i in content:
    output.write(str(i) + "\n")
output.close()
