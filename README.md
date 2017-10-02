# SQLGitHub

SQLGitHub - Access GitHub API with SQL-like syntaxes


## Installation

1. Install prerequisites  
```bash
pip install requests prompt_toolkit pygments
```

2. Install my patched PyGithub  
```bash
git clone https://github.com/lnishan/PyGithub.git
cd PyGithub
sudo ./setup.py build
sudo ./setup.py install
```

3. Start SQLGitHub
```bash
python SQLGitHub.py
```

## Sample Usage

- Get name and description from all the repos in [abseil](https://github.com/abseil)
```sql
select name, description from abseil.repos
```
- Get last-updated time and title of the issues closed in the past 3 days in [servo](https://github.com/servo).
```sql
select updated_at, title from servo.issues.closed.3
```

![Screenshot](https://i.imgur.com/l1Nqctj.png)
