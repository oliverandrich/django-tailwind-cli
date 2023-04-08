# Usage

## Running in development mode

To start the the CLI in watch mode during development, run the following command. This command needs to be run in a second shell besides the normal debug server. It does not replace the development server.

```shell
python manage.py tailwind watch
```

This command takes care that the stylesheet is updated in the background if you change any of the files configured in the `tailwind.config.js` in the `theme` app. The default configuration looks like that. It find all template files inside a global template directory and also inside all apps of the project.

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/line-clamp'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

## Build for production

To create an optimized production built of the stylesheet run the following command. Afterwards you are ready to deploy.

```shell
python manage.py tailwind build
```
