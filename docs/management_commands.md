# Management Commands

`tailwind installcli`
:   Download the Tailwind CLI to path defined with `settings.TAILWIND_CLI_PATH`.

`tailwind init`
:   Create a new theme app with the name `settings.TAILWIND_THEME_APP` inside the `settings.BASE_DIR` of your project.

`tailwind watch`
:   Start the CLI in watch mode.

`tailwind build`
:   Create a production ready build of the Tailwind stylesheet. You have to run this before calling the `collectstatic` command.
