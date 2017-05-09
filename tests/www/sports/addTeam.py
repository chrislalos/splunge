### Check to see if the session exists ... if not we will be dead later but we need to make it
#
# If session is not set
#   create session id
#   create session map
#   globalSessionMap[sessionId] = session
#   setCookie('SESS', sessionId)
#
### Check to see if the sport (our dependency) is set. If not push the 'goto' onto the stack
#
# if not session['sport']:
#   pushOnToStack(thisUrl)   <--- Figure out how to make this work
#   redirect('chooseSport')
#
# sport = session['sport']
#
# Redirect to template, which will have the form to add a team
