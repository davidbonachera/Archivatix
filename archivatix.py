import datetime
import re
import hydra
import time
import progressbar
import sys

from omegaconf import DictConfig
from ftplib import FTP
from dateutil import parser

# Just a fancy ass banner
print('''
                    _     _            _   _
     /\            | |   (_)          | | (_)
    /  \   _ __ ___| |__  ___   ____ _| |_ ___  __
   / /\ \ | '__/ __| '_ \| \ \ / / _` | __| \ \/ /
  / ____ \| | | (__| | | | |\ V / (_| | |_| |>  <
 /_/    \_\_|  \___|_| |_|_| \_/ \__,_|\__|_/_/\_\ 
 
 ''')


# @todo : Add errors on empty config files

@hydra.main(config_path="config.yaml")
class Archivatix:
    """
    An Archivatix class.

    It will parse each FTP config given in config.yaml and find files according to archiving rules.
    Two behaviors are possible, first one, search and destroy (delete files), or second search and backup (move files).
    """

    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = cfg

        # Apply rules for the archiving task
        # Files bigger then 0.01 MB and older then 2020-01-01
        origin_path = "/"
        rules = [MinSizeRule(10000), DateRule(datetime.datetime(2020, 1, 1))]

        # start_time = time.time()

        # For each FTP object inside the config.yaml, parse and apply with predefined rules.
        for credentials in cfg.ftp:
            for credential in credentials.items():
                ftp = FTPUtils(credential[1]["host"], credential[1]["username"], credential[1]["password"])
                ftp.connect()
                ftp.walk(origin_path, rules)
                ftp.close()

        # print("--- %s seconds ---" % (time.time() - start_time))
        # print("\n*****Done*****\n")


class FTPUtils:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.ftp = FTP()

    def connect(self):
        print("")
        print(
            "FTP connecting to {} with user={} ".format(
                self.host, self.user
            )
        )
        print("------------------------------------------------------------")

        self.ftp = FTP()
        self.ftp.set_debuglevel(0)
        self.ftp.connect(self.host)
        self.ftp.login(self.user, self.password)

    def walk(self, dir="/", rules=None):
        """
        Performs a recursive search of folders for files meeting a defined
        criteria

        :param dir: string The origin path
        :type rules: [Rule] A list of rules to be applied
        """
        if rules is None:
            rules = []

        # Default Mode = archive
        archive_mode = True
        destroy_mode = False

        files = []
        rules_passed = []

        # Parse all the folder of the current path and identify if the file met the rules conditions.
        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength, redirect_stdout=True)
        i = 0

        # Archive yearly, skip folder with 4 digits.
        if re.findall(r"[0-9]{4}", dir):
            return None

        print("┣ Scanning {} for directories and files".format(dir), file=sys.stdout)
        for item in self.ftp.mlsd(dir):
            i += 1
            time.sleep(0.001)
            bar.update(i)

            if item[1]['type'] == 'dir':
                # Go in the deepest folder first (post-order) with a recursive routine
                # print('{}/{}'.format(dir, item[0]))
                self.walk('{}/{}'.format(dir, item[0]), rules)

            elif item[1]['type'] == 'file':
                select_file = True

                # Apply each rule and flag the file with true or false
                for rule in rules:
                    if not rule.apply(item[1]):
                        select_file = False

                # Add the file to the list if it passes and apply a rules
                if select_file:
                    rules_passed.append(item[0])
                    if archive_mode:
                        self.archive(dir, item)
                    if destroy_mode:
                        self.destroy(dir, item)

                # List of all files
                files.append(item[0])

            # else:
            #     # System files type="cdir"/"pdir" e.g: . / ..
            #     system_files.append(item[0])

        # Check if all selected files and display those for the current directory
        if rules_passed:
            # @ToDo: improve the display of big list
            print("")
            print("Files moved / archived")
            print('\n'.join(sorted(rules_passed)))

    def archive(self, dir, file):
        timestamp = file[1]["modify"]
        folder_name = parser.parse(timestamp).year

        if str(folder_name) in self.ftp.nlst(dir):
            self.ftp.rename('{}/{}'.format(dir, file[0]), '{}/{}/{}'.format(dir, folder_name, file[0]))
        else:
            self.ftp.cwd(dir)
            self.ftp.mkd(str(folder_name))
            self.ftp.cwd("..")
            self.ftp.rename('{}/{}'.format(dir, file[0]), '{}/{}/{}'.format(dir, folder_name, file[0]))


        # self.ftp.rename(origin, destination)

    # @ToDo
    def destroy(self, curr_dir, file):
        self.ftp.delete()

    def close(self):
        self.ftp.close()

    def dir(self):
        self.ftp.dir()


class Rule:
    """
    Rule interface that defining the basic behavior of a rule.
    """

    def apply(self, file):
        print("Applying rule")


class MinSizeRule(Rule):
    def __init__(self, min_size):
        self.min_size = min_size

    # @Override
    def apply(self, file) -> bool:
        return int(file["size"]) > self.min_size


class DateRule(Rule):
    def __init__(self, max_date):
        self.max_date = max_date

    # @Override
    def apply(self, file) -> bool:
        timestamp = file['modify']
        file_date = parser.parse(timestamp)
        return file_date < self.max_date


f = Archivatix()
