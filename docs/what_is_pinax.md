# What is Pinax?

Pinax is an open source ecosystem of reusable Django apps, themes, and starter project templates.

It takes care of the things that many sites have in common so you can focus on what makes your site different.

Pinax provides:

  * **Standard project layout** for consistency and easy deployment
  * **Starter projects** that can be used as the basis for any Django website as well as some tailored-to-community sites, company sites, intranets and sites in closed beta
  * **Reusable apps** providing both back-end functionality and user-facing components
  * **Default templates** to enable quick prototyping

Pinax has been used for everything from social networks to conference websites, and from intranets to online games.

Because it's an entire ecosystem you can't just download Pinax and try it out, but there are starter projects you can do this with (see [Quick Start](quick_start.md)).

A **starter project** is a Django project template that comes with a bunch of apps already integrated with templates, etc.

Some starter projects are intended to just lay a foundation for your site. For example the "account starter project" or `pinax-project-account`, gives you user signup (optionally closed), login, password change and reset, basic user preferences all with an easy-to-customize Bootstrap-based UI.

Hundreds of sites have been built on `pinax-project-account` even if they otherwise have  nothing else in common or even use any other Pinax apps.

Some starter projects are more designed to be demos of how to use a particular reusable app or set of apps.

Yet other starter projects are designed to be out-of-the-box, fully-functional sites, ready to deploy (although we don't have many of these yet).

After you've started your Django project with a Pinax starter project, it is quite common to add other apps from the Pinax ecosystem. But the apps in Pinax are just regular Django apps. Django apps don't have to be "Pinax" apps to be added to a Pinax starter project.

Furthermore, you can use the apps in the Pinax ecosystem even if you didn't start with a Pinax starter project.

In short, you can use as little or as much of Pinax as you want. Pinax is opinionated but it's just Django. It's not designed to shield you from Django. With Pinax, you're always just doing regular Django development. You just have a lot of existing code to help you.
