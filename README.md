# SQLGitHub

SQLGitHub - Access GitHub API with SQL-like syntaxes

SQLGitHub features a SQL-like syntax that allows you to:   
**Query information about an organization as a whole.**

You may also think of it as a better, enhanced frontend layer built on top of GitHub's RESTful API.


## Installation

1. Install prerequisites  
```bash
pip install requests prompt_toolkit pygments regex
```

2. Install my patched PyGithub  
```bash
git clone https://github.com/lnishan/PyGithub.git
cd PyGithub
./setup.py build
sudo ./setup.py install
```

3. Start SQLGitHub
```bash
./SQLGitHub.py
```

## Sample Usage

### → Get name and description from all the repos in [abseil](https://github.com/abseil).

```sql
select name, description from abseil.repos
```

![Screenshot1](https://i.imgur.com/OG5c2GS.png)

---

### → Get last-updated time and title of the issues closed in the past 3 days in [servo](https://github.com/servo) listed in descending order of last-updated time.

```sql
select updated_at, title from servo.issues.closed.3 order by updated_at, desc
```

![Screenshot2](https://i.imgur.com/nyXdiEh.png)

---

### → Get top 10 most-starred repositories in [servo](https://github.com/servo).

```sql
select concat(concat("(", stargazers_count, ") ", name), ": ", description) from servo.repos order by stargazers_count desc, name limit 10
```

![Screenshot3](https://i.imgur.com/sl2Ztrp.png)

---

### → Get top 10 contributors in [servo](https://github.com/servo) for the past 7 days based on number of commits.

```sql
select login, count(login) from servo.commits.7 group by login order by count(login) desc, login limit 10
```

![Screenshot4](https://i.imgur.com/2ISHbPJ.png)


## SQL Language Support

### Supported Schema

```
SELECT
    select_expr [, select_expr ...]
    FROM {org_name | org_name.{repos | issues | pulls | commits}}
    [WHERE where_condition]
    [GROUP BY {col_name | expr}
      [ASC | DESC], ...]
    [HAVING where_condition]
    [ORDER BY {col_name | expr | position}
      [ASC | DESC], ...]
    [LIMIT row_count]
```

### Supported Fields

Most of the fields listed in [GitHub API v3](https://developer.github.com/v3/) are available for query.  
For example, for `org_name.repos` queries, you can specify `id`, `name`, `full_name`, `description` ... etc. in expr's.

### Supported Functions and Operators

We are actively adding support for functions.  
Refer to `components/expression.py` for the current supported functions and operators.
