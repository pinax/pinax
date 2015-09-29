# Releasing a Starter Project

In an effort to communicate completeness and bring some stability to our starter
projects, we tag releases. Semantic versioning applies less to starter projects
than it does to apps as things like backwards-incompatibility are a non-issue.
However, for the sake of consistency we should adhere to keeping close to it.

### Versioning Rules

* new starter projects remain untagged until they can at least run locally,
  good enough for demos and testing
* once a starter project can run for demos, start minor releases at `0.1.0`
* once a starter project is used to create a site that is running in production
  it gets bumped to `1.0.0`
* increment patch numbers if any change is fixing a bug
* increment minor numbers for any feature changes or version bumps of dependencies
  that are relatively minor
* increment major numbers for any **major** work done


### Tagging

To apply a version, we just use git tags with the project branch slug as a
prefix:

```
git tag account-0.1.0
git push --tags
```

### Update Project Manifest

After creating a new release, update [projects.json](https://github.com/pinax/pinax/blob/master/projects.json) and
add the url to the archive into the `project.json` payload.

```json
{
    "version": 1,
    "projects": {
        "zero": {
            "url": "https://github.com/pinax/pinax-starter-projects/zipball/zero",
            "process-files": ["webpack.config.js", "PROJECT_README.md"],
            "releases": [
                "https://api.github.com/repos/pinax/pinax-starter-projects/tarball/zero-1.0.0"
            ]
        }
    }
}
```

By using [Semantic Versioning](http://semver.org/) the `releases` should sort
easily so that the `pinax` command line tool can sort them easily to install the
latest.
