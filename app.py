#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#



import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for, jsonify
import logging
from logging import Formatter, FileHandler
from forms import *
from settings import app, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#




#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
   __tablename__ = 'show'

   venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
   artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
   start_time = db.Column(db.DateTime, default=datetime.today(), primary_key=True)
   artist = db.relationship("Artist", back_populates="show_artist")
   venue = db.relationship("Venue", back_populates="show_venue")


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show_venue = db.relationship('Show', back_populates="venue")

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show_artist = db.relationship('Show', back_populates='artist')

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  results  = Venue.query.with_entities(Venue.city,Venue.state).distinct().all()

  for result in results:
    venues = []
    venueslists = Venue.query.filter_by(city=result.city,state=result.state).all()

    for venue in venueslists:
        shows = Show.query.filter_by(venue_id=venue.id).all()
        num_upcoming_shows = len(shows)

        venues.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows,
        })
      

    data.append({
       "city": result.city,
       "state": result.state,
       "venues": venues
    })
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search_term=request.form.get('search_term', '')

  data = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  response={
    "count": data.count(),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).all()[0]
  shows = Show.query.filter_by(venue_id=venue_id).all()

  past_shows = []
  upcoming_shows = []
  current_date = datetime.now()

  for show in shows:
    result = {
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
    }
  
    upcoming_shows.append(result) if show.start_time > current_date else past_shows.append(result)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try:
    def form_get(name):
      return request.form.get(name)
    name = form_get('name')
    city = form_get('city')
    state = form_get('state')
    address = form_get('address')
    phone = form_get('phone')
    genres = request.form.getlist('genres')
    facebook_link = form_get('facebook_link')
    image_link = form_get('image_link')
    website_link = form_get('website_link')
    seeking_talent = True if form_get('seeking_talent')=='y' else False
    seeking_description = form_get('seeking_description')
    
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, \
                 facebook_link=facebook_link, image_link=image_link, website_link=website_link, \
                  seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + name + ' was successfully listed!')
  except:
     db.session.rollback()
     flash('An error occured. Venue ' + name + ' could not be listed.')
  finally:
     db.session.close()
     return render_template('pages/home.html')

  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Show.query.filter_by(venue_id=venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
     data.append({
        "id": artist.id,
        "name": artist.name,
     })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  response={
    "count": data.count(),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).all()[0]
  shows = Show.query.filter_by(artist_id=artist_id).all()
  past_shows = []
  upcoming_shows = []
  current_date = datetime.now()

  for show in shows:
     result = {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": format_datetime(str(show.start_time))
     }
  
  upcoming_shows.append(result) if show.start_time > current_date else past_shows.append(result)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = db.session.get(Artist, artist_id)
  
  data = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "genres": artist.genres,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
  }

  form = ArtistForm(name=artist.name, city=artist.city, state=artist.state, phone = artist.phone,
    genres = artist.genres, facebook_link = artist.facebook_link, image_link = artist.image_link,
    website_link = artist.website_link, seeking_venue = artist.seeking_venue,
    seeking_description = artist.seeking_description)

  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    def form_get(name):
       return request.form.get(name)
    artist.name = form_get('name')
    artist.city = form_get('city')
    artist.state = form_get('state')
    artist.phone = form_get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = form_get('facebook_link')
    artist.image_link = form_get('image_link')
    artist.website_link = form_get('website_link')
    artist.seeking_venue = form_get('seeking_venue')
    artist.seeking_description = form_get('seeking_description')

    db.session.commit()
    flash("Artist " + artist.name + " was successfully updated.")
  except:
     db.session.rollback()
     flash("An error occured. Artist " + artist.name + " could not be updated")
  finally:
     db.session.close()
     return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = db.session.get(Venue, venue_id)

  data ={
    "id": venue.id,
    "name": venue.name,
    "city": venue.city,
    "state": venue.state,
    "genres": venue.genres,
    "address": venue.address,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "image_link": venue.image_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
  }
  form = VenueForm(name=venue.name, city=venue.name, state=venue.state,
    genres=venue.genres, address=venue.genres, phone=venue.phone,
    website=venue.website_link, facebook_link=venue.facebook_link,
    seeking_talent=venue.seeking_talent, seeking_description=venue.seeking_description,
    image_link=venue.image_link)
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    def form_get(name):
       return request.form.get(name)
    
    venue.name = form_get('name')
    venue.city = form_get('city')
    venue.state = form_get('state')
    venue.genres = request.form.getlist('genres')
    venue.address = form_get('address')
    venue.phone = form_get('phone')
    venue.website_link = form_get('website_link')
    venue.facebook_link = form_get('facebook_link')
    venue.image_link = form_get('image_link')
    venue.seeking_venue = form_get('seeking_venue')
    venue.seeking_description = form_get('seeking_description')

    db.session.commit()
    flash("Venue " + venue.name + " was successfully updated.")
  except:
    db.session.rollback()
    flash("An error occured. Venue " + venue.name + " could not be updated")
  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form

  try:
    def form_get(name):
        return request.form.get(name)
    name = form_get('name')
    city = form_get('city')
    state = form_get('state')
    genres = request.form.getlist('genres')
    facebook_link = form_get('facebook_link')
    image_link = form_get('image_link')
    website_link = form_get('website_link')
    seeking_venue =  True if form_get('seeking_talent')=='y' else False
    seeking_description = form_get('seeking_description')

    artist = Artist(name=name, city=city, state=state, genres=genres, facebook_link=facebook_link, \
      image_link=image_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + name + ' was successfully listed!')
  except Exception as exc:
    db.session.rollback()
    print(exc)
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  finally:
    db.session.close()
    return render_template('pages/home.html')
    


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
     data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
     })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False

  try:
    def form_get(name):
       return request.form.get(name)
    artist_id = form_get('artist_id')
    venue_id = form_get('venue_id')
    start_time = form_get('start_time')
  
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as exc:
    db.session.rollback()
    print(exc)
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
