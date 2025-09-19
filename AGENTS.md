# Development tips
## Important
**When needing to call 'git', use the full path** '/usr/bin/git'.
## Commits
Use the Conventional Commits flavour when creating commits. You may commit when you deem it adequate.
## Testing
If there are tests and the change set is covered by them, make the necessary implementation efforts to pass those tests before committing.

## Python interpreter
When a script needs to run a Python interpreter, try the following names in order until a valid executable is found:
```
python
python3
python3.8
python3.9
python3.10
```
If none of these are present, ask the user for the path or try the system default `/usr/bin/python3`.
