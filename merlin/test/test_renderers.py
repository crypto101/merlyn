from axiom import attributes, item
from twisted.trial.unittest import SynchronousTestCase
from merlyn.renderers import StringTemplateRenderer
from merlyn.interfaces import IRenderer
from zope.interface.verify import verifyObject


class StringTemplateRendererTests(SynchronousTestCase):
    """
    Tests for the string template (str.format) based renderer.
    """
    def test_verifyInterface(self):
        """A StringTemplateRenderer implements the IRenderer interface.

        """
        verifyObject(IRenderer, StringTemplateRenderer(template=u"xyzzy"))


    def test_noInterpolation(self):
        """A string template renderer renders a template with no context, as
        long as the template doesn't use the context.

        """
        renderer = StringTemplateRenderer(template=u"xyzzy")
        self.assertEqual(renderer.render(None), u"xyzzy")


    def test_withInterpolation(self):
        """A string template renderer can render a template with a context.

        """
        template = u"{c.value} {c.anotherValue} {c.aThirdValue}"
        context = FakeContext()
        renderer = StringTemplateRenderer(template=template, context=context)
        self.assertEqual(renderer.render(None), u"1 2 3")


    def test_contextName(self):
        """The context is available in the template under c, ctx, and
        context.

        """
        context = FakeContext()
        renderedTemplates = set()

        def render(template):
            renderer = StringTemplateRenderer(template=template, context=context)
            rendered = renderer.render(None)
            renderedTemplates.add(rendered)

        render(u"The value is {c.value}.")
        render(u"The value is {ctx.value}.")
        render(u"The value is {context.value}.")

        self.assertEqual(renderedTemplates, set([u"The value is 1."]))



class FakeContext(item.Item):
    """A fake context, for testing purposes.

    """
    value = attributes.integer(default=1)
    anotherValue = attributes.integer(default=2)
    aThirdValue = attributes.integer(default=3)
