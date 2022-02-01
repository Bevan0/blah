import click
import os
import aur
import subprocess

class Constants:
    working_dir = f"{os.environ['HOME']}/aur"

def is_pkg_installed(package):
    return os.path.exists(f"{os.environ['HOME']}/aur/{package}")

def clean(package):
    os.system("rm -rf " + Constants.working_dir + f"/{package}")

@click.group()
def cli(): pass

@click.command()
@click.argument("packages_to_install", nargs=-1, required=True)
def install(packages_to_install):
    for package_name in packages_to_install:
        package = None
    
        try:
            package = aur.info(package_name)
        except:
            click.echo(f"Package {package_name} doesn't exist on AUR, skipping it")
            continue

        click.echo(f"Found package: {package.name} {package.version}")

        if is_pkg_installed(package.name):
            if len(packages_to_install) != 1: click.echo(f"Package {package.name} is already installed on this system, skipping it")
            else: click.echo(f"Package {package.name} is already installed on this system")
            continue

        click.echo(f"Downloading {package.name}")
        os.chdir(Constants.working_dir)
        gitclone_result = os.system(f"git clone https://aur.archlinux.org/{package.name}.git")
        if(gitclone_result != 0):
            if len(packages_to_install) != 1: click.echo("Failed to download, skipping it")
            else: click.echo("Failed to download, aborting")
            clean(package_name)
            continue

        click.echo(f"Building {package.name}")
        os.chdir(Constants.working_dir + f"/{package.name}")
        makepkg_result = os.system("makepkg -sfcri")
        if(makepkg_result != 0):
            if len(packages_to_install) != 1: click.echo("Failed to build and/or install, skipping it")
            else: click.echo("Failed to build and/or install, aborting")
            clean(package_name)
            continue

        click.echo(f"Installed package {package.name} successfully")
    if len(packages_to_install) != 1: click.echo("Finished installing packages successfully")

@click.command()
@click.argument('package_name', nargs=-1, required=True)
def remove(packages_to_remove):
    for package_name in packages_to_remove:
        if not is_pkg_installed(package_name):
            if len(packages_to_remove) != 1: click.echo(f"Package {package_name} is not installed, skipping it")
            else: click.echo("Package is not installed, aborting removal")
            continue

        click.echo("Removing from pacman")
        pacman_result = os.system(f"sudo pacman -R {package_name}")
        if (pacman_result != 0):
            if len(packages_to_remove) != 1: click.echo(f"Failed to remove {package_name} from pacman, skipping it")
            else: click.echo("Failed to remove from pacman, aborting removal")
            continue

        click.echo("Removing local build files")
        clean(package_name)

        click.echo(f"Removed package {package_name} successfully")

@click.command()
@click.argument('package_name')
def search(package_name):
    if is_pkg_installed(package_name):
        click.echo(f"Package {package_name} is installed")
        return
    
    search = aur.search(package_name)
    if len(search) == 1 or search[0].name == package_name:
        print(f"Package {search[0].name} {search[0].version}")
        return
    
    if len(search) == 0:
        print(f"No packages found")
        return

    print(f"Multiple packages found")
    for pkg in search:
        print(f"Package {pkg.name} {pkg.version}")

@click.command()
@click.argument('package_name', required=False)
def update(package_name):
    if not package_name:
        click.echo("Updating all packages")
        packages = os.listdir(Constants.working_dir)
        for pkg in packages:
            os.chdir(Constants.working_dir + f"/{pkg}")
            gitpull_result = subprocess.run(["git", "pull"], capture_output=True)
            if (gitpull_result.returncode != 0):
                click.echo(f"Failed to pull git repository of {pkg}, skipping")
                continue
            if (gitpull_result.stdout == b'Already up to date.\n'):
                click.echo(f"{pkg} is up to date")
                continue
            makepkg_result = os.system("makepkg -sfcri")
            if (makepkg_result != 0):
                click.echo(f"Failed to build and/or install {pkg}, skipping")
                continue
        click.echo("Update succeeded")
        return
    if not is_pkg_installed(package_name):
        click.echo("Package is not installed")
        return
    
    os.chdir(Constants.working_dir + f"/{package_name}")

    gitpull_result = subprocess.run(["git", "pull"], capture_output=True)
    if (gitpull_result.returncode != 0):
        click.echo("Failed to pull git repository, aborting update")
        return
    if (gitpull_result.stdout == b'Already up to date.\n'):
        click.echo("Already newest version.")
        return

    makepkg_result = os.system("makepkg -sfcri")
    
    if(makepkg_result != 0):
        click.echo("Failed to build and/or install, aborting update")
        return
    
    click.echo("Update succeeded")
    return

cli.add_command(install)
cli.add_command(remove)
cli.add_command(search)
cli.add_command(update)