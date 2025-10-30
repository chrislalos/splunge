<html>
<body>
sport = {{name}}
<table>
	<tr> <td>+</td> <td><form action='addTeam' method='post'><input name='name'/><input type='submit'/></form></td> </tr>
	{% for team in teams %}
	<tr> <td></td> <td><a href='team?name={{team}}'>{{team}}</a></td> </tr>
	{% endfor %}
</table>
</body>
</html>
