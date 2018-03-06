"""
py2app build script for Electrum Zcash

Usage (Mac OS X):
     python setup.py py2app
"""

from setuptools import setup
from plistlib import Plist
import requests
import os
import shutil

from lib.version import ELECTRUM_VERSION as version

CERT_PATH = requests.certs.where()

name = "Electrum ZEC"
mainscript = 'electrum-zec'

plist = Plist.fromFile('Info.plist')
plist.update(dict(CFBundleIconFile='icons/electrum.icns'))


os.environ["REQUESTS_CA_BUNDLE"] = "cacert.pem"
shutil.copy(mainscript, mainscript + '.py')
mainscript += '.py'
extra_options = dict(
    setup_requires=['py2app'],
    app=[mainscript],
    packages=[
        'electrum-zec',
        'electrum-zec_gui',
        'electrum-zec_gui.qt',
        'electrum-zec_plugins',
        'electrum-zec_plugins.audio_modem',
        'electrum-zec_plugins.cosigner_pool',
        'electrum-zec_plugins.email_requests',
        'electrum-zec_plugins.greenaddress_instant',
        'electrum-zec_plugins.hw_wallet',
        'electrum-zec_plugins.keepkey',
        'electrum-zec_plugins.labels',
        'electrum-zec_plugins.ledger',
        'electrum-zec_plugins.trezor',
        'electrum-zec_plugins.digitalbitbox',
        'electrum-zec_plugins.trustedcoin',
        'electrum-zec_plugins.virtualkeyboard',

    ],
    package_dir={
        'electrum-zec': 'lib',
        'electrum-zec_gui': 'gui',
        'electrum-zec_plugins': 'plugins'
    },
    data_files=[CERT_PATH],
    options=dict(py2app=dict(argv_emulation=False,
                             includes=['sip'],
                             packages=['lib', 'gui', 'plugins'],
                             iconfile='icons/electrum.icns',
                             plist=plist,
                             resources=["icons"])),
)

setup(
    name=name,
    version=version,
    **extra_options
)

# Remove the copied py file
os.remove(mainscript)
