#!/usr/bin/python
#
# Copyright (C) 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This file demonstrates how to use the Google Data API's Python client library
# to interface with the Blogger service.  There are examples for the following
# operations:
#
# * Retrieving the list of all the user's blogs
# * Retrieving all posts on a single blog
# * Performing a date-range query for posts on a blog
# * Creating draft posts and publishing posts
# * Updating posts
# * Retrieving comments
# * Creating comments
# * Deleting comments
# * Deleting posts


__author__ = 'lkeppler@google.com (Luke Keppler)'


from gdata import service
import gdata
import atom
import getopt
import sys


class BloggerExample:

  def __init__(self, email, password):
    """Creates a GDataService and provides ClientLogin auth details to it.
    The email and password are required arguments for ClientLogin.  The
    'source' defined below is an arbitrary string, but should be used to
    reference your name or the name of your organization, the app name and
    version, with '-' between each of the three values."""

    # Authenticate using ClientLogin.
    self.service = service.GDataService(email, password)
    self.service.source = 'Blogger_Python_Sample-1.0'
    self.service.service = 'blogger'
    self.service.server = 'www.blogger.com'
    self.service.ProgrammaticLogin()

    # Get the blog ID for the first blog.
    feed = self.service.Get('/feeds/default/blogs')
    self_link = feed.entry[0].GetSelfLink()
    if self_link:
      self.blog_id = self_link.href.split('/')[-1]

  def PrintUserBlogTitles(self):
    """Prints a list of all the user's blogs."""

    # Request the feed.
    query = service.Query()
    query.feed = '/feeds/default/blogs'
    feed = self.service.Get(query.ToUri())

    # Print the results.
    print feed.title.text
    for entry in feed.entry:
      print "\t" + entry.title.text
    print

  def CreatePost(self, title, content, author_name, is_draft):
    """This method creates a new post on a blog.  The new post can be stored as
    a draft or published based on the value of the is_draft parameter.  The
    method creates an GDataEntry for the new post using the title, content,
    author_name and is_draft parameters.  With is_draft, True saves the post as
    a draft, while False publishes the post.  Then it uses the given
    GDataService to insert the new post.  If the insertion is successful, the
    added post (GDataEntry) will be returned.
    """

    # Create the entry to insert.
    entry = gdata.GDataEntry()
    entry.author.append(atom.Author(atom.Name(text=author_name)))
    entry.title = atom.Title(title_type='xhtml', text=title)
    entry.content = atom.Content(content_type='html', text=content)
    if is_draft:
      control = atom.Control()
      control.draft = atom.Draft(text='yes')
      entry.control = control

    # Ask the service to insert the new entry.
    return self.service.Post(entry, 
      '/feeds/' + self.blog_id + '/posts/default')

  def PrintAllPosts(self):
    """This method displays the titles of all the posts in a blog.  First it
    requests the posts feed for the blogs and then it prints the results.
    """

    # Request the feed.
    feed = self.service.GetFeed('/feeds/' + self.blog_id + '/posts/default')

    # Print the results.
    print feed.title.text
    for entry in feed.entry:
      if not entry.title.text:
        print "\tNo Title"
      else:
        print "\t" + entry.title.text
    print

  def PrintPostsInDateRange(self, start_time, end_time):
    """This method displays the title and modification time for any posts that
    have been created or updated in the period between the start_time and
    end_time parameters.  The method creates the query, submits it to the
    GDataService, and then displays the results.
  
    Note that while the start_time is inclusive, the end_time is exclusive, so
    specifying an end_time of '2007-07-01' will include those posts up until
    2007-6-30 11:59:59PM.

    The start_time specifies the beginning of the search period (inclusive),
    while end_time specifies the end of the search period (exclusive).
    """

    # Create query and submit a request.
    query = service.Query()
    query.feed = '/feeds/' + self.blog_id + '/posts/default'
    query.updated_min = start_time
    query.updated_max = end_time
    query.orderby = 'updated'
    feed = self.service.Get(query.ToUri())

    # Print the results.
    print feed.title.text + " posts between " + start_time + " and " + end_time
    print feed.title.text
    for entry in feed.entry:
      if not entry.title.text:
        print "\tNo Title"
      else:
        print "\t" + entry.title.text
    print

  def UpdatePostTitle(self, entry_to_update, new_title):
    """This method updates the title of the given post.  The GDataEntry object
    is updated with the new title, then a request is sent to the GDataService.
    If the insertion is successful, the updated post will be returned.

    Note that other characteristics of the post can also be modified by
    updating the values of the entry object before submitting the request.

    The entry_to_update is a GDatEntry containing the post to update.
    The new_title is the text to use for the post's new title.  Returns: a
    GDataEntry containing the newly-updated post.
    """
    
    # Set the new title in the Entry object
    entry_to_update.title = atom.Title('xhtml', new_title)
    
    # Grab the edit URI
    edit_uri = entry_to_update.GetEditLink().href  

    return self.service.Put(entry_to_update, edit_uri)

  def CreateComment(self, post_id, comment_text):
    """This method adds a comment to the specified post.  First the comment
    feed's URI is built using the given post ID.  Then a GDataEntry is created
    for the comment and submitted to the GDataService.  The post_id is the ID
    of the post on which to post comments.  The comment_text is the text of the
    comment to store.  Returns: an entry containing the newly-created comment

    NOTE: This functionality is not officially supported yet.
    """

    # Build the comment feed URI
    feed_uri = '/feeds/' + self.blog_id + '/' + post_id + '/comments/default'

    # Create a new entry for the comment and submit it to the GDataService
    entry = gdata.GDataEntry()
    entry.content = atom.Content(content_type='xhtml', text=comment_text)
    return self.service.Post(entry, feed_uri)

  def PrintAllComments(self, post_id):
    """This method displays all the comments for the given post.  First the
    comment feed's URI is built using the given post ID.  Then the method
    requests the comments feed and displays the results.  Takes the post_id
    of the post on which to view comments. 
    """

    # Build comment feed URI and request comments on the specified post
    feed_url = '/feeds/' + self.blog_id + '/comments/default'
    feed = self.service.Get(feed_url)

    # Display the results
    print feed.title.text
    for entry in feed.entry:
      print "\t" + entry.title.text
      print "\t" + entry.updated.text
    print

  def DeleteComment(self, post_id, comment_id):
    """This method removes the comment specified by the given edit_link_href, the
    URI for editing the comment.
    """
    
    feed_uri = '/feeds/' + self.blog_id + '/' + post_id + '/comments/default/' + comment_id
    self.service.Delete(feed_uri)

  def DeletePost(self, edit_link_href):
    """This method removes the post specified by the given edit_link_href, the
    URI for editing the post.
    """

    self.service.Delete(edit_link_href)
  
  def run(self):
    """Runs each of the example methods defined above, demonstrating how to
    interface with the Blogger service.
    """

    # Demonstrate retrieving a list of the user's blogs.
    self.PrintUserBlogTitles()
  
    # Demonstrate how to create a draft post.
    draft_post = self.CreatePost("Snorkling in Aruba",
      "<p>We had <b>so</b> much fun snorkling in Aruba<p>",
      "Post author", True)
    print "Successfully created draft post: \"" + draft_post.title.text + "\".\n"
  
    # Demonstrate how to publish a public post.
    public_post = self.CreatePost("Back from vacation",
      "<p>I didn't want to leave Aruba, but I ran out of money :(<p>",
      "Post author", False)
    print "Successfully created public post: \"" + public_post.title.text + "\".\n"
  
    # Demonstrate various feed queries.
    print "Now listing all posts."
    self.PrintAllPosts()
    print "Now listing all posts between 2007-04-04 and 2007-04-23."
    self.PrintPostsInDateRange("2007-04-04", "2007-04-23")

    # Demonstrate updating a post's title.
    print "Now updating the title of the post we just created:"
    public_post = self.UpdatePostTitle(public_post, "The party's over")
    print "Successfully changed the post's title to \"" + public_post.title.text + "\".\n"
  
    # Demonstrate how to retrieve the comments for a post.

    # Get the post ID and build the comments feed URI for the specified post
    self_id = public_post.id.text 
    tokens = self_id.split("-")
    post_id = tokens[-1]
    
    print "Now posting a comment on the post titled: \"" + public_post.title.text + "\"."
    comment = self.CreateComment(post_id, "Did you see any sharks?")
    print "Successfully posted \"" + comment.content.text + "\" on the post titled: \"" + public_post.title.text + "\".\n"
    
    comment_id = comment.GetEditLink().href.split("/")[-1]
    
    print "Now printing all comments"
    self.PrintAllComments(post_id)
    
    # Delete the comment we just posted
    print "Now deleting the comment we just posted"
    self.DeleteComment(post_id, comment_id)
    print "Successfully deleted comment." 
    self.PrintAllComments(post_id)

    # Get the post's edit URI    
    edit_uri = public_post.GetEditLink().href
    
    # Demonstrate deleting posts.
    print "Now deleting the post titled: \"" + public_post.title.text + "\"."
    self.DeletePost(edit_uri)
    print "Successfully deleted post." 
    self.PrintAllPosts()


def main():
  """The main function runs the BloggerExample application with the provided
  username and password values.  Authentication credentials are required.
  NOTE:  It is recommended that you run this sample using a test account."""

  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["email=", "password="])
  except getopt.error, msg:
    print ('python BloggerExample.py --email [email] --password [password] ')
    sys.exit(2)

  email = ''
  password = ''

  # Process options
  for o, a in opts:
    if o == "--email":
      email = a
    elif o == "--password":
      password = a
    
  if email == '' or password == '':
    print ('python BloggerExample.py --email [email] --password [password]')
    sys.exit(2)

  sample = BloggerExample(email, password)
  sample.run()


if __name__ == '__main__':
  main()
