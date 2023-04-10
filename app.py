#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#



import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from forms import *
from settings import app, db
from models import shows_table, Venue, Artist
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#




#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




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
        shows = db.session.query(shows_table).filter_by(venue_id=venue.id).all()
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
  shows = db.session.query(shows_table).filter_by(venue_id=venue_id).all()

  past_shows = []
  upcoming_shows = []
  current_date = datetime.now()

  for show in shows:
    artist = db.session.get(Artist, show.artist_id)
    result = {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
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
    form = VenueForm(request.form)
    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_talent = True if form.seeking_talent=='y' else False,
      seeking_description = form.seeking_description.data,
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue: {0} created successfully'.format(venue.name))
  except Exception as err:
     flash('An error occurred creating the Venue: {0}. Error: {1}'.format(venue.name, err))
     db.session.rollback()
  finally:
     db.session.close()
     return render_template('pages/home.html')

  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    db.session.query(shows_table).filter_by(venue_id=venue_id).delete()
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
  shows = db.session.query(shows_table).filter_by(artist_id=artist_id).all()
  past_shows = []
  upcoming_shows = []
  current_date = datetime.now()

  for show in shows:
     venue = db.session.get(Venue, show.venue_id)
     result = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
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

  form = ArtistForm(
    name=artist.name, 
    city=artist.city, 
    state=artist.state, 
    phone = artist.phone,
    genres = artist.genres, 
    facebook_link = artist.facebook_link, 
    image_link = artist.image_link,
    website_link = artist.website_link, 
    seeking_venue = artist.seeking_venue,
    seeking_description = artist.seeking_description
  )

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
    flash('Artist: {0} updated successfully'.format(artist.name))
  except Exception as err:
     flash('An error occurred updating the Artist: {0}. Error: {1}'.format(artist.name, err))
     db.session.rollback()
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
    flash('Venue: {0} updated successfully'.format(venue.name))
  except Exception as err:
     flash('An error occurred updating the Venue: {0}. Error: {1}'.format(venue.name, err))
     db.session.rollback()
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
    form = ArtistForm(request.form)
    artist = None
    if form.validate_phone(form.phone):
      artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website_link = form.website_link.data,
        seeking_venue =  True if form.seeking_venue.data=='y' else False,
        seeking_description = form.seeking_description.data,
      )
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist: {0} created successfully'.format(artist.name))
    else:
      flash('An error occurred creating the Artist')
  except ValidationError as err:
      flash(f'Validation error creating the Artist: {str(err)}')
      db.session.rollback()
  except Exception as err:
      flash(f'An error occurred creating the Artist: {str(err)}')
      db.session.rollback()
  finally:
      db.session.close()
      return render_template('pages/home.html')
    


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = db.session.query(shows_table).all()
  
  data = []
  for show in shows:
     artist = db.session.get(Artist, show.artist_id)
     venue = db.session.get(Venue, show.venue_id)
     data.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
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

  try:
    form = ShowForm(request.form)
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    artist = Artist.query.filter_by(id=artist_id).all()[0]
    venue = Venue.query.filter_by(id=venue_id).all()[0]
    venue.artists.append(artist)
    db.session.add(venue)
    db.session.commit()
    flash('Show: created successfully')
  except Exception as err:
    db.session.rollback()
    flash('An error occurred creating the Venue. Error: {1}'.format(err))
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
