# Style Guide for Contributors

## Python

### Type Annotations

- Use `list, dict, tuple` and `|` instead of importing `List, Dict, Tuple, Union` from `typing`.
- Use `X | None` instead of `Optional[X]`.

### General

- Avoid using `list(filter(lambda))` to filter a list. Use `[x for x in ... if ...]` instead.
    - This way, mypy can infer the type if the list filter with `isinstance(x, type)`.
- Similar for `map(lambda)`. Prefer comprehensions instead.
    - Example:  
        `list(map((lambda x: tuple(map((lambda y: float(y)), x))), p))`  
        becomes  
        `[tuple(float(y) for y in x) for x in p]`


### Comments

- Avoid inline comments if they lead to (ugly) line breaks. Move the comment to the line before the code in this case.
    - Example:  
    `created_components[component] = insert_subsystem(eng, component, model_name) # Create simple subsystem`  
    will be reformatted by *black* as  
    ```
    created_components[component] = insert_subsystem(
        eng, component, model_name
    )  # Create simple subsystem
    ```

#### Docstrings

- Use *sphinx* as docstring style, e.g. in extension *autoDocstring*.
- Start text in the first line of the docstring. E.g.

```
    """Insert a subsystem into the model from the components.

    :param eng: MATLAB engine
    :param subsystem: Subsystem to insert
    :param model_name: Name of the model
    :return: The inserted Subsystem in Simscape
    """
```

### Other Style Guides

- Google: https://github.com/google/styleguide/blob/gh-pages/pyguide.md