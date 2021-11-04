### Accountx
Manage personal finance
record daily expenses, loans etc.

## Dev Setup

1. initialize virtual environment and activate it

```
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```
 pip install -r requirements.txt
```

### Run

```
export FLASK_APP=accountx
export FLASK_ENV=development

# then run 

flask run 
```