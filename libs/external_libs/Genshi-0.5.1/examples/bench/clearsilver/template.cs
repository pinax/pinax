<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <title><?cs var:title ?></title>
  </head>
  <body>
    <?cs include:"header.cs" ?>
    <?cs call:greeting(user) ?>
    <?cs call:greeting('me') ?>
    <?cs call:greeting('world') ?>
    
    <h2>Loop</h2>
    <?cs if:len(items) ?>
      <ul>
        <?cs each:item = items ?>
          <li<?cs if:name(item) == len(items) ?> class="last"<?cs /if ?>><?cs var:item ?></li>
        <?cs /each ?>
      </ul>
    <?cs /if ?>
    
    <?cs include:"footer.cs" ?>
  </body>
</html>
