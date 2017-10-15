def average(numbers):
   return float(sum(numbers) / max(float(len(numbers)), 1.0))
   
nums = [69, 70, 71, 72]

print average(nums)
