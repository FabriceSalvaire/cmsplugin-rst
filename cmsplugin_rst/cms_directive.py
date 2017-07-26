# -*- coding: utf-8 -*-

####################################################################################################

from docutils import nodes
from docutils.parsers.rst import directives, Directive

####################################################################################################

class CmsDirective(Directive):

    """
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    # option_spec = dict([(key, directives.flag) for key in VARIANTS])
    has_content = True

    ##############################################

    def run(self):

        print('CmsDirective', type(self), dir(self))
        print('CmsDirective', type(self.state_machine), dir(self.state_machine))
        s = self.state_machine.get_source(0)
        print('CmsDirective', s, type(s), dir(s))
        print('CmsDirective', type(self.state_machine.document), dir(self.state_machine.document))
        return [nodes.raw('',  '', format='html')]

####################################################################################################

directives.register_directive('cms', CmsDirective)
