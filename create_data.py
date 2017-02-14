from app import db, create_app
from app.external_apis import get_geocode_location
from app.models import User, Request, Proposal, Date

# create app and load context
app = create_app('development')
app_context = app.app_context()
app_context.push()

# empty all tables
db.drop_all()
db.create_all()

# add users
jack = User(username='jack', password='test', email='jack@example.com')
db.session.add(jack)
jill = User(username='jill', password='test', email='jill@example.com')
db.session.add(jill)
db.session.commit()

# add request: jack makes a meal request
location_string = 'amsterdam, europaplein'
latitude, longitude = get_geocode_location(location_string)

request = Request(user_id=jack.id, meal_type='sushi', meal_time='dinner',
                  location_string=location_string, latitude=latitude,
                  longitude=longitude, filled=False)
db.session.add(request)
db.session.commit()

# add proposal: jill proposes to jack
proposal = Proposal(user_proposed_from=jill.id, user_proposed_to=jack.id, 
                    request_id=request.id, filled=False)
db.session.add(proposal)
db.session.add(proposal)
db.session.commit()

# add date: jack agrees agrees to jill's proposal

print("Initial data created!")