"""Branch-coverage tests for the Recycling Rewards application.

The Part 1 tests below cover every decision outcome. Additional cases at the
end check interactions and exact boundaries of the bonus, hazard, and holiday
paths so this file can be run independently.
"""

import pytest

from recycling_rewards import collection_accepted, reward_points, slot_status


# Preserve the two valid starter cases.
def test_below_minimum_weight():
    assert reward_points("paper", 3, False) == 0


def test_collection_accepted():
    assert collection_accepted(20, 2, False) is True


@pytest.mark.parametrize(
    "material, weight_kg, has_bonus, expected",
    [
        ("paper", 5, False, 0),     # Exact minimum earns nothing.
        ("paper", 6, False, 6),     # First kilogram above the minimum.
        ("paper", 5, True, 6),      # Bonus lowers a nonmetal minimum.
        ("plastic", 3, False, 0),
        ("plastic", 3, True, 6),
        ("metal", 2, True, 0),      # Bonus does not lower the metal minimum.
        ("metal", 3, False, 12),
        ("paper", 25, False, 120),  # Exactly 20 extra kilograms: base rate.
        ("paper", 26, False, 210),  # Above 20: increased nonmetal rate.
        ("metal", 22, False, 240),
        ("metal", 23, False, 378),  # Above 20: increased metal rate.
    ],
)
def test_reward_points_thresholds(material, weight_kg, has_bonus, expected):
    assert reward_points(material, weight_kg, has_bonus) == expected


@pytest.mark.parametrize(
    "material, weight_kg, message",
    [
        ("glass", 10, "unknown material"),
        ("paper", -0.1, "invalid weight"),
    ],
)
def test_reward_points_rejects_invalid_inputs(material, weight_kg, message):
    with pytest.raises(ValueError, match=message):
        reward_points(material, weight_kg, False)


@pytest.mark.parametrize(
    "weight_kg, bags, is_hazardous, expected",
    [
        (5, 4, True, True),         # Hazardous collection uses only the 5 kg limit.
        (5.1, 1, True, False),
        (50, 3, False, True),      # Ordinary weight and bag limits are inclusive.
        (50.1, 1, False, False),
        (20, 4, False, False),
    ],
)
def test_collection_limits(weight_kg, bags, is_hazardous, expected):
    assert collection_accepted(weight_kg, bags, is_hazardous) is expected


@pytest.mark.parametrize(
    "minutes_left, is_morning, is_holiday, expected",
    [
        (20, True, False, "open"),
        (19, True, False, "late"),
        (5, True, False, "late"),
        (4, True, False, "missed"),
        (10, False, False, "open"),
        (9, False, False, "late"),
        (-6, False, False, "missed"),
        (25, False, True, "open"),
        (35, True, True, "open"),
        (34, True, True, "late"),
    ],
)
def test_slot_status_cutoffs(minutes_left, is_morning, is_holiday, expected):
    assert slot_status(minutes_left, is_morning, is_holiday) == expected


@pytest.mark.parametrize(
    "material, weight_kg, has_bonus, expected",
    [
        ("paper", 4, True, 0),      # Bonus-adjusted minimum, inclusive.
        ("paper", 24, True, 120),  # Exactly 20 extra after the bonus.
        ("paper", 25, True, 210),  # One more extra switches the rate.
        ("plastic", 23, False, 120),
        ("plastic", 24, False, 210),
        ("metal", 23, True, 378),  # A bonus never changes the metal path.
    ],
)
def test_reward_rate_branches_at_adjusted_boundaries(
    material, weight_kg, has_bonus, expected
):
    assert reward_points(material, weight_kg, has_bonus) == expected


def test_unknown_material_error_precedes_invalid_weight_error():
    with pytest.raises(ValueError, match="unknown material"):
        reward_points("glass", -1, False)


@pytest.mark.parametrize(
    "weight_kg, bags, is_hazardous, expected",
    [
        (5, 99, True, True),       # Hazardous bags do not affect acceptance.
        (5.0001, 0, True, False),
        (50, 4, False, False),    # Bag limit still applies at 50 kg.
        (50.0001, 0, False, False),
    ],
)
def test_collection_decision_precedence(weight_kg, bags, is_hazardous, expected):
    assert collection_accepted(weight_kg, bags, is_hazardous) is expected


@pytest.mark.parametrize(
    "minutes_left, is_morning, is_holiday, expected",
    [
        (20, True, True, "late"),
        (19, True, True, "missed"),
        (10, False, True, "late"),
        (9, False, True, "missed"),
    ],
)
def test_holiday_late_and_missed_boundaries(
    minutes_left, is_morning, is_holiday, expected
):
    assert slot_status(minutes_left, is_morning, is_holiday) == expected
