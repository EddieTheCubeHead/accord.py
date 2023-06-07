Accord.py
=========

An acceptance testing library for discord.py
--------------------------------------------

Accord.py is a library designed to make writing acceptance tests for discord.py clients easy and fast, while offering
robust capabilities for fine-tuned mocking of all discord objects during testing.

Accord.py is designed with end-to-end tests in mind and offers the normal Assign-Act-Assert flow via the following
functionalities:

* Setup data: create and configure mock discord objects
* Fire event: call app commands or execute events like ''on_guild_join''
* Check output: discord.py internal state is not revealed, only actions performed in discord like responding to commands or guild moderation events

.. toctree::
    :maxdepth: 2
    :caption: Table of contents

    accord
