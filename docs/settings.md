# Settings

The package can be configured by a few settings, which can be overwritten in the `settings.py` of your project.

`TAILWIND_VERSION`
:   **Default**: `"3.3.1"`

    This defines the version of the CLI and of Tailwind CSS you want to use in your project.

`TAILWIND_CLI_PATH`
:   **Default**: `"~/.local/bin/"`

    The path where to store CLI binary on your machine. The default value aims for an installation in your home directory and is tailored for Unix and macOS systems. On Windows you might need to configure a different path.

`TAILWIND_THEME_APP`
:   **Default**: `"theme"`

    The name of the app created by calling `python manage.py tailwind init` inside your project.

`TAILWIND_SRC_CSS`
:   **Default**: `"src/styles.css"`

    The name of the input file for the Tailwind CLI, where all the directivces and custom styles are defined. This is where you add your own definitions for the different layers.

    The default content of the file looks like that.

    ```css
    @tailwind base;
    @tailwind components;
    @tailwind utilities;
    @tailwind variants;
    ```

`TAILWIND_DIST_CSS`
:   **Default**: `"css/styles.css"`

    Name of the output file. It is always relative to the `static` folder of the theme app.
