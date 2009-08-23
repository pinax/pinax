import random
from django.contrib.auth.models import User

names = """Jacob Emily Michael Emma Joshua Madison Ethan Isabella Matthew Ava
Daniel Abigail Christopher Olivia Andrew Hannah Anthony Sophia William
Samantha Joseph Elizabeth Alexander Ashley David Mia Ryan Alexis Noah
Sarah James Natalie Nicholas Grace Tyler Chloe Logan Alyssa John Brianna
Christian Ella Jonathan Taylor Nathan Anna Benjamin Lauren Samuel Hailey
Dylan Kayla Brandon Addison Gabriel Victoria Elijah Jasmine Aiden Savannah
Angel Julia Jose Jessica Zachary Lily Caleb Sydney Jack Morgan Jackson
Katherine Kevin Destiny Gavin Lillian Mason Alexa Isaiah Alexandra Austin
Kaitlyn Evan Kaylee Luke Nevaeh Aidan Brooke Justin Makayla Jordan Allison
Robert Maria Isaac Angelina Landon Rachel Jayden Gabriella
"""

surnames = """Smith Johnson Williams Brown Jones Miller Davis Garcia
Rodriguez Wilson Martinez Anderson Taylor Thomas Hernandez Moore Martin
Jackson Thompson White Lopez Le Gonzalez Harris Clark Lewis Robinson Walker
Perez Hall Young Allen Sanchez Wright King Scott Green Baker Adams Nelson
Hill Ramirez Campbell Mitchell Roberts Carter Phillips Evans Turner Torres
Parker Collins Edwards Stewart Flores Morris Nguyen Murphy Rivera Cook Rogers
Morgan Peterson Cooper Reed Bailey Bell Gomez Kelly Howard Ward Cox Diaz
Richardson Wood Watson Brooks Bennett Gray James Reyes Cruz Hughes Price
Myers Long Foster Sanders Ross Morales Powell Sullivan Russell Ortiz
Jenkins Gutierrez Perry Butler Barnes Fisher
"""

names = names.split()
random.shuffle(names)
surnames = surnames.split()
random.shuffle(surnames)

def generate():
    for name, surname in zip(names, surnames):
        username = '%s_%s' % (name.lower(), surname.lower())
        u = User.objects.create(
            username=username,
            first_name=name,
            last_name=surname,
            is_active=True,
            is_superuser=False,
            is_staff=False,
            email='%s@example.com' % (username,),
            password='sha1$58ab4$c80250ca3c0e27ab651ab1f76411ce1418742d25' #password=123
        )
        print "Created User %s" % unicode(u)
    u = User.objects.create(
        username='admin',
        first_name='Admin',
        last_name='Admin',
        is_active=True,
        is_superuser=True,
        is_staff=True,
        email='admin@example.com',
        password='sha1$58ab4$c80250ca3c0e27ab651ab1f76411ce1418742d25' #password=123
    )
    print "Created Admin User"

if __name__ == "__main__":
    generate()