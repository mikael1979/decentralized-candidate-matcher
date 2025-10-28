#!/usr/bin/env python3
import sys
import os

# Lisää services-hakemisto polkuun
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from installation_manager import InstallationManager

def main():
    installer = InstallationManager()
    success = installer.run()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
