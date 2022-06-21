# Setup notes for `ubox2204`

`ubox2204` is XUbuntu 22.04 VirtuaBox guest in a Windows 11 host.

_the best Ubuntu flavor is XUbuntu_

## Fresh install

Fresh install is `xubuntu-22.04-desktop-amd64.iso` image.

## Virtualbox config

- bidirectional clipboard/drag'n drop
- 8192 MB RAM / 2 CPU
- 128 MB video memory / 3D acceleration enabled / VMSVGA
- USB 3.0

## Guest additions and related configs to access host services

- Method 1

        sudo apt install virtualbox-guest-utils virtualbox-guest-x11


- Alternatively, mount the Guest Additions cdrom and run `VBoxLinuxAdditions.run` as root

        sudo sh /path/to/VobLinuxAdditions.run

### Access shared folders

- Add the user to the `vboxsf` group. In case you are missing a graphical interface to access groups:

        sudo apt install gnome-system-tools


### Configure guest network to work with host VPN

Tested on CISCO AnyConnect: sometimes works, others not!

Explained here [https://superuser.com/questions/987150/virtualbox-guest-os-through-vpn/1035327]()

In quick summary:

- enabled to network cards in the configuration
    - 1) type NAT
    - 2) type Host-only
- enabled "allow local (LAN) access when using VPN" in the VPN config

## Git / devel

- install basic tools
    `sudo apt install git meld gftp rsync curl`

- GIT configuration
    ```bash
    git config --global user.name "Mauro Rovezzi"
    git config --global user.email "mauro.rovezzi@gmail.com"
    git config --global credential.helper "cache --timeout=36000"
    #if behind PROXY (example here at ESRF)
    git config --global http.proxy http://proxy.esrf.fr:3128
    git config --global https.proxy https://proxy.esrf.fr:3128
    ```

## Fun stuff

- Petname: a random combination of adverbs, an adjective, and an animal name `sudo apt install petname`

## Build tools

  ```bash
  #Package managers
  sudo apt install gdebi-core snapd
  #basics
  sudo apt install dkms build-essential module-assistant autoconf shtool libtool swig
  sudo m-a prepare
  #GL library/headers
  sudo apt install libglu1-mesa-dev freeglut3-dev mesa-common-dev
```

## Utils

- Disk Usage Analyzer

        sudo apt install baobab


## NOT DONE (YET)

```bash



#Bug with Qt
#===========
#https://askubuntu.com/questions/308128/failed-to-load-platform-plugin-xcb-while-launching-qt5-app-on-linux-without
sudo apt install libqt5x11extras5

###############
# WEB BROWSER #
###############
sudo apt install firefox
#Add-ons installed:
#- Ghostery (https://addons.mozilla.org/en-US/firefox/addon/ghostery/)
#- Clean Links (https://addons.mozilla.org/en-US/firefox/addon/clean-links-webext/)
#- Forget me not (https://addons.mozilla.org/en-US/firefox/addon/forget_me_not) or Self destructing cookies (https://addons.mozilla.org/en-US/firefox/addon/self-destructing-cookies-webex)


#########################################
### TEXT EDITORs/CONVERTERS/UTILITIES ###
#########################################

#VISUAL STUDIO CODE
sudo snap install code --classic
# Extensions installed directly from code
#- Python
#- markdownlint
#- reStructuredText
#- kite
#- LaTeX Workshop
#- Awesome Emacs Keymap

#ATOM
wget -O atom-amd64.deb https://atom.io/download/deb
sudo gdebi atom-amd64.deb
#if behind PROXY (example here at ESRF)
#apm config set proxy "http://proxy.esrf.fr:3128"
#apm config set https_proxy "http://proxy.esrf.fr:3128"
#install packages
apm install language-restructuredtext language-latex
apm install sublime-style-column-selection column-select
apm install autocomplete-python python-indent
#in sloth-dev
python -m pip install 'python-language-server[all]'
apm install atom-ide-ui
apm install ide-python
#pip install black
apm install atom-black

#EMACS
sudo add-apt-repository ppa:ubuntu-elisp/ppa
sudo apt update
sudo apt install emacs-snapshot aspell-en aspell-fr aspell-it
sudo update-alternatives --config emacs #select emacs-snapshot
#ln -s mydotemacsU1804.el .emacs
#starter kit
#https://github.com/bbatsov/prelude
#Emacs as Python IDE:
#http://chillaranand.github.io/emacs-py-ide/
#

#latex2rft (best for converting LaTeX to MS Word)
sudo apt install latex2rtf latex2rtf-doc

#PANDOC
sudo apt install pandoc pandoc-citeproc pandoc-data python-pandocfilters python3-pandocfilters

#PYCHARM (COMMUNITY EDITION)
sudo snap install pycharm-community --classic

######################
### PROXY SETTINGS ###
######################

# IN CASE YOU ARE INSTALLING BEHIND A PROXY (ESRF CASE HERE)
# http://askubuntu.com/questions/150210/how-do-i-set-systemwide-proxy-servers-in-xubuntu-lubuntu-or-ubuntu-studio
# set some env variables (add them in your .bashrc)
#export http_proxy=http://proxy.esrf.fr:3128/
#export https_proxy=http://proxy.esrf.fr:3128/
#export ftp_proxy=http://proxy.esrf.fr:3128/
#export no_proxy="localhost,127.0.0.1,localaddress,.localdomain.com"
#export HTTP_PROXY=http://proxy.esrf.fr:3128/
#export HTTPS_PROXY=http://proxy.esrf.fr:3128/
#export FTP_PROXY=http://proxy.esrf.fr:3128/
#export NO_PROXY="localhost,127.0.0.1,localaddress,.localdomain.com"
# notify APT of proxy settings:
# - create a file called 95proxies in /etc/apt/apt.conf.d/
# - include the following:
#Acquire::http::proxy "http://proxy.esrf.fr:3128/";
#Acquire::ftp::proxy "ftp://proxy.esrf.fr:3128/";
#Acquire::https::proxy "https://proxy.esrf.fr:3128/";
#>>> SEE ALSO PROXY SETTING FOR SPECIFIC APPLICATIONS (e.g. git, atom)
# *NOTE*: use 'sudo -E <command>' to export the proxy variables also to root!!!

#########################
# WORKFLOWS/DIRECTORIES #
#########################
# if migrating from existing machine/install
# -> manually copy 'WinLinShare' to DATA partition
# Links with VirtualBox shared folders
# symbolic link shared folders in $HOME, e.g.:
#cd $HOME
#ln -s /media/sf_WinLinShare/WORK* WORK*

#local software -> $MYLOCAL
cd; mkdir local
export MYLOCAL=$HOME/local/
#devel software -> $MYDEVEL
cd; mkdir devel
export MYDEVEL=$HOME/devel/

######################
### CUSTOM .bashrc ###
######################
echo "
file_to_load="$HOME/devel/software-notes/bash/mydotbashrcU1804.sh"
if [ -f $file_to_load ]; then
    source $file_to_load
fi
" >> $HOME/.bashrc

################
### SSH KEYS ###
################
#NOTE: -C is only a comment to identify multiple keys
ssh-keygen -o -t rsa -b 4096 -C "user@machine_virtual"
#(do not enter passphrase)
#Your identification has been saved in $HOME/.ssh/id_rsa.
#Your public key has been saved in $HOME/.ssh/id_rsa.pub.

#1) copy public key to a server
#ssh-copy-id -i $HOME/.ssh/id_rsa.pub user@host
## or if your server uses custom port number:
#ssh-copy-id -i $HOME/.ssh/id_rsa.pub -p 1234 user@host

#keep alive ssh connections from client side:
#put the following in ~/.ssh/config (send null package every 100 sec)
#ServerAliveInterval 100

#2) copy to gitlab
sudo apt install xclip
xclip -sel clip < ~/.ssh/id_rsa.pub
#paste you key in the web interface
#test if everything works
ssh -T git@gitlab.com
#should get a welcome message

#########
# CONDA #
#########
cd $MYLOCAL
wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -c -p $HOME/local/conda
source $MYLOCAL/conda/bin/activate
conda config --set always_yes yes
conda update -q conda
#conda environments are based on specific .yml files

##############
### DEVELS ###
##############
cd; cd devel
#software-notes
git clone https://github.com/maurov/software-notes.git
#xraysloth
git clone https://github.com/maurov/xraysloth.git
#+others...
#[...]
#pymca
git clone https://github.com/maurov/pymca.git
cd pymca
git remote add --track master upstream https://github.com/vasole/pymca.git
#silx
git clone https://github.com/maurov/silx.git
cd silx
git remote add --track master upstream https://github.com/silx-kit/silx.git
#xraylarch
git clone https://github.com/maurov/xraylarch.git
cd xraylarch
git remote add --track master upstream https://github.com/xraypy/xraylarch.git

################
# COLOR THEMES #
################
sudo apt install gnome-color-chooser

####################################
### GRAPHICS: INKSCAPE & FRIENDS ###
####################################
sudo add-apt-repository ppa:inkscape.dev/stable
sudo apt update
sudo apt install inkscape xclip graphviz

###################
### LIBREOFFICE ###
###################
sudo apt-add-repository ppa:libreoffice/ppa
sudo apt install libreoffice-calc libreoffice-dmaths libreoffice-draw libreoffice-math libreoffice-pdfimport libreoffice-l10n-en-gb hunspell-en-gb hyphen-en-gb mythes-en-us libreoffice-help-en-gb libreoffice-l10n-fr libreoffice-script-provider-python libreoffice-style-tango libreoffice-templates libreoffice-voikko libreoffice-wiki-publisher libreoffice-writer libreoffice-writer2latex hunspell-fr hyphen-fr mythes-fr libreoffice-l10n-it hunspell-it hyphen-it mythes-it libxrender1 libgl1 openclipart-libreoffice openclipart-libreoffice pstoedit imagemagick libpaper-utils libreoffice-java-common

#########################
### TEXLIVE & RELATED ###
#########################
sudo add-apt-repository ppa:jonathonf/texlive
sudo apt update
#A personal sub-selection from texlive-full package
sudo apt install texlive-lang-french texlive-science texlive-science-doc texlive-generic-recommended texlive-latex-extra texlive-formats-extra latexdiff texlive-binaries texlive-base texlive-latex-recommended lcdf-typetools texlive-fonts-recommended-doc texlive-pstricks-doc texlive-font-utils texlive-humanities-doc context texlive-htmlxml texlive-metapost-doc texlive-metapost texlive-pstricks purifyeps dvidvi texlive-generic-extra prosper texlive-publishers  fragmaster texlive-lang-italian texlive-fonts-recommended texlive-lang-english texlive-latex-extra-doc prerex texlive-humanities texinfo texlive-xetex texlive-fonts-extra-doc texlive-luatex feynmf texlive-fonts-extra texlive-plain-extra texlive-publishers-doc chktex texlive-extra-utils lmodern tex4ht texlive-pictures-doc psutils tex-gyre texlive-games texlive-latex-base dvipng texlive-omega latexmk lacheck tipa texlive-music texlive-latex-recommended-doc texlive-latex-base-doc texlive-pictures texlive-bibtex-extra t1utils xindy
#install non free fonts as user
wget -q http://tug.org/fonts/getnonfreefonts/install-getnonfreefonts
sudo texlua ./install-getnonfreefonts -a
getnonfreefonts -a --user

#########################
### REFERENCE MANAGER ###
#########################

#Mendeley
#========
cd; cd local
wget http://www.mendeley.com/repositories/ubuntu/stable/amd64/mendeleydesktop-latest
sudo gdebi mendeleydesktop-latest
mendeleydesktop
#Initial setup by simply profiding your login details
#Quit and TRANSFER YOUR LOCAL VERSION
cd $HOME
ln -s /media/sf_WinLinShare/biblio biblio
ln -s /media/sf_WinLinShare/nextCloudCNRS/mendeleyLinux mendeleyLinux
#rsync_cloud2ubox.sh (keep synchronized/backup with cloud - here nextCloudCNRS)
#!/bin/bash
CLOUDDIR="/media/sf_WinLinShare/nextCloudCNRS/mendeleyLinux"
#First sync MendeleyDB because, starting from version 1.7, it does not like the symbolic link
rsync -avz --delete-after $CLOUDDIR/dotLocalShareData/ $HOME/.local/share/data/Mendeley\ Ltd./
rsync -avz --delete-after $CLOUDDIR/dotLocalShare/ $HOME/.local/share/Mendeley\ Ltd./
rsync -avz --delete-after $CLOUDDIR/dotConfig/ $HOME/.config/Mendeley\ Ltd./
rsync -avz --delete-after $CLOUDDIR/dotCache/ $HOME/.cache/Mendeley\ Ltd./
#PDFs & Co
rsync -avz --delete-after $CLOUDDIR/biblio /media/sf_WinLinShare/

##################
### MULTIMEDIA ###
##################
#encoders
sudo apt install ffmpeg mencoder
#VLC & FRIENDS ###
sudo apt install vlc

#jdownloader
#download JD2Setup_x64.sh from their website
#the install manually: ./JD2Setup_x64.sh (chmod +x first)

