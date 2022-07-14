import pytorch_forecasting as ptf
import pytorch_lightning as pl
import sqlite3
import pandas as pd

class Dataset(pl.LightningDataModule):
    def __init__(self, args):
        self.args = args
        self.query = """SELECT
                            ID, UNDERLYING_ID,
                            TIMESTAMP,
                            OPEN, HIGH, LOW, CLOSE,
                            VOLUME, CHAIN_TX, CHAIN_VOLUME,
                            RECENT_PRICE, RECENT_VOLUME, RECENT_TX,
                            VOLATILITY
                        FROM
                            UNDERLYING_DATA;"""

        self.con = sqlite3.connect(args.DATA_WAREHOUSE_FILE)
        self.dataframe = pd.read_sql_query(self.query, self.con)
        self.dataframe.columns = list(map(lambda x: x.lower(), self.dataframe.columns))
        self.dataframe["time_idx"] = self.make_idx(self.dataframe["timestamp"])

        self.train_size = int(len(self.dataframe) * args.train_size)

        self.back_window = args.back_window
        self.train_forward_window = args.train_forward_window
        self.val_forward_window = args.val_forward_window

    def train_dataloader(self):
        train_dataset = ptf.TimeSeriesDataSet(
            self.dataframe[self.dataframe["time_idx"] < self.train_size],
            time_idx="time_idx",
            target="close",
            max_encoder_length=self.back_window,
            max_prediction_length=self.train_forward_window,
            time_varying_unknown_reals=["open", "high", "low", "close",
                "volume", "chain_tx", "chain_volume", "recent_price",
                "recent_volume", "recent_tx", "volatility"],
        )
        return train_dataset.to_dataloader(batch_size=self.args.batch_size, shuffle=True)

    def val_dataloader(self):
        val_dataset = ptf.TimeSeriesDataSet(
            self.dataframe,
            time_idx="time_idx",
            target="close",
            max_encoder_length=self.back_window,
            max_prediction_length=self.val_forward_window,
            time_varying_unknown_reals=["open", "high", "low", "close",
                "volume", "chain_tx", "chain_volume", "recent_price",
                "recent_volume", "recent_tx", "volatility"],
        )
        return val_dataset.to_dataloader(batch_size=self.args.batch_size, shuffle=False)

    def make_idx(self, timestamps):
        """This function converts a list of arbitrary timestamps to a sorted
        list of indices, with increment 1, starting from 0.
        """
        return pd.DatetimeIndex(timestamps).sort_values().index.values

    def sample_dataset(self) -> ptf.TimeSeriesDataSet:
        """This function returns a TimeSeriesDataSet with all the data in the
        dataset. This should be used to define models.
        """
        return ptf.TimeSeriesDataSet(
            self.dataframe,
            time_idx="time_idx",
            target="close",
            max_encoder_length=self.back_window,
            max_prediction_length=self.train_forward_window,
            time_varying_unknown_reals=["open", "high", "low", "close",
                "volume", "chain_tx", "chain_volume", "recent_price",
                "recent_volume", "recent_tx", "volatility"],
        )