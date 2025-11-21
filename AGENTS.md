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

## Docker containers
When you need to test an image or validate a script in a specific environment, use the MCP mcp-server-docker:

- "pull_image" to test if an image exists
- "create_container" to instantiate an image, omitting superfluous args (you mostly need name, image, eventually ports, or container_id if reusing)
- "fetch_container_logs" to check results, with tail being either an integer or "all"
- When finished, clean your containers up to spare resources. You can also clean images up if you think you won't need them anymore.

When selecting a container image in the context of a task, for instance a docker-compose file, you should validate the image exists and behaves as you expect.

## Github
When looking for resources on github, use the MCP github.

- "search_repositories" to validate a source code repository name or a docker image repository on ghcr.io.
- "get_file_contents" to list a directory or fetch a file.
- "list_tags" to check tagged releases and use thoses when getting files.