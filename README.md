# Ouroboros

This is a learning project,
please check out our articles on https://blog.singulargarden.com to
learn more about the project.


## Setup & Dev

**Install the dependencies in the current python env:**

```
make setup
```

**Run the tests**

```
make test
```

**Use Ouroboros**

```
python main.py --help
```


## Blockchain

Currently we only provide the **blockchain** features, this will be a subcommand later.

- `init` initialise a folder with the genesis block;
- `append` adds a new block;
- `add` adds a block from another source;
- `list` shows all the blocks.


