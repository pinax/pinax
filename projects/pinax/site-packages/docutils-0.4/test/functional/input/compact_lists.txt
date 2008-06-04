* This is an ordinary simple bullet list.
* It should be made compact (<p> & </p> tags omitted).

**********

* This is a bullet list that is not simple.

  There are multiple paragraphs in some items.

* It should not be made compact.

* Even though some items may have only one paragraph.

**********

.. class:: open

* This is a simple bullet list, but class="open" is set.
* It should not be made compact.

**********

.. class:: compact

* This is a bullet list that is not simple.

  There are multiple paragraphs in some items.

* However, the class="compact" setting will cause 
  all first paragraph's <p> & </p> tags to be omitted.

* Items with multiple paragraphs will not appear changed.

* Items may have one paragraph, or multiple.

  Items with multiple paragraphs will still be followed
  by vertical whitespace because of the later paragraphs.

* The effect is interesting.
