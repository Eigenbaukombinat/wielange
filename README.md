## Installation

```
git clone https://github.com/Eigenbaukombinat/wielange.git
cd wielange
python3 -m venv .
bin/pip install -r requirements.txt
```

## Running

To run via supervisor, create `/etc/supervisor/conf.d/wielange.conf` with this:

```
[program:wielange]
directory = /home/<user>/wielange
command=/<user>/wielange/bin/python /home/<user>/wielange/wielange.py
user = <user>
```
