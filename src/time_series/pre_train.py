"""This script trains a model in the time series data.

tutorials: https://pytorch-forecasting.readthedocs.io/en/stable/tutorials/ar.html
"""
import argparse
from gc import callbacks
from dotenv import find_dotenv, dotenv_values
import logging
import json
import warnings

import pytorch_forecasting as ptf
import pytorch_lightning as pl
import torch

from dataset import Dataset


def read_config(args):
    """This function reads a .json file and returns the configuration as a
    Namespace.
    """
    with open(args.config_file) as f:
        config = json.load(f)
    return argparse.Namespace(**vars(args), **config)


def get_model_from_dataset(args, dataset):
    if args.model.lower() == "NBeats":
        return ptf.NBeats.from_dataset(dataset)
    else:
        return ptf.DeepAR.from_dataset(dataset)


def get_callbacks(args):
    callbacks_list = list()
    if args.tensorboard:
        callbacks_list.append(ptf.callbacks.TensorBoard())
    if args.checkpoint:
        callbacks_list.append(ptf.callbacks.Checkpoint(
            save_top_k=1,
            save_last=True,
            log_dir=args.checkpoint_dir,
        ))
    return callbacks_list

def main(args):
    warnings.filterwarnings('ignore')
    logger = logging.getLogger(__name__)
    dataset = Dataset(args)
    model = get_model_from_dataset(args, dataset)
    callbacks_list = list()
    trainer = pl.Trainer.from_argparse_args(args, callbacks=callbacks_list)

    trainer.fit(
        model,
        train_dataloaders=dataset.train_dataloader(),
        val_dataloaders=dataset.val_dataloader(),
    )

    trainer.validate(dataloaders=dataset)
    trainer.save_checkpoint(args.checkpoint_file)
    best_model = model.load_from_checkpoint(args.checkpoint_file)

    val_dataloader = dataset.val_dataloader()
    actuals = torch.cat([y[0] for x, y in iter(val_dataloader)])
    predictions = best_model.predict(val_dataloader)
    logger.info(actuals - predictions).abs().mean()

    raw_predictions, x = best_model.predict(val_dataloader, mode="raw", return_x=True)
    for idx in range(10):  # plot 10 examples
        best_model.plot_prediction(x, raw_predictions, idx=idx, add_loss_to_title=True);


if __name__ == "__main__":
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    parser = argparse.ArgumentParser()
    parser.add_argument("-conf", "--config-file", type=str, help="The configuration file path.")
    args = parser.parse_args()
    args = argparse.Namespace(**vars(read_config(args)), **dotenv_values(find_dotenv()))

    main(args)