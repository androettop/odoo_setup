#!/usr/bin/env python3
from clint.textui import colored
from pyfiglet import Figlet
import os
import urllib.parse


def welcome(text):
    result = Figlet()
    return colored.green(result.renderText(text))


def main():
    print(welcome('Loops.ar'))

    username = set_username()
    password = set_password()
    public_key = set_public_key()
    version = set_version()
    domain = set_domain()
    repo_url = set_repo_url()
    git_username = set_git_username()
    git_password = set_git_password()

    ready = False
    # Check data
    while not ready:
        print(
            "\nRevise que todos los datos sean correctos:")
        print(f"""
            [1] Usuario: {username}
            [2] Contraseña: {password}
            [3] Clave pública: {public_key}
            [4] Versión de Odoo: {version}
            [5] Dominio: {domain}
            [6] Repo de git: {repo_url}
            [7] Usuario de git: {git_username}
            [8] Contraseña de git: {git_password}
            """)
        choice = input("\nPresione Enter para confirmar la instalación o una de las opciones para editarla: ")
        if not choice:
            ready = True
        elif choice == 1:
            username = set_username()
        elif choice == 2:
            password = set_password()
        elif choice == 3:
            public_key = set_public_key()
        elif choice == 4:
            version = set_version()
        elif choice == 5:
            domain = set_domain()
        elif choice == 6:
            repo_url = set_repo_url()
        elif choice == 7:
            git_username = set_git_username()
        elif choice == 8:
            git_password = set_git_password()

    # Init setup

    os.system(f"useradd -m -p $(openssl passwd -crypt {password}) {username}")
    os.system(f"mkdir -p /home/{username}/.ssh")
    file = open(f"/home/{username}/.ssh/authorized_keys", "w")
    file.write(public_key)
    file.close()
    os.system(f"chown -R {username}:{username} /home/{username}/.ssh")

    os.system("echo PasswordAuthentication no >> /etc/ssh/sshd_config")
    os.system("echo PermitRootLogin no >> /etc/ssh/sshd_config")

    os.system("systemctl restart sshd")

    # Add odoo repository and install dependencies
    os.system("apt update && apt install gnupg wget -y")
    os.system("wget -O - https://nightly.odoo.com/odoo.key | apt-key add -")
    os.system(f'echo "deb http://nightly.odoo.com/{version}/nightly/deb/ ./" >> /etc/apt/sources.list.d/odoo.list')
    os.system("apt update")
    os.system(
        "apt install sudo git locales xfonts-75dpi xfonts-base gvfs colord glew-utils libvisual-0.4-plugins gstreamer1.0-tools opus-tools qt5-image-formats-plugins qtwayland5 qt5-qmltooling-plugins librsvg2-bin lm-sensors -y")
    os.system(
        "wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb")
    os.system("dpkg -i wkhtmltox_0.12.5-1.stretch_amd64.deb")
    os.system("rm wkhtmltox_0.12.5-1.stretch_amd64.deb")
    os.system("cp /usr/local/bin/wkhtmltopdf /usr/bin/")
    os.system("cp /usr/local/bin/wkhtmltoimage /usr/bin/")

    # Set locale
    os.system(
        "export LANGUAGE=en_US.UTF-8 && export LANG=en_US.UTF-8 && export LC_ALL=en_US.UTF-8 && locale-gen en_US.UTF-8 && dpkg-reconfigure locales --frontend=noninteractive")

    # Install postgresql, odoo and apache2
    os.system("apt install postgresql -y")
    os.system("apt install odoo -y")
    os.system("apt install apache2 -y")
    os.system("apt install certbot python3-certbot-apache -y")

    # Configure virtual hosts

    os.system("a2dissite 000-default.conf")
    os.system("a2enmod proxy proxy_http proxy_balancer lbmethod_byrequests")

    # input file
    fin = open("./odoo.conf", "rt")
    # output file to write the result to
    fout = open("/etc/apache2/sites-available/odoo.conf", "wt")
    # for each line in the input file
    for line in fin:
        # read replace the string and write to output file
        fout.write(line.replace('@domain@', domain))
    # close input and output files
    fin.close()
    fout.close()

    os.system("a2ensite odoo.conf")
    os.system("systemctl reload apache2")
    os.system(f'certbot --apache -d "{domain}"')

    if repo_url:
        if git_username and git_password:
            os.system(
                f"sudo -u {username} git clone https://{urllib.parse.quote(git_username)}:{urllib.parse.quote(git_password)}@{repo_url} /home/{username}/addons")
        else:
            os.system(f"sudo -u {username} git clone https://{repo_url} /home/{username}/addons")

    input("Enter para salir.")


def set_version():
    return input("\nIngrese la versión de odoo (13.0,14.0): ")


def set_username():
    return input("\nIngrese un nombre de usuario: ")


def set_password():
    return input("\nIngrese una contraseña: ")


def set_domain():
    return input("\nIngrese un dominio (sin http/https): ")


def set_public_key():
    return input("\nIngrese una clave publica: ")


def set_repo_url():
    return input("\nIngrese la url del repositorio de addons (sin http/https, vacio si no hay): ")


def set_git_username():
    return input("\nIngrese el usuario de git: ")


def set_git_password():
    return input("\nIngrese la contraseña de git: ")


if __name__ == "__main__":
    main()
