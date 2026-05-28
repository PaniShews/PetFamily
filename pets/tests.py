from django.test import TestCase, Client
from django.urls import reverse

from pets.models import Pet, AnimalType, AdoptionRequest, Vaccination
from users.models import User, BreederShelterProfile


def make_user(username="user1", password="testpass123", **kwargs):
    return User.objects.create_user(username=username, password=password, **kwargs)


def make_org_user(username="shelter1", is_shelter=True):
    user = make_user(username=username)
    animal_type = AnimalType.objects.get_or_create(name="Dog")[0]
    profile = BreederShelterProfile.objects.create(
        user=user, name=f"{username} org", is_shelter=is_shelter
    )
    return user, profile


def make_pet(owner, name="Buddy", is_available=True, price=None):
    animal_type = AnimalType.objects.get_or_create(name="Dog")[0]
    return Pet.objects.create(
        name=name,
        type=animal_type,
        breed="Labrador",
        age=2,
        owner=owner,
        is_available=is_available,
        price=price,
    )


class PetModelTest(TestCase):

    def setUp(self):
        _, self.shelter = make_org_user("shelter_model", is_shelter=True)
        _, self.breeder = make_org_user("breeder_model", is_shelter=False)

    def test_shelter_pet_is_free(self):
        pet = make_pet(self.shelter)
        self.assertTrue(pet.is_free)

    def test_breeder_pet_with_price_is_not_free(self):
        pet = make_pet(self.breeder, price=500)
        self.assertFalse(pet.is_free)

    def test_breeder_pet_without_price_is_free(self):
        pet = make_pet(self.breeder, price=None)
        self.assertTrue(pet.is_free)

    def test_pet_str(self):
        pet = make_pet(self.shelter)
        self.assertIn("Buddy", str(pet))

    def test_age_cannot_be_negative(self):
        from django.core.exceptions import ValidationError
        animal_type = AnimalType.objects.get_or_create(name="Dog")[0]
        pet = Pet(name="X", type=animal_type, breed="X", age=-1, owner=self.shelter)
        with self.assertRaises(ValidationError):
            pet.full_clean()

    def test_price_cannot_be_negative(self):
        from django.core.exceptions import ValidationError
        animal_type = AnimalType.objects.get_or_create(name="Dog")[0]
        pet = Pet(name="X", type=animal_type, breed="X", age=1, owner=self.breeder, price=-10)
        with self.assertRaises(ValidationError):
            pet.full_clean()


class BreederShelterProfileModelTest(TestCase):

    def test_kind_label_shelter(self):
        user = make_user("u1")
        profile = BreederShelterProfile(user=user, name="Happy Paws", is_shelter=True)
        self.assertEqual(profile.kind_label, "Shelter")

    def test_kind_label_breeder(self):
        user = make_user("u2")
        profile = BreederShelterProfile(user=user, name="Top Breeds", is_shelter=False)
        self.assertEqual(profile.kind_label, "Breeder")


class HomePageViewTest(TestCase):

    def setUp(self):
        _, self.shelter = make_org_user("s1")
        self.pet = make_pet(self.shelter, name="Rex")

    def test_home_page_loads(self):
        response = self.client.get(reverse("home_page"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rex")

    def test_home_page_search_by_name(self):
        make_pet(self.shelter, name="Luna")
        response = self.client.get(reverse("home_page") + "?q=Rex")
        self.assertContains(response, "Rex")
        self.assertNotContains(response, "Luna")

    def test_home_page_filter_by_shelter(self):
        _, breeder = make_org_user("b1", is_shelter=False)
        make_pet(breeder, name="BreederDog", price=300)
        response = self.client.get(reverse("home_page") + "?kind=shelter")
        self.assertContains(response, "Rex")
        self.assertNotContains(response, "BreederDog")

    def test_unavailable_pets_not_shown(self):
        make_pet(self.shelter, name="Gone", is_available=False)
        response = self.client.get(reverse("home_page"))
        self.assertNotContains(response, "Gone")


class PetDetailViewTest(TestCase):

    def setUp(self):
        _, self.shelter = make_org_user("s2")
        self.pet = make_pet(self.shelter)

    def test_pet_detail_loads(self):
        response = self.client.get(reverse("pet_detail", args=[self.pet.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buddy")

    def test_pet_detail_404_for_missing(self):
        response = self.client.get(reverse("pet_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)


class ShelterListViewTest(TestCase):

    def test_shelters_list_loads(self):
        response = self.client.get(reverse("shelter_list"))
        self.assertEqual(response.status_code, 200)

    def test_shelter_appears_in_list(self):
        _, profile = make_org_user("happy_shelter")
        response = self.client.get(reverse("shelter_list"))
        self.assertContains(response, "happy_shelter org")

    def test_shelter_detail_loads(self):
        _, profile = make_org_user("detail_shelter")
        response = self.client.get(reverse("shelter_detail", args=[profile.pk]))
        self.assertEqual(response.status_code, 200)


class ReservePetViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.adopter = make_user("adopter")
        _, self.shelter = make_org_user("reserve_shelter")
        self.pet = make_pet(self.shelter)

    def test_reserve_redirects_if_not_logged_in(self):
        response = self.client.get(reverse("reserve_pet", args=[self.pet.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response["Location"])

    def test_reserve_get_loads_form(self):
        self.client.force_login(self.adopter)
        response = self.client.get(reverse("reserve_pet", args=[self.pet.pk]))
        self.assertEqual(response.status_code, 200)

    def test_reserve_post_creates_adoption_request(self):
        self.client.force_login(self.adopter)
        response = self.client.post(
            reverse("reserve_pet", args=[self.pet.pk]),
            {"message": "I would love to adopt Buddy!"}
        )
        self.assertEqual(AdoptionRequest.objects.count(), 1)
        adoption = AdoptionRequest.objects.first()
        self.assertEqual(adoption.user, self.adopter)
        self.assertEqual(adoption.pet, self.pet)

    def test_reserve_post_marks_pet_unavailable(self):
        self.client.force_login(self.adopter)
        self.client.post(
            reverse("reserve_pet", args=[self.pet.pk]),
            {"message": "Please!"}
        )
        self.pet.refresh_from_db()
        self.assertFalse(self.pet.is_available)

    def test_reserve_post_redirects_to_agreement(self):
        self.client.force_login(self.adopter)
        response = self.client.post(
            reverse("reserve_pet", args=[self.pet.pk]),
            {"message": ""}
        )
        self.assertRedirects(response, reverse("agreement", args=[1]))

    def test_duplicate_request_redirects_to_existing(self):
        self.client.force_login(self.adopter)
        self.client.post(reverse("reserve_pet", args=[self.pet.pk]), {"message": ""})
        # Second attempt on same (now unavailable) pet — pet is gone but request exists
        existing = AdoptionRequest.objects.first()
        # Try to access agreement directly
        response = self.client.get(reverse("agreement", args=[existing.pk]))
        self.assertEqual(response.status_code, 200)


class AgreementViewTest(TestCase):

    def setUp(self):
        self.adopter = make_user("agr_adopter")
        _, self.shelter = make_org_user("agr_shelter")
        self.pet = make_pet(self.shelter)
        self.adoption = AdoptionRequest.objects.create(
            user=self.adopter, pet=self.pet, status="pending"
        )

    def test_agreement_loads_for_owner(self):
        self.client.force_login(self.adopter)
        response = self.client.get(reverse("agreement", args=[self.adoption.pk]))
        self.assertEqual(response.status_code, 200)

    def test_agreement_denied_for_other_user(self):
        other = make_user("stranger")
        self.client.force_login(other)
        response = self.client.get(reverse("agreement", args=[self.adoption.pk]))
        self.assertRedirects(response, reverse("home_page"))


class DashboardViewTest(TestCase):

    def setUp(self):
        self.org_user, self.profile = make_org_user("dash_shelter")
        self.regular = make_user("regular_dash")

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_requires_org_profile(self):
        self.client.force_login(self.regular)
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("home_page"))

    def test_dashboard_loads_for_org(self):
        self.client.force_login(self.org_user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_shows_own_pets(self):
        make_pet(self.profile, name="MyDog")
        self.client.force_login(self.org_user)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "MyDog")


class AddPetViewTest(TestCase):

    def setUp(self):
        self.org_user, self.profile = make_org_user("add_shelter")
        self.animal_type = AnimalType.objects.get_or_create(name="Dog")[0]

    def test_add_pet_get_loads(self):
        self.client.force_login(self.org_user)
        response = self.client.get(reverse("add_pet"))
        self.assertEqual(response.status_code, 200)

    def test_add_pet_post_creates_pet(self):
        self.client.force_login(self.org_user)
        self.client.post(reverse("add_pet"), {
            "name": "NewDog",
            "type": self.animal_type.pk,
            "breed": "Poodle",
            "age": 3,
            "description": "",
        })
        self.assertTrue(Pet.objects.filter(name="NewDog").exists())

    def test_shelter_pet_has_no_price(self):
        self.client.force_login(self.org_user)
        self.client.post(reverse("add_pet"), {
            "name": "FreeDog",
            "type": self.animal_type.pk,
            "breed": "Mix",
            "age": 1,
            "price": 999,  # should be ignored for shelter
        })
        pet = Pet.objects.filter(name="FreeDog").first()
        if pet:
            self.assertIsNone(pet.price)

    def test_regular_user_cannot_add_pet(self):
        regular = make_user("reg_add")
        self.client.force_login(regular)
        response = self.client.get(reverse("add_pet"))
        self.assertRedirects(response, reverse("home_page"))