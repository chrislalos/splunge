import contextlib
import io
import types

from .EnrichedModule import EnrichedModuleResult
# from .HttpEnricher import HttpEnricher
from .Xgi import Xgi
from . import loggin, util

def exec_module(mod: types.ModuleType, xgi: Xgi):
    mod = util.enrich_module(mod, xgi)

    # use the module spec's loader to execute the module in a stdout-capturing context
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        loggin.debug(f'Before: mod.http={mod.http}')
        mod.__spec__.loader.exec_module(mod)
        loggin.debug(f'After: mod.http={mod.http}')

    # get the context + templateString from the module
    context = get_context(mod)
    templateString = get_template_string(mod)

    # create + return the result object
    result = EnrichedModuleResult(
        headers=mod.http.headers,
        statusCode=mod.http.statusCode,
        statusMessage=mod.http.statusMessage,
        stdout=stdout,
        context=context,
        templateString=templateString
    )
    return result

def get_context(mod):
    attrs = util.get_module_attrs(mod)
    # attrs.pop('http', None)
    attrs.pop('_', None)
    return attrs


def get_template_string(mod):
    attrs = util.get_module_attrs(mod)
    templateString = attrs.pop('_', None)
    return templateString

