# Compilation Guide
For more information on writing and [compiling](https://joss.readthedocs.io/en/latest/paper.html#checking-that-your-paper-compiles) the paper refer to the [joss documentation](https://joss.readthedocs.io/en/latest/paper.html#).

This directory should include the `paper.md`, `paper.bib` and any additional figures as needed.

## Docker Compose
I have rewritten the [instructions for docker](https://joss.readthedocs.io/en/latest/paper.html#docker) into a docker compose file, so you just have to run the following from within this directory:
```sh
docker compose up
```

## Docker Run
If you do want to compile the paper directly via docker run instead, the following should do too:
```sh
docker run --rm \
    --volume $PWD/:/data \
    --user $(id -u):$(id -g) \
    --env JOURNAL=joss \
    openjournals/inara
```

Notice that you have to run it from within this `paper` directory.

In any case, if everything ran successfully, a `paper.pdf` file was generated in the same directory.