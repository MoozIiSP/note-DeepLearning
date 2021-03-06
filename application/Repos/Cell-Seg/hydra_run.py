import os
import shutil
import hydra
import pytorch_lightning as pl
from omegaconf import DictConfig, OmegaConf
from pytorch_lightning.loggers import CometLogger, TensorBoardLogger

from src.lightning_classes.lightning_bdci import LitBCDI
from src.utils.utils import set_seed, save_useful_info
import torch

def run(cfg: DictConfig):
    """
    Run pytorch-lightning model

    Args:
        cfg: hydra config

    Returns:

    """
    set_seed(cfg.training.seed)

    model = LitBCDI(hparams=cfg)

    early_stopping = pl.callbacks.EarlyStopping(**cfg.callbacks.early_stopping.params)
    model_checkpoint = pl.callbacks.ModelCheckpoint(**cfg.callbacks.model_checkpoint.params)

    tb_logger = TensorBoardLogger(save_dir=cfg.general.save_dir)
    comet_logger = CometLogger(save_dir=cfg.general.save_dir,
                               workspace=cfg.general.workspace,
                               project_name=cfg.general.project_name,
                               # api_key=cfg.private.comet_api,
                               experiment_name=os.getcwd().split('\\')[-1])

    print(cfg.trainer)
    trainer = pl.Trainer(logger=[tb_logger, comet_logger],
                         # early_stop_callback=early_stopping,
                         checkpoint_callback=model_checkpoint,
                         # nb_sanity_val_steps=0,
                         gradient_clip_val=0.5,
                         **cfg.trainer)
    trainer.fit(model)

    # save as a simple torch model
    model_name = "{os.getcwd().split('\\')[-1]}.pth"
    torch.save(model.model.state_dict(), model_name)


@hydra.main(config_path="conf", config_name="config")
def run_model(cfg: DictConfig) -> None:
    print(OmegaConf.to_yaml(cfg))
    save_useful_info()
    run(cfg)


if __name__ == "__main__":
    run_model()
