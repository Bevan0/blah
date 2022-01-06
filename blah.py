import click
import os
import aur

class Constants:
    working_dir = f"{os.environ['HOME']}/aur"

def is_pkg_installed(package):
    return os.path.exists(f"{os.environ['HOME']}/aur/{package}")

@click.group()
def cli(): pass

@click.command()
@click.argument("package_name")
def install(package_name):
    package = None
    try:
        package = aur.info(package_name)
    except:
        click.echo("Package doesn't exist on AUR, aborting install")
        return
    
    click.echo(f"Found package: {package.name} {package.version}")
    
    if is_pkg_installed(package.name):
        click.echo(f"Package is already installed on this system, aborting")
        return

    click.echo(f"Downloading {package.name}")
    os.chdir(Constants.working_dir)
    gitclone_result = os.system(f"git clone https://aur.archlinux.org/{package.name}.git")
    if(gitclone_result != 0):
        click.echo("Failed to download, aborting install")
        return
    
    click.echo(f"Building {package.name}")
    os.chdir(Constants.working_dir + f"/{package.name}")
    makepkg_result = os.system("makepkg -sfcri")
    if(makepkg_result != 0):
        click.echo("Failed to build/install, aborting install")
        return
    
    click.echo(f"Installed package successfully")

@click.command()
@click.argument('package_name')
def remove(package_name):
    if not is_pkg_installed(package_name):
        click.echo("Package is not installed, aborting removal")
        return
    
    click.echo("Removing from pacman")
    pacman_result = os.system(f"sudo pacman -R {package_name}")
    if (pacman_result != 0):
        click.echo("Failed to remove from pacman, aborting removal")
        return

    click.echo("Removing local build files")
    os.chdir(Constants.working_dir)
    os.remove(package_name)

    click.echo("Removal succeeded")

cli.add_command(install)
cli.add_command(remove)