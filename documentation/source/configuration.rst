Configuration
=============
Some importers and exporters require default values to use during conversion.
These values are stored in the configuration file to allow for overriding.

The configuration files use the YAML format. The default values are store in the `config.yml` file. 
`Configuration.get(key)` will return the highest priority value for the given key.

Keys are separated by periods, for example `a.b.0` will return the number 1 from the following configuration:

.. code-block:: yaml

    a:
        b:
            - 1
            - 2
            - 3
        c: d

Referencing Additional Configuration Files
------------------------------------------
A configuration file can reference additional configuration files using the `file` key.

It is used as a `file:<path>` string, where `<path>` is the path to the configuration file to load.
If this is found in the configuration tree, the referenced file will be loaded and merged into the current configuration.

Example
^^^^^^^

.. code-block:: yaml

    "file1.yml"
    a:
        b: <file:file2.yml>
        c: d

    "file2.yml"
    e: f

The above configuration for `file1.yml` will be equivalent to the following:

.. code-block:: yaml

    a:
        b:
            e: f
        c: d



Overlays and Priorities
-----------------------
The `Configuration.load_config(path, priority=0)` method can be used to load additional configuration files.

The configuration file can be overridden by loading additional configuration files with higher priority and conflicting values.
Higher priority values will override lower priority values.

There can only be one configuration with the same priority, loading a configuration with the same priority **will override the previous configuration**.
Priorities also serve as the identifier for the configuration for deletion and retrieval.

Structure in ePowCoRe
---------------------

The default configuration is stored in the `config.yml` file in the root of the package.

It references additional configuration files in the `config` directory.

The `config` directory contains the following files:

- `jmdl.yml` - Default values for the JMDL importer/exporter
- `powerfactory.yml` - Default values for the PowerFactory importer/exporter
- `rscad.yml` - Default values for the RSCAD importer/exporter and mappings for connection ports
- `simscape.yml` - Default values and subsystem definitions for the Simscape importer/exporter

Details for the configuration files can be found in the documentation for the respective importer/exporter.
