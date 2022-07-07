import torch
import torch.nn
import torch.nn.functional as F
from torch.utils.data import Dataset
from torch import Tensor
import sqlite3
import gym


def find_extremes(file):
    """This function returns the first and last date in the database."""
    time_query = """SELECT TIMESTAMP
                    FROM CONTRACTS_DATA;"""
    with sqlite3.connect(file) as conn:
        cursor = conn.cursor()
        response = cursor.execute(time_query)
        return min(response), max(response)


class DeribitDataset(Dataset):
    def __init__(self, file, interval_length, future_distance, start=None, end=None):
        self.connection = sqlite3.connect(file)
        self.cursor = self.connection.cursor()
        self.interval_length = interval_length
        self.future_distance
        # get the first and last timestamp

        # separate the intervals evenly and generate a dictionary with pairs:
        # self.samples = {idx: (t0, t1)} or a list
        if start is None or end is None:
            self.start, self.end = find_extremes(self.cursor)
        else:
            self.start = start
            self.end = end
        self.samples = self.generate_samples_dict()
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        t0, t1 = self.samples[idx]
        response_iterator = self.query(t0, t1)  # TODO: decide if we need to cache this
        # convert the data in the iterator to a tensor
        state_data = torch.Tensor(response_iterator.fetchall())
        return state_data, all_data

    def query(self, t0, t1):
        """This function generates an iterator object with data to build the 
        state tath the model will see between t0 and t1.
        """
        # TODO: check the query is ok and check whether the newlines are ok
        query_text =  f"SELECT \
                            PRICE, DELTA, VEGA, THETA, GAMMA, IV, \
                            P_C, EXPIRATION, STRIKE, \
                            OPEN, CLOSE, HIGH, LOW, VOLUME, VOLATILITY \
                        FROM \
                            VARIABLE_DATA NATURAL \
                            LEFT JOIN CONTRACTS_METADATA \
                            LEFT JOIN UNDERLYING ON TIMESTAMP \
                        WHERE \
                            TIMESTAMP BETWEEN {t0} AND {t1} \
                            AND PRICE * 0.5 < STRIKE AND STRIKE < PRICE * 1.5 \
                            AND TIMESTAMP < EXPIRATION \
                            AND TIMESTAMP - EXPIRATION < {self.future_distance} \
                        SORT BY TIMESTAMP, STRIKE, EXIPRATION DESC;"
        return self.cursor.execute(query_text)

    def generate_samples_dict(self) -> dict:
        i = 0
        current_start = self.start
        samples = dict()
        while current_start < self.end:
            samples[i] = (current_start, current_start + self.interval_length)
            current_start = current_start + self.interval_length
            i += 1
        return samples

class DeribitEnv(gym.Env):
    """gym.Env class to manage the execution of actions. This inplementation
    works with porfolio agnostic models.
    TODO: implement batches
    """
    def __init__(self, args):
        super().__init__()
        self.action_space = gym.spaces.Discrete(6,)  # TODO: decide how the action space will be
        self.porfolio = torch.zeros(args.batch_size, 1)
        self.batch_size = args.batch_size
        self.reward_delay = args.reward_delay

    def reset(self, data):
        """This function resets the state of the environment to the initial
        point in the data passed.
        """
        self.current_episode_data = data
        self.timestep = 0
        self.porfolio = torch.zeros(self.batch_size, self.porfolio_size)
        state = self.current_episode_data
        return state
    
    def render(self):
        pass
    
    def close(self):
        pass

    def step(self, action):
        self.process_action(action)  # update the porfolio
        reward = self.get_reward(self.timestep)
        self.timestep += 1

        done = self.timestep == len(self.current_episode_data)
        return None, reward, done, []  # next_state: None, reward, done: bool, info
    
    def get_reward(self) -> float:
        # very dummy function working as example
        return self.porfolio.sum().item()
    
    def get_reward_sequence(self, sequence_of_actions) -> Tensor:
        """This function returns the reward for a sequence of actions.
        Notes:
        current_episode_data -> (batch, time, contracts, features)
        sequence_of_actions: -> (batch, time, contracts)
        """
        time_crop_actions = sequence_of_actions[:, :-self.reward_delay]  # working with batch_first
        time_crop_data = self.current_episode_data[:, self.reward_delay:]

        porfolio = torch.mul(self.current_episode_data, sequence_of_actions.unsqueeze(-1))
        oracle = torch.mul(time_crop_data, time_crop_actions.unsqueeze(-1))

        feature_dim = 0
        return (oracle[:, :, :, feature_dim] - porfolio[:, :, :, feature_dim]).sum(dim=-1)  # shape (batch, time)
    
    def get_gains(self) -> float:
        pass

    def process_action(self, action):
        # dummy example but it would be great to make it as simple and tensory
        # as possible
        self.porfolio += action * self.current_episode_data[self.timestep]
