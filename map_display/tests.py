import json
import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import LegislativeDistrict
from .views import MapView


class MapUpdateTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='secret123')
        geojson_path = Path(__file__).resolve().parent.parent / 'static' / 'map_coordinates' / 'legis_dists.json'
        with geojson_path.open(encoding='utf-8') as file:
            geojson = json.load(file)
        district_name = geojson['features'][0]['properties']['legis_dist']

        self.district = LegislativeDistrict.objects.create(
            legis_dist=district_name,
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
        self.assertEqual(self.district.collected_signatures, 52)
        self.assertEqual(self.district.difficulty, 'Hard')
        self.assertEqual(self.district.partners, 'Partner B')
        self.assertTrue(self.district.partner_mobilized)

    def test_geojson_file_is_updated_from_database(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('map_display:map_display'),
            {
                'legis_dist': self.district.legis_dist,
                'collected_signatures': 77,
                'difficulty': 'Easy',
                'partners': 'Partner C',
                'partner_mobilized': 'on',
            },
        )

        self.assertContains(response, 'Partner C')

        geojson_path = os.path.join('static', 'map_coordinates', 'legis_dists.geojson')
        self.assertTrue(os.path.exists(geojson_path))

        with open(geojson_path, encoding='utf-8') as file:
            data = json.load(file)

        matching_features = [
            feature for feature in data['features']
            if feature['properties'].get('legis_dist') == self.district.legis_dist
        ]
        self.assertTrue(matching_features)

        properties = matching_features[0]['properties']
        self.assertEqual(properties['collected_signatures'], 87)
        self.assertEqual(properties['difficulty'], 'Easy')
        self.assertEqual(properties['partners'], 'Partner C')
        self.assertTrue(properties['partner_mobilized'])

    def test_compute_fill_style_uses_saved_district_values(self):
        self.district.collected_signatures = 77
        self.district.difficulty = 'Hard'
        self.district.registered_voters = 1000
        self.district.partners = 'Partner C'
        self.district.partner_mobilized = False
        self.district.save()

        view = MapView()
        feature = {
            'properties': {
                'legis_dist': self.district.legis_dist,
                'registered_voters': 1000,
                'collected_signatures': self.district.collected_signatures,
                'difficulty': self.district.difficulty,
                'partners': self.district.partners,
                'partner_mobilized': self.district.partner_mobilized,
            }
        }

        style = view._compute_fill_style(
            feature,
            districts_by_name={self.district.legis_dist: self.district},
            blue='#0099ff',
            yellow='#ffcc00',
            pink='#ff0088',
            stripes_blue=None,
            stripes_yellow=None,
            stripes_pink=None,
        )

        self.assertEqual(style['fillColor'], '#ff0088')
        self.assertEqual(style['fillOpacity'], 1.0)
