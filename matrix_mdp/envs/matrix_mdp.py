__credits__ = ["Paul Festor"]

from os import path
from typing import Optional

import numpy as np

import gymnasium as gym
from gymnasium import spaces


class MatrixMDPEnv(gym.Env):
    """
    ## Description

    An flexible enfironment to have a gym API for discrete MDPs with `N_s` states and `N_a` actions given:
     - A vector of initial state distribution P_0(S)
     - A transition probability matrix P(S' | S, A)
     - A reward vector R(S)

    ## Action Space

    The action is a `ndarray` with shape `(1,)` representing the index of the action to execute.

    ## Observation Space

    The observation is a `ndarray` with shape `(1,)` representing index of the state the agent is in.

    ## Rewards

    The reward function is defined according to the reward matrix given at the creation of the environment.

    ## Starting State

    The starting state is a random state sampled from $P_0$.

    ## Episode Truncation

    The episode truncates when a terminal state is reached.
    Terminal states are inferred from the transition probability matrix as
    $\sum_{s' \in S} \sum_{s \in S} \sum_{a \in A} P(s' | s, a) = 0$

    ## Arguments

    - `p_à`: `ndarray` of shape `(n_states, )` representing the initial state probability distribution.
    - `p`: `ndarray` of shape `(n_states, n_states, n_actions)` representing the transition dynamics $P(S' | S, A)$.
    - `r`: `ndarray` of shape `(n_states, n_actions)` representing the reward matrix.

    ```python
    import gymnasium as gym
    gym.make('MatrixMDP-v0', p_0, p, r)
    ```

    ## Version History

    * v0: Initial versions release (1.0.0)

    """

    metadata = {
        "render_modes": ["human", ],
    }

    def __init__(self, p_0, p, r, render_mode: Optional[str] = None):
        self.p_0 = p_0
        self.p = p
        self.r = r

        self.action_space = spaces.Discrete(n=p.shape[2])
        self.observation_space = spaces.Discrete(n=p.shape[0])
        self.states_array = np.arange(p.shape[0])

        # Matrix checks
        if p_0.sum() != 1:
            raise ValueError("The provided initial probabilities do not sum tp 1.")
        for s in self.states_array:
            for a in np.arange(self.p.shape[2]):
                if p[:,s,a].sum() != 1:
                    raise ValueError(
                        "The provided transition probabilities are invalid: \sum_s' P(s' | s, a) not in {0, 1}" +\
                        f"for s={s} and a={a}."
                    )

        self.render_mode = render_mode

        # Terminal states are states where no actions lead anywhere
        self.terminal_states = [s for s in self.states_array if self.p[:, :, s].sum() == 0]

        # Initialize the first state
        self.state = np.random.choice(self.states_array, p=self.p_0)

    def step(self, action):

        new_state = np.random.choice(self.states_array, p=self.p[:, self.state, action])
        reward = self.r[self.state, action]
        done = (new_state in  self.terminal_states)

        if self.render_mode == "human":
            self.render()
        return self._get_obs(), reward, done, done, {}

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)

        start_state = np.random.choice(self.states_array, p=self.p_0)
        if options is not None:
            start_state = options.get("start_state") if "start_state" in options else start_state

        self.state = start_state

        if self.render_mode == "human":
            self.render()
        return self._get_obs(), {}

    def _get_obs(self):
        return np.array([self.state, ], dtype=np.int)

    def render(self):
        if self.render_mode is None:
            gym.logger.warn(
                "You are calling render method without specifying any render mode. "
                "You can specify the render_mode at initialization, "
                f'e.g. gym("{self.spec.id}", render_mode="rgb_array")'
            )
            return

        if self.render_mode == "human":
            print(f"Current state: {self.state}")

    def close(self):
        pass
