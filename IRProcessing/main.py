import estimation
import analysis
import thread
from Queue import Queue


q_s1 = Queue()
q_s2 = Queue()
q_s3 = Queue()
q_s4 = Queue()

def main():
   thread.start_new_thread(estimation.estimator, (q_s1, q_s2, q_s3, q_s4))
   thread.start_new_thread(analysis.analyze, (q_s1, 1))
   thread.start_new_thread(analysis.analyze, (q_s2, 2))
   thread.start_new_thread(analysis.analyze, (q_s3, 3))
   thread.start_new_thread(analysis.analyze, (q_s4, 4))
    
if __name__ == "__main__":
    main() 