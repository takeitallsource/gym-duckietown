import argparse
import math
import pyglet
import gym
from gym_duckietown.envs import SimpleSimEnv
from gym_duckietown.wrappers import HeadingWrapper
from controllers import JoystickController

from learning_iil.algorithms import DAggerLearning, AggreVaTeLearning, SupervisedLearning, UPMSLearning
from learning_iil.learners import UARandomExploration, NeuralNetworkPolicy
from learning_iil.learners.parametrizations.tf.baselines import ResnetOneRegression, ResnetOneMixture
from learning_iil.learners.parametrizations.tf.uncertainty import FortifiedResnetOneRegression
from learning_iil.teachers import UncertaintyAwareHumanController


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env-name', default='SimpleSim-v0')
    parser.add_argument('--map-name', default='udem1')
    parser.add_argument('--controller', default='joystick')
    parser.add_argument('--controller_mapping', default='demos/shared.joystick.logitech.yaml')
    return parser.parse_args()


def create_environment(args, with_heading=True):
    if args.env_name == 'SimpleSim-v0':
        environment = SimpleSimEnv(
            max_steps=math.inf,
            domain_rand=False,
            draw_curve=False
        )
    else:
        environment = gym.make(args.env_name)
    if with_heading:
        environment = HeadingWrapper(environment)

    return environment


def create_learning_algorithm(environment, arguments):
    # human controller
    joystick_controller = UncertaintyAwareHumanController(environment)
    joystick_controller.load_mapping(arguments.controller_mapping)

    # learner
    random_controller = UARandomExploration(environment)

    tf_model = FortifiedResnetOneRegression()
    tf_learner = NeuralNetworkPolicy(env=None,
                                     parametrization=tf_model,
                                     storage_location=base_directory)
    iil_algorithm = UPMSLearning(env=environment,
                                       teacher=joystick_controller,
                                       learner=random_controller,
                                        explorer=random_controller,
                                       horizon=512,
                                       episodes=10,
                                       starting_position=(1.5, 0.0, 3.5),
                                       starting_angle=0.0)

    return iil_algorithm


if __name__ == '__main__':
    args = parse_args()

    env = create_environment(args)
    env.reset()
    env.render()

    dagger_controller = create_learning_algorithm(environment=env, arguments=args)
    dagger_controller.configure()
    dagger_controller.open()
    dagger_controller.reset()

    pyglet.app.run()

    dagger_controller.close()
    env.close()