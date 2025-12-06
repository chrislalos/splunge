from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from _typeshed.wsgi import WSGIEnvironment

@dataclass
class Xwsgi:
	wsgi: "WSGIEnvironment"

	def __getattr__ (self, name):
		return getattr(self.wsgi, name)

	def __getitem__ (self, key):
		return self.wsgi[key]
	