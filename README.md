# suhail

**The [nazm.dev](https://nazm.dev) website and book.**

*Suhail* (Canopus) is the star Arab navigators steered by — the guide.

The site is an [mdBook](https://rust-lang.github.io/mdBook/) (0.5.4) built from the documentation
**committed** in the [compiler repository](https://github.com/Nazm-Lang/nazm): `deploy.sh` reads it
through `git archive` at a ref, so a working tree's uncommitted edits never reach the site.

| File | |
| --- | --- |
| `SUMMARY.md` | the book's table of contents |
| `exclude.txt` | internal pages kept off the public site |
| `prep.py` | turns the repository's `docs/` and `README.md` into the book's source |
| `book.toml` | mdBook settings |
| `deploy.sh` | build at a ref, then rsync to the web root |

```sh
cp deploy.env.example deploy.env   # REPO, HOST, WEBROOT for this machine
NO_DEPLOY=1 ./deploy.sh v0.9.0     # build only, into build/book
./deploy.sh v0.9.0                 # build and deploy
```

`bin/mdbook` is the mdBook binary (not committed).

Contributions are not accepted yet. Licence: Apache License 2.0 with LLVM Exceptions —
[`LICENSE`](LICENSE). The documentation the site publishes is the compiler repository's, under its
licences.
