import click
from kit import Fernet


@click.group('fernet', help='fernet key')
def main():
    pass

@click.command('verify', help='verify a fernet key setup or not')
def verify_cmd():
    try:
        result = Fernet.validateOptEnv()
    except Exception as e:
        print("validation error on fernet: ", e)
        return

    if result == True:
        print("eveything is OK")

    return


@click.command('generate', help='generate a ferenet key')
def generate_cmd():
    key = Fernet.generateKey()
    click.echo("====key content below====")
    click.echo("{!s}".format(key))
    click.echo("====key content above====\n")
    click.echo("update FERENET_KEY in your .env file\n")

@click.command('encrypt', help='encryption')
def encrypt_cmd():
    key = click.prompt('fernet key', type=str)
    plain_txt = click.prompt('plain text', type=str)

    fernet = Fernet( key )
    ciphered_txt = fernet.encrypt(plain_txt)
    click.echo("ciphered text->{!s}".format(ciphered_txt))

@click.command('decrypt', help='decryption')
def decrypt_cmd():
    key = click.prompt('fernet key', type=str)
    cipher_txt = click.prompt('ciphered text', type=str)
    fernet = Fernet( key )

    plain_txt = fernet.decrypt(cipher_txt)
    click.echo("plain text->{!s}".format(plain_txt))

if __name__ == '__main__':
    try:
        main.add_command(verify_cmd)
        main.add_command(generate_cmd)
        main.add_command(encrypt_cmd)
        main.add_command(decrypt_cmd)
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
