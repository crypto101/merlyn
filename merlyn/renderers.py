"""
Step renderers.
"""
from axiom import attributes, item
from merlyn.interfaces import IRenderer
from zope.interface import implementer


@implementer(IRenderer)
class StringTemplateRenderer(item.Item):
    """
    A renderer which will render a str.format-style template with a context.
    """
    template = attributes.text(allowNone=False)
    context = attributes.reference()


    def render(self, _userStore):
        """
        Formats the template using the context.
        """
        kwargs = dict.fromkeys(["c", "ctx", "context"], self.context)
        return self.template.format(**kwargs)
