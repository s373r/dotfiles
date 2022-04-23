# dotfiles

[TODO](https://github.com/s373r/dotfiles/issues/5)

### Useful commands

**Reset zsh environment**
```shell
$ s373r-zsh-reset-env
```

**Testing**

1. Create a VM and boot Fedora ISO (without installation)

2. Install
```shell
$ INSTALL_PACKAGES=yes sh -c "$(curl -fsLS git.io/chezmoi)" -- init --apply s373r --verbose
```
