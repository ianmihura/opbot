import sqlite3
import pytorch_lightning as pl
from src.models.models import get_model
from torch import Tensor

from torch.utils.data import DataLoader
from environment import DeribitDataset
from environment import DeribitEnv


def make_loss_function(gamma, **kwargs):
    def loss_Q_learning(rewards: Tensor, Qt: Tensor, Q: Tensor) -> Tensor:
        """This function computes the Q-learning loss of one batch of episodes."""
        # L = (r + gamma * Qt(s', a') - Q(s, a))**2
        loss = (rewards + gamma * Qt - Q).square().sum().item()
    return loss_Q_learning


def find_extremes(cursor):
    """This function returns the first and last date in the database."""
    time_query = """SELECT MIN(TIMESTAMP), MAX(TIMESTAMP)
                    FROM VARIABLE_DATA;"""
    response = cursor.execute(time_query).fetchall()
    return min(response), max(response)


class PorfolioAgnosticAgent(pl.LightningModule):
    """This class implements a porfolio agnostic agent"""
    def __init__(self, **kwargs):
        super().__init__()
        self.save_hyperparameters()  # this saves all arguments from kwargs in self.hparams
        self.model = get_model(self.hparams.model_name)
        self.target_model = get_model(self.hparams.model_name)
        self.criterion = make_loss_function(self.hparams.gamma)
        self.env = DeribitEnv()

    def forward(self, state):
        return self.model(state)

    def train_step(self, batch, batch_idx):
        state_seq = self.env.reset(batch)
        action_seq = self.model(state_seq)
        t_action_seq = self.target_model(state_seq)

        reward_seq = self.env.get_reward_sequence(action_seq)
        # compute the loss and the gains of the model
        loss = self.criterion(reward_seq, action_seq, t_action_seq)
        gains = self.env.get_gains(action_seq)

        self.log("train_loss", loss, on_epoch=True)
        self.log("train_gains", gains, on_epoch=True)

        return loss

    def val_step(self, batch, batch_idx):
        state_seq = self.env.reset(batch)
        action_seq = self.model(state_seq)
        t_action_seq = self.target_model(state_seq)

        reward_seq = self.env.get_reward_sequence(action_seq)
        # compute the loss and the gains of the model
        loss = self.criterion(reward_seq, action_seq, t_action_seq)
        gains = self.env.get_gains(action_seq)

        self.log("val_loss", loss, on_epoch=True)
        self.log("val_gains", gains, on_epoch=True)

        return loss

    def test_step(self, batch, batch_idx):
        state_seq = self.env.reset(batch)
        action_seq = self.model(state_seq)

        gains = self.env.get_gains(action_seq)

        self.log("test_gains", gains, on_epoch=True)

        return 0

    def configure_optimizers(self):
        return [self.optimizer]


class DataModule(pl.LightningDataModule):
    def __init__(self, file, interval_length=1, proportions = (0.8, 0.1, 0.1), **kwargs):
        super().__init__()
        assert(sum(proportions) == 1, "The proportions must sum to 1")
        # define the starts and ends of the partitions
        with sqlite3.connect8(file) as conn:
            cursor = conn.cursor()
            self.start_train, self.end_abs = find_extremes(cursor)
            duration = int(self.end_abs - self.start_train)
            self.start_val = self.start_train + duration * proportions[0]
            self.start_test = self.start_val + duration * proportions[1]

        self.batch_size = 

    def train_dataloader(self):
        dataset = DeribitDataset(self.file, self.interval_length,
            self.future_distance, start=self.start_train, end=self.start_val)
        return DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self):
        dataset = DeribitDataset(self.file, self.interval_length,
            self.future_distance, start=self.start_val, end=self.start_test)
        return DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

    def test_dataloader(self):
        dataset = DeribitDataset(self.file, self.interval_length,
            self.future_distance, start=self.start_test, end=self.end_abs)
        return DataLoader(dataset, batch_size=self.batch_size, shuffle=True)