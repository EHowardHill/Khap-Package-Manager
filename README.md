# Khap Package Manager

Khap is designed to be a hypothetical, hyper-simple package manager for legacy Mac OS 10.3.9 and earlier systems. The goal is for it to be easy to setup and deploy software on aging hardware that cannot support MacPorts or Homebrew.

This software is in the **proof of concept** stage. I'm not sure where I'll go with it, but it works for now. There is no setup script, as there are no publicly active servers as of right now.

For now, **bash is the only requirement client-side**. You will need Python 3 in order to use the server-side application.

`khap` is the client-side application.
`app.py` is the Flask-based server application.
`config.json` is the server-side configuration.
`static` (can) contain binaries to serve.
`promo` contains photos for this GitHub page.

## Client Side

`khap` must be run as the superuser.

On the client side, the Mac will be able to manage new software via the command line. Two commands are supported for the time being:
- `khap install XXX` will install a given package for your system.
- `khap search XXX` will search your available repositories for software. Leaving it blank will return *all* available software for your system.

Repositories are stored in `/etc/khap.d/repos`. There are no active servers, so this file must point to your local development machine's IP address and port number.

## Server Side

The server side is written in Flask. It can be quickly run and accessible over the network in debug mode using the following command: `flask run --host=0.0.0.0`. Deployment and load balancing with a tool, such as NGINX, is recommended for a production environment.

Packages do not have to be stored on the local server - they can be remote. However, one package (Python 3.1.1.1 for PowerPC) has been compiled and stored in `static` for demonstration purposes. Packages somewhat resemble `.deb` packages, and are expected to be compressed using the GZ format. They must contain a single folder named `tree`, which contains the file tree to be mirrored onto the client machine.

Edit `config.json` before starting up the Flask server in order to configure what packages are available, what versions they are currently at, and what systems they support.