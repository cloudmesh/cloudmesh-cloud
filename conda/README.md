# Anaconda


brew install readline xz
xcode-select --install
brew install openssl
brew install pyenv
pyenv init
pyenv local 3.6.6




To install anaconda we also use pyenv

```bash
$ pyenv install anaconda3-5.3.0
```

ANaconda breaks the pyenv model or vice versa. Please note we do not like anaconda as we can not use a virtualenv, but must use conda 

```bash
$ pyenv activate anaconda3-5.3.0
$ conda update -n base -c defaults conda
```


Does only install python 3.6.7


conda create -n python37 python=3.7.1 --no-default-packages



The following does not wor

After instalation, create a virtual environment for anacoda



```bash
pyenv virtualenv anaconda3-5.3.0 ana
```

Create an alsia in .bash_profile


Activate it with 

ANA

Update the base version with 


