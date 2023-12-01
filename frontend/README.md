### Saasr Frontend

## Getting Started

# Prepare wsl:

- Edit /etc/wsl.conf and add:
  [interop]
  enabled=false
  appendWindowsPath=false

- restart the wsl using
  wsl --shutdown

- wait 8 seconds

# Install dependencies

yarn install

# Install orval and prettier globally:

npm i -g orval
npm i -g prettier

# Create api functions and models

orval

# Run the app

yarn start

This will automatically open [http://localhost:3000](http://localhost:3000).

# Based on

https://github.com/m6v3l9/react-material-admin
