#!/usr/bin/env python3
"""
Tests for ACE fact parsing functionality
"""

import unittest
from src.ace_prolog_parser import ACEToPrologParser


class TestFactParsing(unittest.TestCase):
    """Test ACE fact parsing to Prolog conversion"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = ACEToPrologParser()

    def test_is_a_person_pattern(self):
        """Test 'X is a person' pattern"""
        result = self.parser.ace_to_prolog_fact("John is a person.")
        self.assertEqual(result, "person(john)")

    def test_is_a_teacher_pattern(self):
        """Test 'X is a teacher' pattern"""
        result = self.parser.ace_to_prolog_fact("Mary is a teacher.")
        self.assertEqual(result, "teacher(mary)")

    def test_is_a_student_pattern(self):
        """Test 'X is a student' pattern"""
        result = self.parser.ace_to_prolog_fact("Bob is a student.")
        self.assertEqual(result, "student(bob)")

    def test_is_a_doctor_with_hyphen(self):
        """Test 'X is a Y' pattern with hyphenated names"""
        result = self.parser.ace_to_prolog_fact("Alice-Smith is a doctor.")
        self.assertEqual(result, "doctor(alice_smith)")

    def test_is_a_machine_with_number(self):
        """Test 'X is a Y' pattern with numbered entities"""
        result = self.parser.ace_to_prolog_fact("Computer-1 is a machine.")
        self.assertEqual(result, "machine(computer_1)")

    def test_is_happy_property(self):
        """Test 'X is happy' property pattern"""
        result = self.parser.ace_to_prolog_fact("John is happy.")
        self.assertEqual(result, "happy(john)")

    def test_is_tall_property(self):
        """Test 'X is tall' property pattern"""
        result = self.parser.ace_to_prolog_fact("Mary is tall.")
        self.assertEqual(result, "tall(mary)")

    def test_is_smart_property(self):
        """Test 'X is smart' property pattern"""
        result = self.parser.ace_to_prolog_fact("Bob is smart.")
        self.assertEqual(result, "smart(bob)")

    def test_is_kind_property(self):
        """Test 'X is kind' property pattern"""
        result = self.parser.ace_to_prolog_fact("Alice is kind.")
        self.assertEqual(result, "kind(alice)")

    def test_is_friendly_with_hyphen(self):
        """Test 'X is Y' property with hyphenated entity"""
        result = self.parser.ace_to_prolog_fact("The-dog is friendly.")
        self.assertEqual(result, "friendly(the_dog)")

    def test_likes_chocolate(self):
        """Test 'X likes chocolate' pattern"""
        result = self.parser.ace_to_prolog_fact("John likes chocolate.")
        self.assertEqual(result, "likes(john, chocolate)")

    def test_likes_music(self):
        """Test 'X likes music' pattern"""
        result = self.parser.ace_to_prolog_fact("Mary likes music.")
        self.assertEqual(result, "likes(mary, music)")

    def test_likes_ice_cream(self):
        """Test 'X likes Y' with hyphenated object"""
        result = self.parser.ace_to_prolog_fact("Bob likes ice-cream.")
        self.assertEqual(result, "likes(bob, ice_cream)")

    def test_likes_sunny_days(self):
        """Test 'X likes Y' with compound object"""
        result = self.parser.ace_to_prolog_fact("Alice likes sunny-days.")
        self.assertEqual(result, "likes(alice, sunny_days)")

    def test_likes_fish_with_hyphenated_subject(self):
        """Test 'X likes Y' with hyphenated subject"""
        result = self.parser.ace_to_prolog_fact("The-cat likes fish.")
        self.assertEqual(result, "likes(the_cat, fish)")

    def test_has_age_25(self):
        """Test 'X has age Y' pattern"""
        result = self.parser.ace_to_prolog_fact("John has age 25.")
        self.assertEqual(result, "has_property(john, age, 25)")

    def test_has_color_blue(self):
        """Test 'X has color Y' pattern"""
        result = self.parser.ace_to_prolog_fact("Mary has color blue.")
        self.assertEqual(result, "has_property(mary, color, blue)")

    def test_has_height_tall(self):
        """Test 'X has height Y' pattern"""
        result = self.parser.ace_to_prolog_fact("Bob has height tall.")
        self.assertEqual(result, "has_property(bob, height, tall)")

    def test_has_pet_cat(self):
        """Test 'X has pet Y' pattern"""
        result = self.parser.ace_to_prolog_fact("Alice has pet cat.")
        self.assertEqual(result, "has_property(alice, pet, cat)")

    def test_has_color_red_with_hyphen(self):
        """Test 'X has Y Z' with hyphenated subject"""
        result = self.parser.ace_to_prolog_fact("The-car has color red.")
        self.assertEqual(result, "has_property(the_car, color, red)")

    def test_entity_normalization_john_smith(self):
        """Test entity normalization with John-Smith"""
        result = self.parser.ace_to_prolog_fact("John-Smith is a person.")
        self.assertEqual(result, "person(john_smith)")

    def test_entity_normalization_mary_jane(self):
        """Test entity normalization with spaces"""
        result = self.parser.ace_to_prolog_fact("Mary Jane is happy.")
        self.assertEqual(result, "happy(mary_jane)")

    def test_entity_normalization_computer_1(self):
        """Test entity normalization with numbers"""
        result = self.parser.ace_to_prolog_fact("Computer 1 is a machine.")
        self.assertEqual(result, "machine(computer_1)")

    def test_entity_normalization_ice_cream_shop(self):
        """Test entity normalization with multiple hyphens"""
        result = self.parser.ace_to_prolog_fact("Ice-Cream-Shop is a business.")
        self.assertEqual(result, "business(ice_cream_shop)")

    # def test_unsupported_complex_sentence(self):
    #     """Test unsupported complex sentence returns None"""
    #     result = self.parser.ace_to_prolog_fact("This is a complex sentence that doesn't match patterns.")
    #     self.assertIsNone(result)

    def test_unsupported_and_conjunction(self):
        """Test unsupported 'and' conjunction returns None"""
        result = self.parser.ace_to_prolog_fact("John and Mary are friends.")
        self.assertIsNone(result)

    # def test_unsupported_weather_sentence(self):
    #     """Test unsupported weather sentence returns None"""
    #     result = self.parser.ace_to_prolog_fact("The weather is nice today.")
    #     self.assertIsNone(result)

    def test_unsupported_empty_string(self):
        """Test empty string returns None"""
        result = self.parser.ace_to_prolog_fact("")
        self.assertIsNone(result)

    def test_unsupported_random_text(self):
        """Test random text returns None"""
        result = self.parser.ace_to_prolog_fact("Random text without proper structure")
        self.assertIsNone(result)

    def test_without_period_person(self):
        """Test fact without period - person"""
        result = self.parser.ace_to_prolog_fact("John is a person")
        self.assertEqual(result, "person(john)")

    def test_without_period_happy(self):
        """Test fact without period - property"""
        result = self.parser.ace_to_prolog_fact("Mary is happy")
        self.assertEqual(result, "happy(mary)")

    def test_without_period_likes(self):
        """Test fact without period - likes"""
        result = self.parser.ace_to_prolog_fact("Bob likes chocolate")
        self.assertEqual(result, "likes(bob, chocolate)")

    def test_whitespace_leading_trailing(self):
        """Test handling leading/trailing whitespace"""
        result = self.parser.ace_to_prolog_fact("  John is a person.  ")
        self.assertEqual(result, "person(john)")

    def test_whitespace_tabs(self):
        """Test handling tabs"""
        result = self.parser.ace_to_prolog_fact("\tMary is happy.\t")
        self.assertEqual(result, "happy(mary)")

    def test_whitespace_multiple_spaces(self):
        """Test handling multiple spaces"""
        result = self.parser.ace_to_prolog_fact("Bob  likes  chocolate.")
        self.assertEqual(result, "likes(bob, chocolate)")

    def test_whitespace_has_property(self):
        """Test handling whitespace in has property"""
        result = self.parser.ace_to_prolog_fact("Alice   has   age   25.")
        self.assertEqual(result, "has_property(alice, age, 25)")


if __name__ == '__main__':
    unittest.main()