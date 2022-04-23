# dotfiles

[TODO](https://github.com/s373r/dotfiles/issues/5)

### Useful commands

**Reset zsh environment**
```shell
$ INSTALL_GIT=yes chezmoi apply ~/.antigenrc --verbose && rm -rf ~/.antigen && zsh
```

**Testing**

1. Create a new isolated environment
```shell
$ podman run -it fedora
```

2. Install
```shell
$ sudo dnf install -y git zsh && INSTALL_GIT=yes INSTALL_PACKAGES=yes sh -c "$(curl -fsLS git.io/chezmoi)" -- init --apply s373r --verbose
```
