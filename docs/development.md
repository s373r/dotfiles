# Development

### 🔧 Useful commands

**Reset zsh environment**
```shell
$ s373r-zsh-reset-env
```

**Open `dconf-editor` to view changed extension settings**
```shell
GSETTINGS_SCHEMA_DIR=~/.local/share/gnome-shell/extensions/Vitals@CoreCoding.com/schemas dconf-editor
```

**Testing**

1. Create a VM and boot Fedora ISO (without installation)

2. Install
```shell
$ DEBUG=1 sh -c "$(curl -fsLS s373r.github.io/dotfiles)"
```
