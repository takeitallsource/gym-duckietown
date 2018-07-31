import numpy as np
import tensorflow as tf
from learning_iil.learners.models.tf.tf_online_learner import TensorflowOnlineLearner

from .._layers import resnet_1, MixtureDensityNetwork


class MonteCarloDropoutResnetOneMixture(TensorflowOnlineLearner):
    def __init__(self):
        TensorflowOnlineLearner.__init__(self)

    def predict(self, state, horizon=1):
        mdn = TensorflowOnlineLearner.predict(self, np.repeat(state, 16, axis=0))
        # print('prediction')
        # print(mdn)
        mixtures = np.mean(mdn[0], axis=0)
        means = np.mean(mdn[1], axis=0)
        variances = np.mean(mdn[2], axis=0)
        prediction = MixtureDensityNetwork.max_central_value(mixtures=np.squeeze(mixtures),
                                                             means=np.squeeze(means),
                                                             variances=np.squeeze(variances))
        return prediction[0], np.sum(prediction[1])  # FIXME: Is this the best way to add the variances?

    def architecture(self):
        model = tf.map_fn(lambda frame: tf.image.per_image_standardization(frame), self.state_tensor)
        model = resnet_1(model, keep_prob=1.0)
        # TRY: tanh + 64 or change to (relu, crelu), without dense
        # model = tf.layers.dense(model, units=512, activation=tf.nn.relu,
        #                         kernel_initializer=tf.contrib.layers.xavier_initializer(uniform=False),
        #                         bias_initializer=tf.contrib.layers.xavier_initializer(uniform=False),
        #                         kernel_regularizer=tf.contrib.layers.l2_regularizer(scale=0.01))
        # model = tf.layers.dense(model, units=100, activation=tf.nn.relu,
        #                         kernel_initializer=tf.contrib.layers.xavier_initializer(uniform=False),
        #                         bias_initializer=tf.contrib.layers.xavier_initializer(uniform=False),
        #                         kernel_regularizer=tf.contrib.layers.l2_regularizer(scale=0.01))
        model = tf.layers.dense(model, units=64, activation=tf.nn.relu,
                                kernel_initializer=tf.contrib.layers.xavier_initializer(uniform=False),
                                bias_initializer=tf.contrib.layers.xavier_initializer(uniform=False),
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(scale=0.01))

        loss, components, _ = MixtureDensityNetwork.create(model, self.action_tensor, number_mixtures=3)
        return components, loss

    def get_optimizer(self, loss):
        return tf.train.AdagradOptimizer(1e-3).minimize(loss, global_step=self.global_step)

