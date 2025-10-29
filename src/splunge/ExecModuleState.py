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
# If a module does not write to stdout or set `_`, then its output comprises
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
#       variables, and shortcut (_) to override module variables. The biggest issue
#       could be dealing with cases where the output isn't actually Jinja
#       but contains Jinja tokens.
# @note As an alternative to always treating stdout as Jinja, Jinja rendering
#       could be added as a module extra. If the user wants dynamic Jinja they
#       can simply generate it with the module extra. This checks a lot of
#       boxes and avoids ambiguity. Then stdout is just stdout.
#       The idea of letting splunge interpret a template and data collection
#       from module execution is appealing and might provide a nice
#       abstraction, but ambiguity is a high price to pay.
# @note None of this even considers what happens when a .py file has an
#       associcated .pyp Jinja template. In this case any data resulting from
#       module execution is passed to the Jinja template which is then
#       executed. Whatever I dedide, the .pyp case(s) needs tobe handled too.
# @note Based on the above, here is a proposal
#       - stdout is stdout. if it exists, use it to render the data
#       - _ is an explicit dict of args to use as output
#         * if a .pyp exists, execute it it as a jinja template and pass it _
#         * if no .pyp exists, output _ as a simple table or JSON
#       - no stdout and no _ means use the collection of new module attributes
#         exactly as youd use _
#         * if a .pyp exists, execute it it as a jinja template and pass it the attrs 
#         * if no .pyp exists, output the attrs as a simple table or JSON
# @note This might imply that ExecModuleState is really just a (string, dict)
#       tuple, where the string (if present) is stdout and the dict (if present)
#       is the output data context. Maybe I don't need a class
# @note This proposal actually supports the nice feature of 'infer the template 
#       and context from the result of module execution'. If a .pyp exists,
#       it's the inferred template. If _ exists, it's the context. Otherwise
#       module attributes are the context. The only thing unsupported is 
#       dynamically generating a template and setting it to stdout to be
#       inferred as a template by the runtime. That's ok, because dynamic
#       Jinja is supported by a module extra. The user is already doing the 
#       work. They'll have to make an additional module_extra call to explicitly
#       generate Jinja output. This is an acceptable requirement.
class ExecModuleState:
	def __init__ (self):
		self.args = None
		self.shortcut = False
		self.stdout = None

