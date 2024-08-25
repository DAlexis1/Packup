import yaml
import argparse
import os

programname = "Packup"
home = ""
configpath = ""
configdir = ""


def argsparsing():
    parser = argparse.ArgumentParser(description="Backup and restore dotfiles to ~/.dotfiles")
    parser.add_argument("Action", action="store",
                        help="""newconfig = generate a default config file\n
                        backup = backup the files\n
                        restore = symlink all the files to the wanted place on a new system\n
                        uninstall=put the files back to their original place like written in config file """)
    return parser.parse_args()


def backup():
    if ".dotfiles" not in os.listdir(home):
        os.mkdir(home + "/.dotfiles")

    config = open(configpath, 'r')
    loadedconfig = yaml.safe_load(config.read())
    config.close()

    print(f"Backup with this configuration :\n{loadedconfig}\n")

    backup = loadedconfig["Backup"]
    for i in backup.keys():
        if i in os.listdir(f"{home}/.dotfiles"):
            print(f"{i} is already backup")
        else:
            backup[i] = backup[i].replace("~", home)
            if backup[i][-1] == "/":
                backup[i] = backup[i][:-1]

            os.mkdir(f"{home}/.dotfiles/{i}")

            os.rename(backup[i], f"{home}/.dotfiles/{i}/{backup[i].split("/")[-1]}")

            os.symlink(f"{home}/.dotfiles/{i}/{backup[i].split("/")[-1]}", backup[i])

    print("All files have been backup")


def restore():
    config = open(f"{home}/.dotfiles/{programname}/{programname}/{programname}.yaml", 'r')
    loadedconfig = yaml.safe_load(config.read())
    config.close()

    backup = loadedconfig["Backup"]
    for i in backup.keys():

        backup[i] = backup[i].replace("~", home)
        if backup[i][-1] == "/":
            backup[i] = backup[i][:-1]

        if not os.path.exists(backup[i]):
            backup[i] = backup[i].replace("~", home)
            if backup[i][-1] == "/":
                backup[i] = backup[i][:-1]
            os.symlink(f"{home}/.dotfiles/{i}/{backup[i].split("/")[-1]}", backup[i])
        else:
            print(f"A config already exist for {i}, please save them in another place")

    print("All files have been restored")


def newconfig():
    os.mkdir(configdir + programname)

    config = open(configpath, "w")
    defaultconfig = {
        "Backup": {
            programname: f"~/.config/{programname}"
        }
    }
    yaml.dump(defaultconfig, config)
    config.close()
    print("Default configuration generated")
    print("To add other tools to backup keep the same format 'programname: pathtoconfig'")


def uninstall():
    config = open(f"{home}/.dotfiles/{programname}/{programname}/{programname}.yaml", 'r')
    loadedconfig = yaml.safe_load(config.read())
    config.close()

    backup = loadedconfig["Backup"]
    for i in backup.keys():

        backup[i] = backup[i].replace("~", home)
        if backup[i][-1] == "/":
            backup[i] = backup[i][:-1]

        os.unlink(backup[i])
        os.rename(f"{home}/.dotfiles/{i}/{backup[i].split("/")[-1]}", backup[i])
        os.rmdir(f"{home}/.dotfiles/{i}")

    print("Dotfiles copied back to their initial directory")


def get_config_path():
    global configpath
    global home
    global configdir
    configdir = os.environ.get("XDG_CONFIG_HOME", "")
    home = os.environ.get("HOME", "")
    if configdir == "":
        if home == "":
            # It should never come there as $HOME is set from /etc/passwd
            print("Add your user config directory to the env variable XDG_CONFIG_HOME or at least your user home directory to the environment variable HOME ")
            exit(1)
        else:
            configdir = home + "/.config"
    configpath = configdir + "/" + programname + "/" + programname + ".yaml"


if __name__ == "__main__":
    get_config_path()

    args = argsparsing()

    match args.Action:
        case "backup":
            backup()
        case "restore":
            restore()
        case "newconfig":
            newconfig()
        case "uninstall":
            uninstall()
        case _:
            print("Select backup, restore, newconfig or uninstall option")
            exit(1)