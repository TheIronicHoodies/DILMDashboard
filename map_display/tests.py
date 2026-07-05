from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import LegislativeDistrict


class MapUpdateTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='secret123')
        self.district = LegislativeDistrict.objects.create(
            legis_dist='District 1',
            collected_signatures=10,
            difficulty='Medium',
            partners='Partner A',
            partner_mobilized=False,
            registered_voters=1000,
        )

    def test_post_updates_existing_district(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('map_display:map_display'),
            {
                'legis_dist': self.district.legis_dist,
                'collected_signatures': 42,
                'difficulty': 'Hard',
                'partners': 'Partner B',
                'partner_mobilized': 'on',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.district.refresh_from_db()
        self.assertEqual(self.district.collected_signatures, 42)
        self.assertEqual(self.district.difficulty, 'Hard')
        self.assertEqual(self.district.partners, 'Partner B')
        self.assertTrue(self.district.partner_mobilized)
