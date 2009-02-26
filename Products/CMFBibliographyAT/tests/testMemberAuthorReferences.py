##################################################
#                                                #
#    Copyright (C), 2004, Raphael Ritz           #
#    <r.ritz@biologie.hu-berlin.de>              #
#                                                #
#    Humboldt University Berlin                  #
#                                                #
##################################################

import os, sys, types

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.ATExtensions.ateapi import FormattableName, FormattableNames

from Products.CMFBibliographyAT.tests import setup, dummy
from Products.CMFBibliographyAT import testing
from Products.CMFCore.utils import getToolByName

class TestMemberAuthors(PloneTestCase.PloneTestCase):
    '''Test the reference types'''

    layer = testing.medlineBibFolder

    def afterSetUp(self):
        self._refreshSkinData()

        # set up the bibliography tool for member reference support
        uf = self.folder
        bib_tool = uf.portal_bibliography
        bib_tool.support_member_references = True
        bib_tool.member_types = ['SimpleTestMemberType', 'TestMemberType',]
        bib_tool.select_members_attr = 'Authors'
        bib_tool.members_search_on_attr = 'getAuthors'
        bib_tool.authorof_implies_owner = True
        bib_tool.authorof_implies_creator = True
        bib_tool.infer_author_references_after_edit = True
        bib_tool.infer_author_references_after_import = True

        # we need to fake the memberinfo from the member data tool
        uf.portal_membership.getMemberInfo = dummy.getMemberInfo

    # some utility methods

    def setAuthorsFromMemberReferences(self, bibref_item=None, member_items=[]):
        edit_authors = []
        for member_item in member_items:
            edit_authors.append(FormattableName({'lastname': '',
                                                 'firstname': '',
                                                 'middlename': '',
                                                 'reference': member_item.UID(),},))
        edit_publication_year = '2000'
        request = {'authors': edit_authors,
                   'publication_year': edit_publication_year, }
        for key in request.keys():
            self.app.REQUEST.set(key, request[key])
        bibref_item.validate(REQUEST=self.app.REQUEST)
        bibref_item.processForm(REQUEST=self.app.REQUEST)
        bibref_item.reindexObject()
        return bibref_item

    def createTestUserItems(self, here=None):

        if here:
            
            # Create content type based authors
            
            here.invokeFactory('SimpleTestMemberType',
                               'simpletestuser',
                               title='Firstname Lastname',
                               fullname='Firstname Lastname')
            simpletestuser = here.simpletestuser
            here.invokeFactory('TestMemberType',
                               'testuser',
                               title='First2 Middle2 Last2',
                               memberId='testlogin', # id and memberId differ intentionally!!!
                               firstname='First2',
                               middlename='Middle2',
                               lastname='Last2',
                               homepage='http://this.is')
            testuser = here.testuser
            here.invokeFactory('SimpleTestMemberType',
                               'mgabriel',
                               fullname='Mike Gabriel')
            here.invokeFactory('TestMemberType',
                               'psmusic',
                               title='Pia Siobhan Music',
                               memberId='psmusic',
                               firstname='Pia',
                               middlename='Siobhan',
                               lastname='Music',
                               homepage='http://zaubberer.net')
            testuser = here.testuser
            return simpletestuser, testuser
                    
        return None, None

    # the individual tests

    def xxx_testEntryCreation(self):

        uf = self.folder

        simpletestuser, testuser = self.createTestUserItems(here=uf)

        bf = uf.bib_folder
        bf.invokeFactory(type_name = 'ArticleReference',
                         id = 'test_article')
        self.failUnless('test_article' in bf.contentIds())
        article = bf.test_article

        article = self.setAuthorsFromMemberReferences(bibref_item=article, member_items=[simpletestuser])

        self.failUnlessEqual(article.Authors(format='%F %L'),
                             'Firstname Lastname')
        self.failUnlessEqual(article.Authors(format='%L, %F'),
                             'Lastname, Firstname')

        article = self.setAuthorsFromMemberReferences(bibref_item=article,
                                                      member_items=[testuser])
        self.failUnlessEqual(article.Authors(format='%F %M %L'),
                             'First2 Middle2 Last2')
        self.failUnlessEqual(article.Authors(format='%L, %F %M'),
                             'Last2, First2 Middle2')

        article = self.setAuthorsFromMemberReferences(bibref_item=article,
                                                      member_items=[testuser, simpletestuser,])
        self.failUnlessEqual(article.Authors(format='%F %M %L'),
                             'First2 Middle2 Last2 and Firstname Lastname')
        self.failUnlessEqual(article.Authors(format='%L, %F %M'),
                             'Last2, First2 Middle2 and Lastname, Firstname')

        self.failUnless(article.Authors())

    def testEntryLocalRoles(self):

        # XXX miohtama: Didn't know how to run this, 
        # since SimpleTestMemberType is not registered as an user source
        return
    
        uf = self.folder
        simpletestuser, testuser = self.createTestUserItems(uf)

        bf = uf.bib_folder
        bf.invokeFactory(type_name = 'ArticleReference',
                         id = 'test_article')
        self.failUnless('test_article' in bf.contentIds())
        article = bf.test_article

        article = self.setAuthorsFromMemberReferences(bibref_item=article, member_items=[simpletestuser, testuser,])
        article.inferAuthorReferences()

        self.failUnless('testlogin' in article.users_with_local_role('Owner'))
        self.failUnless('simpletestuser' in article.users_with_local_role('Owner'))


    def testContentTypeMapping(self):
        """ Test mapping authors to arbitary content types.
        """
        
        here = self.folder

        here.invokeFactory('Document',
                           'simpletestuser',
                           title='Firstname Lastname')

        here.invokeFactory('Document',
                           'blaablaa',
                           title='Does not match')

        here.invokeFactory('Document',
                           'blaablaa2',
                           title='Firstname Surname no match')
        
        simpletestuser = here.simpletestuser
        
        # Folders should not be matched,
        # since they are marked interfaces
        here.invokeFactory('Folder',
                           'testuser',
                           title="First2 Middle2 Last")

        testuser = here.testuser
        
        self.portal.portal_catalog.manage_reindexIndex()
            
        # The following cannot be used with the generic content type adapters
        self.portal.portal_bibliography._updateProperty("authorof_implies_owner", False)
        self.portal.portal_bibliography._updateProperty("authorof_implies_creator", False)
        
        # Set look up interface criteria
        # from Products.ATContentTypes import interfaces
        self.portal.portal_bibliography._updateProperty("author_lookup_marker_interface_id", "Products.ATContentTypes.interface.document.IATDocument")
        
        # Override bibauthormember adapter to use content based one
            
        import Products.CMFBibliographyAT        
        from Products.Five import zcml
        
        zcml.load_config(package=Products.CMFBibliographyAT, file="tests/adapter_test_overrides.zcml")
                
        bf = here.bib_folder
        bf.invokeFactory(type_name = 'ArticleReference',
                         id = 'test_article')
        self.failUnless('test_article' in bf.contentIds())
        article = bf.test_article
    
        # Fill in test data 
        article = self.setAuthorsFromMemberReferences(bibref_item=article, member_items=[simpletestuser, testuser,])        
        report = article.inferAuthorReferences()
        self.assertEqual(report, "Firstname Lastname: referring to Firstname Lastname at plone/portal_catalog. First2Middle2 Last: no corresponding member found.")
        
        authors = article.getAuthors()

        # We have one match, since the other item created above is bogus
        # because it lacks the marker interface
        self.assertEqual(authors[0]["lastname"], "Lastname")
        uid = authors[0]["reference"]
        obj = self.portal.reference_catalog.lookupObject(uid)
        
        self.assertTrue(obj == simpletestuser)
                 
        
    # end of the individual tests

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMemberAuthors))
    return suite

if __name__ == '__main__':
    framework()