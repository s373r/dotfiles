# dotfiles

[TODO: add more details](https://github.com/s373r/dotfiles/issues/5)

### ✨ New machine setup

```shell
$ sh -c "$(curl -fsLS s373r.github.io/dotfiles)"
```

### 🔧 Useful commands

**Reset zsh environment**
```shell
$ s373r-zsh-reset-env
```

**Testing**

1. Create a VM and boot Fedora ISO (without installation)

2. Install
```shell
$ DEBUG=1 sh -c "$(curl -fsLS s373r.github.io/dotfiles)"
```
