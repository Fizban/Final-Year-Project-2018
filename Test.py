import gym
import time
from multiprocessing import Process, Pipe
import numpy as np

class EnvWorker(Process):

	def __init__(self, env_name, pipe, name=None,NotDisplay=False):
		Process.__init__(self, name=name)
		self.env = gym.make(env_name)
		self.pipe = pipe
		self.name = name
		self.Display= not NotDisplay
		print "Environment initialized. ", self.name

	def run(self):
		observation=self.env.reset()
		param=self.pipe.recv()
		episode_return=0
		while True:
			time.sleep(0.005)
			decision=np.matmul(observation,param)
			action=1 if decision>0 else 0
			observation, reward, done, _ = self.env.step(action)
			episode_return+=reward
			self.env.render(close=self.Display)
			if done:
				self.pipe.send(episode_return)
				episode_return=0
				param=self.pipe.recv()
				if param=="EXIT":
					break
				self.env.reset()

p_start, p_end = Pipe()
env_worker = EnvWorker("CartPole-v1", p_end, name="Worker",NotDisplay=True)
env_worker.start()
for i in range(5):
	p_start.send(np.random.uniform(-1,1,4))
	episode_return = p_start.recv()
	print "Reward for the episode ",i," ->", episode_return
p_start.send("EXIT")
env_worker.terminate()