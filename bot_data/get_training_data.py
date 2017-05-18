import tensorflow as tf
import numpy as np

def main():
	lines = np.loadtxt("raw_data2.csv", delimiter=',')
	
	with open("training_data2.csv", 'w') as file:
		for i, line in enumerate(lines[:-1]):
			block_sum = 0.0
			green_sum = 0.0
			remain_block = 0.0
			remain_green = 0.0
			
			print("start")
			str = ""
			# row 7, column 6
			for e in range(42):		# get block and green ball data
				if line[e] >= 0:
					block_sum += line[e]
				else:
					green_sum += line[e] * -1
				
				str += "%d,"%line[e]
				
			if green_sum == 0 or block_sum == 0:
				continue
				
			for e in range(6, 42):
				if lines[i+1][e] >= 0:
					remain_block += lines[i+1][e]
				else:
					remain_green += lines[i+1][e] * -1
			
			current_round = line[44]
			next_round = lines[i+1][44]
			
			if current_round + 1 != next_round:
				continue
			
			file.write(str)
			reward = (remain_block / block_sum * 50) + (remain_green / green_sum * 50)
			
			for e in range(42, 44):
				file.write("%d,"%line[e])
			
			file.write("%d,"%line[45])
			file.write("%d\n"%reward)
			
						
					
					
if __name__ == "__main__":
	main()