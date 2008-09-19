<%args>
	title
	items
	user
</%args>

<head>
  <title><% title %></title>
</head>

 <&|base.myt:wrap &>
  <div><& base.myt:greeting, name=user &></div>
  <div><& base.myt:greeting, name="me"&></div>
  <div><& base.myt:greeting, name="world" &></div>

  <h2>Loop</h2>
%if items:
      <ul>
%	for item in items:
  <li><% item %></li>
%
      </ul>
%

 </&>
