################################################################################
#
# splunge has fancy rules about the output of a module
#
# If a module writes to stdout, eg with `print()`, then that's the output of 
# the module. Noting else matters - writing to stdout is an explicit
# declaration of intent, of saying "this is what I want the output to be".
#
# If a module doesn't write to stdout, but does assign a Jinja template string 
# to the variable `_`, then _ is used to render a Jinja template. The data for
# the template is a dictionary of module level variables set during execution
# of the module. Currently there's no way to explicitly set that data.
#
# If a module does not write to stdout or set `_`, then its output comprisea
# `name=value` pairs for all module-level variables set during the module's
# execution. The is the base case. splunge is designed to do the right thing
# and be useful even/especially with this base case.
# 
# `ExecModuleState` has fields to support all these scenarios.
#    args	  The module-level variables assigned during module execution
#    shortcut The value assigned to `_`, if any
#    stdout   The output written to stdout, if any
#
# Module execution returns an ExecModuleState object. 
# Module rendering consumes an ExecModuleState object.
#
# @note I actually thought that the point of _ was to override args and allow
#       explicitly setting the module level variables. This could be very 
#       useful. For one it would support generators and lazy-loading.
# @note A more intuitive use of stdout might be to use stdout as a Jinja
#       template, especially since Jinja templates tend to fallback nicely to
#       plain text if the user doesn't actually want Jinja. This could be very
#       useful. For one it would support dynamic templates, which might 
#       otherwise be impossible or require hero Jinja.
# @note These two ideas can be combined: use stdout for Jinja, args for module
#       variables, and shortcut to override module variables. The biggest issue
#       could be dealing with cases where the output isn't actually Jinja
#       but contains Jinja tokens.
# @note As an alternative to always treating stdout as Jinja, Jinja rendering
#       could be added as a module extra. If the user wants dynamic Jinja they
#       can simply generate it with the module extra. This checks a lot of
#       boxes and avoids ambiguity.
#       The idea of letting splunge interpret a template and data collection
#       from module execution is appealing and might provide a nice
#       abstraction, but ambiguity is a high price to pay.
# @note None of this even considers what happens when a .py file has an
#       associcated .pyp Jinja template. In this case any data resulting from
#       module execution is passed to the Jinja template which is then
#       executed. Whatever I dedide, the .pyp case(s) needs tobe handled too.
class ExecModuleState:
	def __init__ (self):
		self.args = None
		self.shortcut = False
		self.stdout = None

