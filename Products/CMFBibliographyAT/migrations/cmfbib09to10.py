# Zope imports

# Archetypes import

# Product imports
from Products.CMFCore.utils import getToolByName

class Migration(object):
    """Migrate from 0.9 to 1.0

    It *must* be safe to use this multiple times as it is run automatically
    upon (re)install in the portal_quickinstaller.
    """

    def __init__(self, site, out):
        self.site = site
        self.out = out
        #self.catalog = getToolByName(self.site, 'portal_catalog')

    def migrate(self):
        """Run migration on site object passed to __init__.
        """
        print >> self.out
        print >> self.out, u"Migrating CMFBibliographyAT 0.9 -> 1.0"
        bibtool = getToolByName(self.site, 'portal_bibliography')
        self.migrateTool(bibtool)

    def migrateTool(self, bibtool):
        """Migrate the bibtool.
        """
        # Check for and add a persistent dictionary to keep track of
        # registered reference types on the tool.
        print >> self.out, u'BibliographyTool migration:'
        print >> self.out, u'---------------------------'
        persistent_components = ['Renderers']
        REMOVED_COMPONENT = False
        for pcid in persistent_components:
            if pcid in bibtool.objectIds():
                msg = u"    Remove the persistent '%s' object." % pcid
                print >> self.out, msg
                bibtool._delObject(pcid)
                REMOVED_COMPONENT = True
        if not REMOVED_COMPONENT:
            print >> self.out, u'    Tool is up-to-date'
        print >> self.out


