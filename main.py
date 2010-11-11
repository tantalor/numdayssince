#!/usr/bin/env python

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util, template
from datetime import date, timedelta

class Event(db.Model):
  description = db.StringProperty()
  last_occured = db.DateProperty()
  
  def days_ago(self):
    delta = date.today() - self.last_occured
    if delta.days == 1:
      return "1 day"
    else:
      return "%s days" % delta.days

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write(template.render('default.html', None))
  def post(self):
    description = self.request.get('description')
    days_ago = self.request.get('days_ago')
    if description:
      days_ago_numeric = 0
      if days_ago:
        try:
          days_ago_numeric = int(days_ago)
          if days_ago_numeric < 0:
            raise ValueError()
        except ValueError:
          days_ago_numeric = 0
      try:
        last_occured = date.today() - timedelta(days_ago_numeric)
      except OverflowError:
        last_occured = date.today()
      event = Event(
        description = description,
        last_occured = last_occured
      )
      event.put()
      self.redirect('/%s' % event.key())
    else:
      self.redirect('/')

class DetailHandler(webapp.RequestHandler):
  def get(self, key):
    event = Event.get(key)
    self.response.out.write(template.render('detail.html', dict(event=event)))

class ResetHandler(webapp.RequestHandler):
  def post(self, key):
    event = Event.get(key)
    event.last_occured = date.today()
    event.put()
    self.redirect('/%s' % event.key())

def main():
  application = webapp.WSGIApplication(
    [
      ('/', MainHandler),
      ('/(.*)/reset', ResetHandler),
      ('/(.*)', DetailHandler),
    ],
    debug=True,
  )
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
