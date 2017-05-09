<html>
<body>
<b>Sports</b>
<table>
	<tr> <td>+</td> <td><form action='addSport' method='post'><input name='name'/><input type='submit'></td> </tr>
{% for name in sports %}
	<tr> <td></td> <td><a href='sport?name={{name}}'>{{name}}</a></td> </tr>
{% endfor %}
</table>
</body>
</html>
