## Controller Python Script "prefs_bibliography_duplicates"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure the Bibliography Tool

from Products.CMFBibliographyAT import CMFBibMessageFactory as _

REQUEST=context.REQUEST

BIBFOLDER_TYPES = context.portal_bibliography.getBibFolderTypes()

criteria_object = None
if context.portal_type in BIBFOLDER_TYPES:
    criteria_object = context

try:
    for ref_type in context.portal_bibliography.getReferenceTypes():
        REQUEST.set('%s_reference_type' % ref_type, 1)
    criteria_object.manage_changeCriteria(REQUEST)
    context.plone_utils.addPortalMessage(_(u'bibliography_tool_updated_criteriamanager',
                                           default=u'Updated Bibliography Settings - Duplicates Criteria Manager.'))
    return state.set(context=context)
except:
    context.plone_utils.addPortalMessage(_(u'bibliography_tool_update_criteriamanager_failed',
                                           default=u'Updated Bibliography Settings - Failure in update of Duplicates Criteria Manager.'))
    return state.set(context=context)

