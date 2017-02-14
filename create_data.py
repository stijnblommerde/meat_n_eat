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
stijn = User(username='stijn', password='test', email='stijn@example.com')
db.session.add(stijn)
casper = User(username='casper', password='test', email='casper@example.com')
db.session.add(casper)

# add request
location_string = 'amsterdam'
latitude, longitude = get_geocode_location(location_string)
request = Request(user_id=2, meal_type='pizza', meal_time='lunch',
                  location_string='amsterdam', latitude=latitude,
                  longitude=longitude, filled=False)
db.session.add(request)

# add proposal
# add date

db.session.commit()

print("Initial data created!")