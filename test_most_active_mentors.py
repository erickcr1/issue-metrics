"""A module containing unit tests for the most_active_mentors module.

This module contains unit tests for the count_comments_per_user and
get_mentor_count functions in the most_active_mentors module.
The tests use mock GitHub issues and comments to test the functions' behavior.

Classes:
    TestCountCommentsPerUser: A class testing count_comments_per_user.
    TestGetMentorCount: A class to test the
        get_mentor_count function.

"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock

from classes import IssueWithMetrics
from most_active_mentors import count_comments_per_user, get_mentor_count


class TestCountCommentsPerUser(unittest.TestCase):
    """Test the count_comments_per_user function."""

    def test_count_comments_per_user_limit(self):
        """Test that count_comments_per_user correctly counts user comments.

        This test mocks the GitHub connection and issue comments, and checks
        that count_comments_per_user correctly considers user comments for
        counting.

        """
        # Set up the mock GitHub issues
        mock_issue1 = MagicMock()
        mock_issue1.comments = 2
        mock_issue1.issue.user.login = "issue_owner"
        mock_issue1.created_at = "2023-01-01T00:00:00Z"

        # Set up 21 mock GitHub issue comments - only 20 should be counted
        mock_issue1.issue.comments.return_value = []
        for i in range(22):
            mock_comment1 = MagicMock()
            mock_comment1.user.login = "very_active_user"
            mock_comment1.created_at = datetime.fromisoformat(
                f"2023-01-02T{i:02d}:00:00Z"
            )
            # pylint: disable=maybe-no-member
            mock_issue1.issue.comments.return_value.append(mock_comment1)

        # Call the function
        result = count_comments_per_user(mock_issue1)
        expected_result = {"very_active_user": 3}

        # Check the results
        self.assertEqual(result, expected_result)

    def test_count_comments_per_user_with_ignores(self):
        """Test that count_comments_per_user correctly counts user comments with some users ignored."""
        # Set up the mock GitHub issues
        mock_issue1 = MagicMock()
        mock_issue1.comments = 2
        mock_issue1.issue.user.login = "issue_owner"
        mock_issue1.created_at = "2023-01-01T00:00:00Z"

        # Set up mock GitHub issue comments by several users
        mock_issue1.issue.comments.return_value = []
        for i in range(5):
            mock_comment1 = MagicMock()
            mock_comment1.user.login = "very_active_user"
            mock_comment1.created_at = datetime.fromisoformat(
                f"2023-01-02T{i:02d}:00:00Z"
            )
            # pylint: disable=maybe-no-member
            mock_issue1.issue.comments.return_value.append(mock_comment1)
        for i in range(5):
            mock_comment1 = MagicMock()
            mock_comment1.user.login = "very_active_user_ignored"
            mock_comment1.created_at = datetime.fromisoformat(
                f"2023-01-02T{i:02d}:00:00Z"
            )
            # pylint: disable=maybe-no-member
            mock_issue1.issue.comments.return_value.append(mock_comment1)

        # Call the function
        result = count_comments_per_user(
            mock_issue1, ignore_users=["very_active_user_ignored"]
        )
        # Only the comments by "very_active_user" should be counted,
        # so the count should be 3 since that is the threshold for heavily involved
        expected_result = {"very_active_user": 3}

        # Check the results
        self.assertEqual(result, expected_result)
        self.assertNotIn("very_active_user_ignored", result)

    def test_get_mentor_count(self):
        """Test that get_mentor_count correctly counts comments per user."""
        mentor_activity = {"sue": 15, "bob": 10}

        # Create mock data
        issues_with_metrics = [
            IssueWithMetrics(
                "Issue 1",
                "https://github.com/user/repo/issues/1",
                "alice",
                None,
                mentor_activity=mentor_activity,
            ),
            IssueWithMetrics(
                "Issue 2",
                "https://github.com/user/repo/issues/2",
                "bob",
                None,
                mentor_activity=mentor_activity,
            ),
        ]

        # Call the function and check the result
        result = get_mentor_count(issues_with_metrics, 2)
        expected_result = 2
        self.assertEqual(result, expected_result)
