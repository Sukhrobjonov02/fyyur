@app.route('/venues')
def venues():

  data_venues=[]
  results  = Venue.query.with_entities(Venue.city,Venue.state).distinct().all()
  
  for result in results:
    venues=[]
    venuelists = Venue.query.filter_by(city=result.city,state=result.state)
    
    for venue in venuelists:
      venueresults = Show.query.filter_by(venue_id=venue.id).all()
      num_upcoming_shows = len(venueresults)
      
      venues.append({"id":venue.id,"name":venue.name,"num_upcoming_shows":num_upcoming_shows})


@app.route('/venues')
def venues():

  data_venues=[]
  results  = Venue.query.with_entities(Venue.city,Venue.state).distinct().all()
  
  for result in results:
    venues=[]
    venuelists = Venue.query.filter_by(city=result.city,state=result.state)
    
    for venue in venuelists:
      venueresults = Show.query.filter_by(venue_id=venue.id).all()
      num_upcoming_shows = len(venueresults)
      
      venues.append({"id":venue.id,"name":venue.name,"num_upcoming_shows":num_upcoming_shows})

    data_venues.append({"city":result.city,"state":result.state,"venues":venues})

  return render_template('pages/venues.html', areas=data_venues)