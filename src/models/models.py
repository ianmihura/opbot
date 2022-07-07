"""The library with the models adapted to our application."""

from re import M
from transformers import BertModel
import torch
import torch.nn as nn


class BERT(nn.Module):
    def __init__(self, input_size, output_size):
        super(BERT, self).__init__()
        model = BertModel.from_pretrained("prajjwal1/bert-tiny")
        self.fc1 = nn.Linear(input_size, 128)
        self.encoder = model.encoder
        self.pooler = nn.Sequential(
            nn.Linear(in_features=128, out_features=output_size),
            nn.Tanh()
        )

    def forward(self, input):
        o = self.fc1(input)  # (batch_size, sequence_length, input_size)
        o = self.encoder(o)  # (batch_size, sequence_length, 128)
        # We "pool" the model by simply taking the hidden state corresponding
        # to the first token.
        o = self.pooler(o[:, 0])
        return o  # (batch_size, output_size)


class TradeRNN(nn.Module):
    def __init__(self, input_size, output_size):
        super(TradeRNN, self).__init__()
        self.rnn = nn.RNN(input_size=input_size, hidden_size=128, num_layers=1, batch_first=True)
        self.fc = nn.Sequential(
            nn.Linear(128, 6),
            nn.Tanh()
        )

    def forward(self, input):
        o, h = self.rnn(input)
        o = self.fc(o)
        return o


def get_model(model_name, input_size, output_size):
    """This function returns the model according to the name passed,
    paramatrized by input and output size.
    """
    if model_name.lower() == "bert":
        return BERT(input_size, output_size)
    else:
        return TradeRNN(input_size, output_size)
