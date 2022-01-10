import click
import os
import aur

class Constants:
    working_dir = f"{os.environ['HOME']}/aur"

def is_pkg_installed(package):
    return os.path.exists(f"{os.environ['HOME']}/aur/{package}")

def clean(package):
    os.system("rm -rf " + Constants.working_dir + f"/{package}")

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
        clean(package_name)
        return
    
    click.echo(f"Building {package.name}")
    os.chdir(Constants.working_dir + f"/{package.name}")
    makepkg_result = os.system("makepkg -sfcri")
    if(makepkg_result != 0):
        click.echo("Failed to build and/or install, aborting install")
        clean(package_name)
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
    clean(package_name)

    click.echo("Removal succeeded")

@click.command()
@click.argument('package_name')
def search(package_name):
    if is_pkg_installed(package_name):
        click.echo(f"Package {package_name} is installed")
        return
    
    search = aur.search(package_name)
    if len(search) == 1:
        print(f"Package {search[0].name} {search[0].version}")
        return
    
    if len(search) == 0:
        print(f"No packages found")
        return
    
    print(f"Multiple packages found")
    for pkg in search:
        print(f"Package {pkg.name} {pkg.version}")

cli.add_command(install)
cli.add_command(remove)
cli.add_command(search)