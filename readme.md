# PyLox

Python 3.10 implementation of the Tree-Walk interpreter for the Lox programming language from the book [Crafting Interpreters](https://craftinginterpreters.com/) by [Robert Nystrom](https://github.com/munificent).

The interpreter in complete, but I will add an implementation for some of the challenges proposed in the book.

---

To run the interpreter in REPL mode

```shell
python main.py
```

To run the interpreter with an input file

```shell
python main.py <input_file_name>.lox
```

## TODO

- [ ] Complete source code tests;
- [ ] Refactor:
  - [ ] do not use visitor pattern, use match statements instead;
- [ ] challenge 2. ch. 6 "Parsing Expressions" => implement '?:' operator;
- [ ] challenge 3. ch. 6 "Parsing Expressions" => error production for incomplete;
- [ ] binary operator;
- [ ] Static methods and getters (Ch. 12/Challenges);
