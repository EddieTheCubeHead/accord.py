# Contributing

## Feature requests and bugs

If you are looking to contribute ideas or bug reports, please make an issue in the library's
[issue tracker](https://github.com/EddieTheCubeHead/accord.py/issues) using the appropriate issue template. The issue 
templates contain fields that should all be filled unless directly stated otherwise in the template. If you are 
looking to make a contribution in the form of code, please read the following section.

## Contributing code

If you would like to contribute code to the project feel free to make a pull request. Both pull requests about 
issues in the issue tracker and brand-new features are considered. If the pull request is not about an issue marked 
with the "ready for development"-label, the main maintainer of the project, 
[Eetu Asikainen](https://github.com/EddieTheCubeHead), will decide whether the feature or bugfix is relevant to the 
library development.

If your pull request is about an open issue, please start the pull request name with the issue number. (#1: Add 
contribution guidelines)

### Code style

Please make sure your code adheres to the [pep-8 standard](https://peps.python.org/pep-0008/) and is generally 
readable and neat, but don't stress too much. The worst that can happen is a change request.

All exposed interface members (classes, attributes, methods, constants...) should have a Google-style docstring
describing their functionality and use.

### Testing

All features or bugfixes should be automatically tested. Enhance the testing bot (`test/testbot`) to enable testing the
feature or bug and write tests for all functionality introduced in an appropriate folder inside the `test`-directory

## Running the testing bot (for local development)

To run the testing bot you need to create a "secrets.json" -file in the root folder of the bot. There you should supply 
two key-value pairs. "GUILD_ID": int and "TOKEN": str. You can get the "GUILD_ID" by
[enabling developer mode in discord](https://beebom.com/how-enable-disable-developer-mode-discord/), right-clicking on
the guild you are using for testing your local version and selecting "Copy ID".

To get the "BOT_TOKEN" you need to
[create a bot account in discord developer portal](https://discordpy.readthedocs.io/en/stable/discord.html).

Once you have both values, the file should look something like this:

```
{
    "TOKEN": "my_cool_bot_token",
    "GUILD_ID": 314159265359
}
```