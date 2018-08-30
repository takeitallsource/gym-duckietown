import numpy as np
from learning_iil.algorithms.dagger import DAggerLearning


class AggreVaTeLearning(DAggerLearning):

    def __init__(self, env, teacher, learner, explorer, horizon, episodes, starting_position, starting_angle, alpha=0.99):
        DAggerLearning.__init__(self, env, teacher, learner, horizon, episodes, starting_position, starting_angle, alpha)
        # self._select_breakpoint()
        self.break_point = None
        self.explorer = explorer

    def _select_breakpoint(self):
        self.break_point = np.random.randint(1, self._horizon)  # t in AggreVaTeSampling()
        print('t: {}'.format(self.break_point))

    def _do_update(self, dt):
        observation = self.env.unwrapped.render_obs()

        if self.break_point is None:
            self._select_breakpoint()
        if self._current_horizon < self.break_point:
            control_policy = self._active_policy()
        elif self._current_horizon == self.break_point:
            control_policy = self.explorer
        else:
            control_policy = self.primary

        control_action = control_policy._do_update(observation)
        self._on_expert_input(control_policy, control_action, observation)

        return control_action

    def _on_episode_done(self):
        self._select_breakpoint()
        DAggerLearning._on_episode_done(self)