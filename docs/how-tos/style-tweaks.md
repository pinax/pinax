# Style Tweaks


## How to edit LESS and rebuild CSS

To edit LESS you will need to go to the less file you wish to change. The LESS
files are located in `static/src/less/`. In this example, we will use
`custom.less`.

In `custom.less` add the CSS changes you want to make to your site:
```
...
p{
  font-size: 18;
  color: red;
}
```
Save `custom.less`.

Before rebuilding the CSS, make sure you have `npm` installed by running the
following command:
```
npm install
```

To rebuild the CSS, be sure to open two command windows for the following commands:

In one window, you will run:
```
npm run build
```
This will rebuild your CSS changes.

In the second window, you will run:
```
npm run watch.
```
This will ensure that the changes will be rebuilt on save.

You can refresh your browser at this point to review your changes.

To make a production build, you will run:
```
npm run build
```
before committing.
 
## How to edit the footer

If you want to make changes to the footer, you will first locate `_footer.html`
located under the `templates` directory. Once you open `_footer.html`, you can
customize the footer anyway you like:
```
{% load i18n %}

My own footer.

{% trans "&copy; 2015 &lt;your company here&gt;" %}
```

Be sure to save `_footer.html`.

## How to change the site name in the top left

To change the site name, you will go to `fixtures/sites.json`. In `sites.json`,
you will modify the file as shown:
```
[
    {
        "pk": 1,
        "model": "sites.site",
        "fields": {
            "domain": "localhost:8000",
            "name": "MySite [localhost]"
        }
    },
    {
        "pk": 2,
        "model": "sites.site",
        "fields": {
            "domain": "MySite.com",
            "name": "MySite"
        }
    }
]
```
After the modification, save `sites.json` and type the following command:
```
./manage.py loaddata sites
```

## How to change the top left to be a logo

To change the top left to be a logo, you can modify `site_base.html` under
`{% block topbar_base %}`:
```
{# remove to bring back topbar #}
{% block topbar_base %}
  <img src="{% static 'logo.jpg' %}" alt="logo" />
  ...
{% endblock %}
```

Be sure to save `site_base.html`

## How to add a left nav bar

To add a left nav bar, you can modify `site_base.html` under `{% topbar_base %}`,
just like we did in the example above for the logo:
```
{# remove to bring back topbar #}
{% block topbar_base %}
  <nav class="navbar navbar-inverse">
    <a href="page1Url">Page1</a> |
    <a href="page2Url">Page2</a>
  </nav>
{% endblock %}
```

Be sure to save `site_base.html`.
