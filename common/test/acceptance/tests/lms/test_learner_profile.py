# -*- coding: utf-8 -*-
"""
End-to-end tests for Student's Profile Page.
"""

from ...pages.lms.auto_auth import AutoAuthPage
from ...pages.lms.learner_profile import LearnerProfilePage
from ...pages.lms.dashboard import DashboardPage

from bok_choy.web_app_test import WebAppTest


class LearnerProfilePageTest(WebAppTest):
    """
    Tests that verify Student's Profile Page.
    """

    USER_1_NAME = 'user1'
    USER_1_EMAIL = 'user1@edx.org'
    USER_2_NAME = 'user2'
    USER_2_EMAIL = 'user2@edx.org'

    MY_USER = 1
    OTHER_USER = 2

    PRIVACY_PUBLIC = 'all_users'
    PRIVACY_PRIVATE = 'private'

    PUBLIC_PROFILE_FIELDS = ['username', 'country', 'language', 'bio']
    PRIVATE_PROFILE_FIELDS = ['username']

    PUBLIC_PROFILE_EDITABLE_FIELDS = ['country', 'language', 'bio']

    def setUp(self):
        """
        Initialize pages.
        """
        super(LearnerProfilePageTest, self).setUp()
        self.dashboard_page = DashboardPage(self.browser)

        self.my_auto_auth_page = AutoAuthPage(self.browser, username=self.USER_1_NAME, email=self.USER_1_EMAIL).visit()
        self.my_profile_page = LearnerProfilePage(self.browser, self.USER_1_NAME)

        self.other_auto_auth_page = AutoAuthPage(
            self.browser,
            username=self.USER_2_NAME,
            email=self.USER_2_EMAIL
        ).visit()

        self.other_profile_page = LearnerProfilePage(self.browser, self.USER_2_NAME)

    def authenticate_as_user(self, user):
        """
        Auto authenticate a user.
        """
        if user == self.MY_USER:
            self.my_auto_auth_page.visit()
        elif user == self.OTHER_USER:
            self.other_auto_auth_page.visit()

    def set_pubilc_profile_fields_data(self, profile_page):
        """
        Fill in the public profile fields of a user.
        """
        profile_page.language('English')
        profile_page.country('United Kingdom')
        profile_page.aboutme('Nothing Special')

    def visit_my_profile_page(self, user, privacy=None):
        """
        Visits a users profile page.
        """
        self.authenticate_as_user(user)
        self.my_profile_page.visit()
        self.my_profile_page.wait_for_page()

        if user is self.MY_USER and privacy is not None:
            self.my_profile_page.privacy = privacy

            if privacy == self.PRIVACY_PUBLIC:
                self.set_pubilc_profile_fields_data(self.my_profile_page)

    def visit_other_profile_page(self, user, privacy=None):
        """
        Visits a users profile page.
        """
        self.authenticate_as_user(user)
        self.other_profile_page.visit()
        self.other_profile_page.wait_for_page()

        if user is self.OTHER_USER and privacy is not None:
            self.other_profile_page.privacy = privacy

            if privacy == self.PRIVACY_PUBLIC:
                self.set_pubilc_profile_fields_data(self.other_profile_page)

    def test_dashboard_learner_profile_link(self):
        """
        Scenario: Verify that my profile link is present on dashboard page and we can navigate to correct page.

        Given that I am a registered user.
        When I go to Dashboard page.
        And I click on username dropdown.
        Then I see My Profile link in the dropdown menu.
        When I click on My Profile link.
        Then I will be navigated to My Profile page.
        """
        self.dashboard_page.visit()
        self.dashboard_page.click_username_dropdown()
        self.assertTrue('My Profile' in self.dashboard_page.username_dropdown_link_text)
        self.dashboard_page.click_my_profile_link()
        self.my_profile_page.wait_for_page()

    def test_fields_on_my_private_profile(self):
        """
        Scenario: Verify that desired fields are shown when looking at her own private profile.

        Given that I am a registered user.
        And I visit My Profile page.
        And I set the profile visibility to private.
        And I reload the page.
        Then I should see the profile visibility selector dropdown.
        Then I see some of the profile fields are shown.
        """
        self.visit_my_profile_page(self.MY_USER, privacy=self.PRIVACY_PRIVATE)

        self.assertTrue(self.my_profile_page.privacy_field_visible)
        self.assertEqual(self.my_profile_page.visible_fields, self.PRIVATE_PROFILE_FIELDS)

    def test_fields_on_my_public_profile(self):
        """
        Scenario: Verify that desired fields are shown when looking at her own public profile.

        Given that I am a registered user.
        And I visit My Profile page.
        And I set the profile visibility to public.
        And I reload the page.
        Then I should see the profile visibility selector dropdown.
        Then I see all the profile fields are shown.
        And `location`, `language` and `about me` fields are editable.
        """
        self.visit_my_profile_page(self.MY_USER, privacy=self.PRIVACY_PUBLIC)

        self.assertTrue(self.my_profile_page.privacy_field_visible)
        self.assertEqual(self.my_profile_page.visible_fields, self.PUBLIC_PROFILE_FIELDS)

        self.assertEqual(self.my_profile_page.editable_fields, self.PUBLIC_PROFILE_EDITABLE_FIELDS)

    def test_fields_on_others_private_profile(self):
        """
        Scenario: Verify that desired fields are shown when looking at her own private profile.

        Given that I am a registered user.
        And I visit My Profile page.
        And I set the profile visibility to private.
        And I reload the page.
        Then I shouldn't see the profile visibility selector dropdown.
        Then I see some of the profile fields are shown.
        """
        self.visit_other_profile_page(self.OTHER_USER, privacy=self.PRIVACY_PRIVATE)
        self.visit_other_profile_page(self.MY_USER)

        self.assertFalse(self.other_profile_page.privacy_field_visible)
        self.assertEqual(self.other_profile_page.visible_fields, self.PRIVATE_PROFILE_FIELDS)

    def test_fields_on_others_public_profile(self):
        """
        Scenario: Verify that desired fields are shown when looking at her own public profile.

        Given that I am a registered user.
        And I visit My Profile page.
        And I set the profile visibility to public.
        And I reload the page.
        Then I shouldn't see the profile visibility selector dropdown.
        Then I see all the profile fields are shown.
        Also `location`, `language` and `about me` fields are not editable.
        """
        self.visit_other_profile_page(self.OTHER_USER, privacy=self.PRIVACY_PUBLIC)
        self.visit_other_profile_page(self.MY_USER)

        self.assertFalse(self.other_profile_page.privacy_field_visible)

        # We are excluding language field from verification because when a usr view another users profile,
        # server send `languages` field in model instead of `language`, due to which language field will not be shown
        # Until this is fixed on server side, we will exclude the language fields.
        fields_to_check = self.PUBLIC_PROFILE_FIELDS[0:2] + self.PUBLIC_PROFILE_FIELDS[3:]
        self.assertEqual(self.other_profile_page.visible_fields, fields_to_check)

        self.assertEqual(self.my_profile_page.editable_fields, [])

    def _test_dropdown_field(self, field_id, new_value, displayed_value, mode):
        """
        Test behaviour of a dropdown field.
        """
        self.visit_my_profile_page(self.MY_USER, privacy=self.PRIVACY_PUBLIC)

        self.my_profile_page.value_for_dropdown_field(field_id, new_value)
        self.assertEqual(self.my_profile_page.get_non_editable_mode_value(field_id), displayed_value)
        self.assertTrue(self.my_profile_page.mode_for_field(field_id), mode)

        self.browser.refresh()
        self.my_profile_page.wait_for_page()

        self.assertEqual(self.my_profile_page.get_non_editable_mode_value(field_id), displayed_value)
        self.assertTrue(self.my_profile_page.mode_for_field(field_id), mode)

    def _test_textarea_field(self, field_id, new_value, displayed_value, mode):
        """
        Test behaviour of a textarea field.
        """
        self.visit_my_profile_page(self.MY_USER, privacy=self.PRIVACY_PUBLIC)

        self.my_profile_page.value_for_textarea_field(field_id, new_value)
        self.assertEqual(self.my_profile_page.get_non_editable_mode_value(field_id), displayed_value)
        self.assertTrue(self.my_profile_page.mode_for_field(field_id), mode)

        self.browser.refresh()
        self.my_profile_page.wait_for_page()

        self.assertEqual(self.my_profile_page.get_non_editable_mode_value(field_id), displayed_value)
        self.assertTrue(self.my_profile_page.mode_for_field(field_id), mode)

    def test_country_field(self):
        """
        Test behaviour of `Country` field.
        """
        self._test_dropdown_field('country', 'Pakistan', 'Pakistan', 'display')

        self.my_profile_page.make_field_editable('country')
        self.assertTrue(self.my_profile_page.mode_for_field('country'), 'edit')

        self.assertTrue(self.my_profile_page.field_icon_present('country'))

    def test_language_field(self):
        """
        Test behaviour of `Language` field.
        """
        self._test_dropdown_field('language', 'Urdu', 'Urdu', 'display')
        self._test_dropdown_field('language', '', 'Add language', 'placeholder')

        self.my_profile_page.make_field_editable('language')
        self.assertTrue(self.my_profile_page.mode_for_field('language'), 'edit')

        self.assertTrue(self.my_profile_page.field_icon_present('language'))

    def test_aboutme_field(self):
        """
        Test behaviour of `About Me` field.
        """
        placeholder_value = (
            "Tell other edX learners a little about yourself: where you live, what your interests are, "
            "why you're taking courses on edX, or what you hope to learn."
        )

        self._test_textarea_field('bio', 'Eat Sleep Code', 'Eat Sleep Code', 'display')
        self._test_textarea_field('bio', '', placeholder_value, 'placeholder')

        self.my_profile_page.make_field_editable('bio')
        self.assertTrue(self.my_profile_page.mode_for_field('bio'), 'edit')
