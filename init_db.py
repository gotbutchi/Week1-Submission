from app import db, User, Project, Vote
# Create all the tables
db.create_all()

# create Projects
education = Project(name='Gift an education...Make a life !')
health = Project(name='Less Privileged Elders Need Care & Meal Support')

# add projects to session
db.session.add(education)
db.session.add(health)

# commit the projects to database
db.session.commit()

