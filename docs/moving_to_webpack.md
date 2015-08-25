# A Move to webpack and Away from Vendoring

For a while now, we’ve been maintaining a theme we use in all our projects based on Bootstrap, Font Awesome, and jQuery. Up until today, we have just vendored the static assets and included them by leveraging Django staticfiles finders.

The [pinax-theme-bootstrap](https://github.com/pinax/pinax-theme-bootstrap) until now has been doing too many things. In addition, to providing templates, it was bundling specific versions of [jQuery](http://jquery.com), [Font Awesome](http://fontawesome.io), and [Bootstrap (style and javascript)](http://getbootstrap.com). Anytime there was a point release of any one of the three, it would require a new release of the entire theme despite over time there being very little need to change the templates.

What this meant in practice is that the libraries would get out of date and semantic versioning was hard at best, if not meaningless.

We have long adopted the view and practice that Python requirements should live in `requirements.txt` (or a `setup.py`‘s `install_requires`). Why should our frontend libraries by any different?

Starting with [version 6.0.0](http://blog.pinaxproject.com/2015/08/02/pinax-theme-bootstrap-6-0-0-released/), the theme ships with templates and it’s own small javascript file. It is documented what versions the templates are tested with but nothing restricts you from using different versions at the project level.

We have provided a reference implementation of using [npm](https://www.npmjs.com) and [webpack](http://webpack.github.io) in our most popular starter project, the `pinax-project-account` project. To build the `package.json` (`npm`‘s version of `requirements.txt`) we simply:

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

and it will install everything in the `package.json` to a local `node_modules/` directory that `webpack` can then use to build static files.

Another thing we did in the starter project was to provide a working `webpack.config.js` which provides not only a build script but also the ability to run a watcher so static assets are built as you edit them.

To signal the static files taking on it’s own parallel process to manage dependencies and requirements, we moved the `static` folder to the top level rather than inside the project package. In addition, we segment to subfolders, `src/` and `dist/` to help developers understand that you only edit the files in `src/`. Only the files winding up in `dist/` are served due to the changes in `settings.STATICFILES_DIRS`.

The starter project comes with assets prebuilt and ready to go. If you make changes to any any assets you simply need to run:

```
npm install
npm run build
```

If you want to have your assets automatically rebuild whenver you save changes, you can run:

```
npm run watch
```

If you need to add some other library, a datepicker for instance, you simply need to run the `npm install <package> --save` command, hook it up in your `static/src/js/main.js` (or elsewhere in your modules), and run `npm run build` if you were not already running `npm run watch`.
