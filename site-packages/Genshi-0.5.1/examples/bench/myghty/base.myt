<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">

<%method wrap>
<%args scope="request">
  title
</%args>
<div id="header">
  <h1><% title %></h1>
</div>

<% m.content() %>

</%method>

<div id="footer"></div>
</html>

<%method greeting>
<%args>
   name
</%args>
Hello, <% name | h %>
</%method>
