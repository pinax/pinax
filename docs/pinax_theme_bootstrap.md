# Pinax Theme Bootstrap

In all our projects we’ve been maintaining a theme based on `Bootstrap`, `Font Awesome`, and `jQuery`. We previously vendored these packages and had an undocumented build process pre-configured in our starter projects that use this theme. We are now using proper packaging in the starter projects.

Starting with [version 6.0.0](http://blog.pinaxproject.com/2015/08/02/pinax-theme-bootstrap-6-0-0-released/), [pinax-theme-bootstrap](https://github.com/pinax/pinax-theme-bootstrap) ships with templates and it’s own small javascript file.

## Dependencies

The templates in this project are currently tested with the following versions:

* `Bootstrap 3.3.5`
* `Font Awesome 4.4.0`
* `jQuery 2.1.4`

## Upgrade Notes

Upgrading to 6.0, you should be aware of a few changes:

* `style_base` and `extra_style` blocks have been merged into styles
* `script_base` and `extra_script` blocks have been merged into `scripts` and the `theme.js` script is now loaded within a `theme_script` block after the `scripts block`. It now expects that you'll load the necessary `jQuery` library at the project level in the `scripts` block.
* No vendored assets ship with the theme anymore. You are responsible for setting up your own static assets at the project level. We have made it easy by just using one of our starter projects.

If you are not using one of our starter projects, you will need to go about setting up a build environment to use these libraries. We recommend using [webpack](http://webpack.github.io) and installing these libraries with [npm](https://www.npmjs.com).


## Reference Implementation

We have provided a reference implementation of using `npm` and `webpack`  in our most popular starter project, the `pinax-project-account` [project](https://github.com/pinax/pinax-project-account). To build the `package.json` (`npm`‘s version of `requirements.txt`) simply follow these steps:

```
npm init  # taking all defaults
npm install bootstrap font-awesome jquery --save  # the core libraries we need
npm install webpack  --save # the builder
npm install extract-text-webpack-plugin --save  # plugin to break apart files
npm install css-loader style-loader file-loader less-loader babel-loader --save
```

Subsequent developers (or if you are using this starter project), can simply issue:

```
npm install
```

to install everything in the `package.json` to a local `node_modules/` directory that `webpack` can then use to build static files.

We also provided a working `webpack.config.js` in the starter project, which provides not only a build script but also the ability to run a watcher so static assets are built as you edit them.


## Asset Changes
The starter project comes with assets prebuilt and ready to go. If you make changes to any assets you simply need to run:

```
npm install
npm run build
```

If you want to have your assets automatically rebuild whenver you save changes, you can run:

```
npm run watch
```

## Adding Libraries

If you need to add some other library, a datepicker for instance, you simply need to run the `npm install <package> --save` command, hook it up in your `static/src/js/main.js` (or elsewhere in your modules), and run `npm run build` if you were not already running `npm run watch`.

For more on our move to `webpack`and away from vendoring, please read [this blog post](http://blog.pinaxproject.com/2015/08/06/move-webpack-and-away-vendoring/).
