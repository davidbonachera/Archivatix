import hydra

from omegaconf import DictConfig
from ftplib import FTP


@hydra.main(config_path="config.yaml")
class Archivatix:
    """
    An Archivatix class.

    It will parse each FTP config given in config.yaml and apply archiving rules
    for each of them.
    """

    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = cfg
        for credentials in cfg.ftp:
            for credential in credentials.items():
                ftp = FTPConnection(credential[1]["host"], credential[1]["username"], credential[1]["password"])
                ftp.connect()
                ftp.dir()
                ftp.close()


class FTPConnection:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.ftp = FTP()

    def connect(self):
        print(
            "FTP connecting to {} with user={} and password={}".format(
                self.host, self.user, self.password
            )
        )
        self.ftp = FTP()
        self.ftp.set_debuglevel(2)
        self.ftp.connect(self.host)
        self.ftp.login(self.user, self.password)

    def close(self):
        self.ftp.close()

    def dir(self):
        self.ftp.dir()


f = Archivatix()
