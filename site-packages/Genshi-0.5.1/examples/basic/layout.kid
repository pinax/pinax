<div xmlns:py="http://purl.org/kid/ns#" py:strip="">
  <head>
    <title>Hello ${hello}</title>
    <style type="text/css">@import(style.css)</style>
  </head>
  <div py:def="macro1">reference me, please</div>
  <div py:def="macro2(name, classname='expanded')" class="${classname}">
    Hello ${name.title()}
  </div>
  <span py:match="item.tag == '{http://www.w3.org/1999/xhtml}greeting'" class="greeting">
    Hello ${item.get('name')}
  </span>
  <span py:match="item.tag == '{http://www.w3.org/1999/xhtml}span' and item.get('class') == 'greeting'"
        py:content="item.text" style="text-decoration: underline" />
</div>
