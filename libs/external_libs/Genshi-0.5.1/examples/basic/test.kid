<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'layout.kid'"
      lang="en">
 <body class="${bozz}">
  <ul py:attrs="{'id': 'second', 'class': None}" py:if="len(items) > 0">
   <li py:for="item in items">Item $prefix${item.split()[-1]}</li>
   XYZ ${hey}
  </ul>
  ${macro1()} ${macro1()} ${macro1()}
  ${macro2('john')}
  ${macro2('kate', classname='collapsed')}
  <div py:content="macro2('helmut')" py:strip="">Replace me</div>
  <greeting name="Dude" />
  <greeting name="King" />
  <span class="greeting">Hello Silicon</span>
 </body>
</html>
