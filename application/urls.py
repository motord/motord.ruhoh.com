"""
urls.py

URL dispatch route mappings and error handlers

"""

from flask import render_template

from application import app
from application import views


## URL dispatch rules
# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'warmup', view_func=views.warmup)

# Examples list page
app.add_url_rule('/api/', 'read', view_func=views.read, methods=['GET'])
app.add_url_rule('/api/', 'create', view_func=views.create, methods=['POST'])
app.add_url_rule('/api/<int:id>', 'update', view_func=views.update, methods=['PUT'])
app.add_url_rule('/api/<int:id>', 'delete', view_func=views.delete, methods=['DELETE'])

app.add_url_rule('/api/authorize', 'authorize', view_func=views.authorize, methods=['GET'])
app.add_url_rule('/api/authorize', 'authorization_request', view_func=views.authorization_request, methods=['POST'])
# Contrived admin-only view example
app.add_url_rule('/admin_only', 'admin_only', view_func=views.admin_only)

app.add_url_rule('/api/tickets', 'read_tickets', view_func=views.read_tickets, methods=['GET'])
app.add_url_rule('/api/tickets/<int:id>', 'update_tickets', view_func=views.update_tickets, methods=['PUT'])

app.add_url_rule('/api/tasks.json', 'read_tasks', view_func=views.read_tasks, methods=['GET'])
## Error handlers
## Handle 404 errors
#@app.errorhandler(404)
#def page_not_found(e):
#    return render_template('404.html'), 404
#
## Handle 500 errors
#@app.errorhandler(500)
#def server_error(e):
#    return render_template('500.html'), 500

