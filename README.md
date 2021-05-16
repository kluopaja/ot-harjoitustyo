Repository for the University of Helsinki couse *Ohjelmistotekniikka*.

# Unnamed Plane Game

A 2D shoot 'em up flying game inspired by Sopwith.

* Release for week 5: https://github.com/kluopaja/ot-harjoitustyo/releases/tag/viikko5
* Release for week 6: https://github.com/kluopaja/ot-harjoitustyo/releases/tag/viikko6


## Documentation
* [Manual](https://github.com/kluopaja/ot-harjoitustyo/blob/master/doc/manual.md)
* [Requirements specification](https://github.com/kluopaja/ot-harjoitustyo/blob/master/doc/requirements_specification.md)
* [Architecture description](https://github.com/kluopaja/ot-harjoitustyo/blob/master/doc/architecture.md)
* [Work hours](https://github.com/kluopaja/ot-harjoitustyo/blob/master/doc/work_hours.md)
* [Testing documentation](https://github.com/kluopaja/ot-harjoitustyo/blob/master/doc/testing.md)


## Installation

The following commands should be run at the project root.

1. Set up Poetry environment:
```poetry install```

2. Initialize the database:
```poetry run invoke init-database```

3. Start game:
```poetry run invoke start```

## Running tests

Tests can be run with:
```poetry run invoke test```

Coverage report can be genreated with:
```poetry run invoke coverage-report```

Pylint can be run with;
```poetry run invoke lint```
