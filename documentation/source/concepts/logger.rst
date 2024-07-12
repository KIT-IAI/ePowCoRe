Logger
------

To better understand the changes being applied to a model during the conversion from one format to another, ``epowcore.generic.logger`` implements a singleton logger class.

The ``Logger.new(name, selected, print_to_console)`` method returns an integer value as a handle. This handle can later be used to select the logger again or to close it.

``Logger.get().save_to_file(filename)`` saves the log to a file with the name of the logger as the first line.

Usage Example::

    handle = Logger.new("my_logger", selected=True, print_to_console=True)
    Logger.log_to_selected("This is a log message")
    handle2 = Logger.new("my_logger2", selected=False, print_to_console=True)
    Logger.log_to_selected("This is a log message to logger 2")
    Logger.get(handle).log("This is a log message to logger 1")
    Logger.get(handle2).write_to_file("my_logger2.log")
    Logger.close(handle2)
    Logger.close(handle)

The above code will produce the following output::
    
    my_logger: This is a log message
    my_logger2: This is a log message to logger 2
    my_logger: This is a log message to logger 1


Usage in Converters
^^^^^^^^^^^^^^^^^^^

The ``converter_base.py`` class and all derived converter classes create a new logger for each conversion. The logger is selected by default and prints to the console.
If a log_path is given during initialization, the logger will also save the log to a file.
The logger is closed at the end of the conversion.

During conversion, changes to the model or potential problems are logged using the ``Logger.log_to_selected(message)`` method.