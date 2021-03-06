#! /usr/bin/env python

import unittest
import os
import sys
import logging

from pycoevolity import errors 
from pycoevolity import partition
from pycoevolity.test import TestLevel
from pycoevolity.test.support.pycoevolity_test_case import PycoevolityTestCase

_LOG = logging.getLogger(__name__)


class TestStandardizePartition(unittest.TestCase):
    def test_simple(self):
        elements = ['c', 'c', 'a', 'b', 'c', 'a']
        p, v = partition.standardize_partition(elements)
        self.assertEqual(p, tuple([0, 0, 1, 2, 0, 1]))
        self.assertEqual(v, {0: ['c'], 1: ['a'], 2: ['b']})

class TestSubset(unittest.TestCase):
    def test_simple(self):
        s = partition.Subset()
        self.assertEqual(s.value, None)
        self.assertEqual(s.set_of_indices, set())
        self.assertEqual(s.list_of_indices, [])
        self.assertEqual(s.number_of_elements, 0)

        s.add_index(3)
        s.add_index(1)
        s.add_index(5)

        self.assertEqual(s.value, None)
        self.assertEqual(s.set_of_indices, set([1,3,5]))
        self.assertEqual(s.list_of_indices, [1,3,5])
        self.assertEqual(s.number_of_elements, 3)
        self.assertRaises(Exception, s.add_index, 3)

        s = partition.Subset([5,1,3], 1.1)
        self.assertEqual(s.value, 1.1) 
        self.assertEqual(s.set_of_indices, set([1,3,5]))
        self.assertEqual(s.list_of_indices, [1,3,5])
        self.assertEqual(s.number_of_elements, 3)
        self.assertRaises(Exception, s.add_index, 3)

    def test_ops(self):
        s1 = partition.Subset()
        s2 = partition.Subset()
        self.assertEqual(s1 == s2, True)
        self.assertEqual(s1 <= s2, True)
        self.assertEqual(s1 >= s2, True)
        self.assertEqual(s1 < s2, False)
        self.assertEqual(s1 > s2, False)

        s1.add_index(0)
        self.assertEqual(s1 == s2, False)
        self.assertEqual(s1 <= s2, False)
        self.assertEqual(s1 >= s2, True)
        self.assertEqual(s1 < s2, False)
        self.assertEqual(s1 > s2, True)

        s2.add_index(0)
        self.assertEqual(s1 == s2, True)
        self.assertEqual(s1 <= s2, True)
        self.assertEqual(s1 >= s2, True)
        self.assertEqual(s1 < s2, False)
        self.assertEqual(s1 > s2, False)

        s2 = partition.Subset()
        s2.add_index(1)
        s1.add_index(2)
        self.assertEqual(s1 == s2, False)
        self.assertEqual(s1 <= s2, True)
        self.assertEqual(s1 >= s2, False)
        self.assertEqual(s1 < s2, True)
        self.assertEqual(s1 > s2, False)


class TestSetPartition(unittest.TestCase):
    def test_missing_index(self):
        s1 = partition.Subset([0, 1])
        s2 = partition.Subset([3, 4])
        self.assertRaises(errors.InvalidSetPartitionError, partition.SetPartition, [s1, s2])

    def test_duplicate_index(self):
        s1 = partition.Subset([0, 1])
        s2 = partition.Subset([1, 2])
        self.assertRaises(errors.InvalidSetPartitionError, partition.SetPartition, [s1, s2])

    def test_constructors(self):
        s1 = partition.Subset([0, 2])
        s2 = partition.Subset([1, 3])
        p1 = partition.SetPartition([s1, s2])
        p2 = partition.SetPartition.get_from_indices(("a", "b", "a", "b"))

        indices1 = []
        for ss in p1.subsets:
            indices1.append(ss.list_of_indices)
        indices2 = []
        for ss in p2.subsets:
            indices2.append(ss.list_of_indices)
        self.assertEqual(sorted(indices1), sorted(indices2))

        self.assertTrue(p1 == p2)

        self.assertEqual(p1.as_indices(), (0, 1, 0, 1))
        self.assertEqual(p2.as_indices(), (0, 1, 0, 1))

        self.assertEqual(p1.number_of_elements, 4)
        self.assertEqual(p1.number_of_subsets, 2)
        self.assertEqual(p2.number_of_elements, 4)
        self.assertEqual(p2.number_of_subsets, 2)

    def test_as_indices(self):
        s1 = partition.Subset([0, 3])
        s2 = partition.Subset([1, 4])
        s3 = partition.Subset([2, 5])

        p1 = partition.SetPartition()
        p1.add_subset(s1)
        p1.add_subset(s2)
        p1.add_subset(s3)
        self.assertEqual(p1.as_indices(), (0, 1, 2, 0, 1, 2))

        p2 = partition.SetPartition()
        p2.add_subset(s3)
        p2.add_subset(s2)
        p2.add_subset(s1)
        self.assertEqual(p2.as_indices(), (0, 1, 2, 0, 1, 2))

        p3 = partition.SetPartition()
        p3.add_subset(s2)
        p3.add_subset(s3)
        p3.add_subset(s1)
        self.assertEqual(p3.as_indices(), (0, 1, 2, 0, 1, 2))

        self.assertTrue(p1 == p2)
        self.assertTrue(p1 == p3)
        self.assertFalse(p1 is p2)
        self.assertFalse(p1 is p3)

    def test_distance_zero(self):
        s1 = partition.Subset([0, 2])
        s2 = partition.Subset([1, 3])
        p1 = partition.SetPartition([s1, s2])
        p2 = partition.SetPartition.get_from_indices(("a", "b", "a", "b"))

        self.assertEqual(p1.distance(p2), 0)
        self.assertEqual(p2.distance(p1), 0)
        self.assertEqual(p1.as_indices(), (0, 1, 0, 1))
        self.assertEqual(p2.as_indices(), (0, 1, 0, 1))

    def test_distance_one(self):
        p1 = partition.SetPartition.get_from_indices((0, 1, 2))
        p2 = partition.SetPartition.get_from_indices((0, 1, 1))

        self.assertEqual(p1.distance(p2), 1)
        self.assertEqual(p2.distance(p1), 1)

        self.assertEqual(p1.number_of_elements, 3)
        self.assertEqual(p1.number_of_subsets, 3)
        self.assertEqual(p2.number_of_elements, 3)
        self.assertEqual(p2.number_of_subsets, 2)

        p1 = partition.SetPartition.get_from_indices((0, 1, 2))
        p2 = partition.SetPartition.get_from_indices((0, 0, 1))

        self.assertEqual(p1.distance(p2), 1)
        self.assertEqual(p2.distance(p1), 1)

        self.assertEqual(p1.number_of_elements, 3)
        self.assertEqual(p1.number_of_subsets, 3)
        self.assertEqual(p2.number_of_elements, 3)
        self.assertEqual(p2.number_of_subsets, 2)

        # We can remove the first element from both in this case
        p1 = partition.SetPartition.get_from_indices((0, 1, 0))
        p2 = partition.SetPartition.get_from_indices((0, 0, 1))

        self.assertEqual(p1.distance(p2), 1)
        self.assertEqual(p2.distance(p1), 1)

        self.assertEqual(p1.number_of_elements, 3)
        self.assertEqual(p1.number_of_subsets, 2)
        self.assertEqual(p2.number_of_elements, 3)
        self.assertEqual(p2.number_of_subsets, 2)

    def test_distance_two(self):
        p1 = partition.SetPartition.get_from_indices((0, 1, 2))
        p2 = partition.SetPartition.get_from_indices((0, 0, 0))

        self.assertEqual(p1.distance(p2), 2)
        self.assertEqual(p2.distance(p1), 2)

        p1 = partition.SetPartition.get_from_indices((0, 0, 1, 1, 2))
        p2 = partition.SetPartition.get_from_indices((0, 1, 2, 2, 2))

        self.assertEqual(p1.distance(p2), 2)
        self.assertEqual(p2.distance(p1), 2)

        p1 = partition.SetPartition.get_from_indices((0, 0, 0, 0, 1, 0))
        p2 = partition.SetPartition.get_from_indices((0, 0, 0, 0, 0, 1))

        self.assertEqual(p1.distance(p2), 2)
        self.assertEqual(p2.distance(p1), 2)
        self.assertEqual(p1.as_indices(), (0, 0, 0, 0, 1, 0))
        self.assertEqual(p2.as_indices(), (0, 0, 0, 0, 0, 1))
