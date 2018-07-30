import math
import numpy as np
from controllers import Controller


class UncertaintyAwareRandomController(Controller):

    def __init__(self, env, fake_uncertainty=math.inf):
        Controller.__init__(self, env)
        self.uncertainty = fake_uncertainty

    def _do_update(self, dt):
        return self.predict(dt)

    def predict(self, observation):
        return np.random.uniform(-1, 1, 2), self.uncertainty

    def learn(self, observations, actions):
        pass

    def save(self):
        print('I didn\'t learn a thing...')
