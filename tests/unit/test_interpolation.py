"""
Task 4: Unit Tests for NULL Handling & Interpolation

Tests the interpolation engine for revenue, growth, and employee estimation.
"""


from solstein.data.interpolation import InterpolationConfig, InterpolationEngine


class TestInterpolationConfig:
    """Test InterpolationConfig."""

    def test_default_config(self):
        """Default config should have sensible values."""
        config = InterpolationConfig()
        assert config.revenue_min_timeline_points == 2
        assert config.revenue_interpolation_method == "geometric"
        assert config.revenue_max_gap_years == 3
        assert config.growth_sector_average_fallback == 10.0
        assert config.employee_revenue_ratio == 0.0003
        assert config.flag_all_interpolations is True


class TestInterpolationEngine:
    """Test InterpolationEngine."""

    def test_engine_initializes(self):
        """Engine should initialize successfully."""
        engine = InterpolationEngine()
        assert engine.config is not None

    def test_revenue_already_known(self):
        """If revenue is known, return it without interpolation."""
        engine = InterpolationEngine()
        revenue, is_interpolated = engine.interpolate_revenue(
            revenue_timeline=[],
            current_revenue=100.0,
        )
        assert revenue == 100.0
        assert is_interpolated is False

    def test_revenue_no_timeline(self):
        """If no timeline, return None."""
        engine = InterpolationEngine()
        revenue, is_interpolated = engine.interpolate_revenue(
            revenue_timeline=None,
            current_revenue=None,
        )
        assert revenue is None
        assert is_interpolated is False

    def test_revenue_insufficient_points(self):
        """If timeline has < 2 points, return None."""
        engine = InterpolationEngine()
        revenue, is_interpolated = engine.interpolate_revenue(
            revenue_timeline=[{"year": 2022, "revenue": 10.0}],
            current_revenue=None,
        )
        assert revenue is None
        assert is_interpolated is False

    def test_revenue_geometric_interpolation(self):
        """Revenue should interpolate using geometric mean."""
        engine = InterpolationEngine()
        timeline = [
            {"year": 2022, "revenue": 10.0},
            {"year": 2024, "revenue": 15.0},
        ]
        revenue, is_interpolated = engine.interpolate_revenue(
            revenue_timeline=timeline,
            current_revenue=None,
        )
        # Geometric mean: sqrt(10 * 15) = sqrt(150) ≈ 12.25
        assert 12.0 <= revenue <= 12.5
        assert is_interpolated is True

    def test_revenue_gap_too_large(self):
        """If gap > max_gap_years, don't interpolate."""
        config = InterpolationConfig(revenue_max_gap_years=2)
        engine = InterpolationEngine(config)
        timeline = [
            {"year": 2020, "revenue": 10.0},
            {"year": 2024, "revenue": 15.0},  # 4 year gap
        ]
        revenue, is_interpolated = engine.interpolate_revenue(
            revenue_timeline=timeline,
            current_revenue=None,
        )
        assert revenue is None
        assert is_interpolated is False

    def test_revenue_linear_interpolation(self):
        """Revenue should support linear interpolation method."""
        config = InterpolationConfig(revenue_interpolation_method="linear")
        engine = InterpolationEngine(config)
        timeline = [
            {"year": 2022, "revenue": 10.0},
            {"year": 2024, "revenue": 20.0},
        ]
        revenue, is_interpolated = engine.interpolate_revenue(
            revenue_timeline=timeline,
            current_revenue=None,
        )
        # Linear: 10 + (20 - 10) / 2 = 15
        assert revenue == 15.0
        assert is_interpolated is True

    def test_growth_already_known(self):
        """If growth is known, return it without interpolation."""
        engine = InterpolationEngine()
        growth, is_interpolated = engine.interpolate_growth_rate(
            revenue_timeline=[],
            current_growth=15.0,
        )
        assert growth == 15.0
        assert is_interpolated is False

    def test_growth_no_timeline_use_sector_average(self):
        """If no timeline and sector average enabled, use it."""
        engine = InterpolationEngine()
        growth, is_interpolated = engine.interpolate_growth_rate(
            revenue_timeline=None,
            current_growth=None,
        )
        assert growth == 10.0  # Default sector average
        assert is_interpolated is True

    def test_growth_calculated_from_timeline(self):
        """Growth should be calculated as CAGR from timeline."""
        engine = InterpolationEngine()
        timeline = [
            {"year": 2022, "revenue": 10.0},
            {"year": 2024, "revenue": 15.0},  # 2 years
        ]
        growth, is_interpolated = engine.interpolate_growth_rate(
            revenue_timeline=timeline,
            current_growth=None,
        )
        # CAGR: ((15/10) ^ (1/2) - 1) * 100 ≈ 22.5%
        assert 22.0 <= growth <= 23.0
        assert is_interpolated is True

    def test_employees_already_known(self):
        """If employees is known, return it without interpolation."""
        engine = InterpolationEngine()
        employees, is_interpolated = engine.interpolate_employees(
            employee_timeline=[],
            current_employees=100,
            revenue=None,
        )
        assert employees == 100
        assert is_interpolated is False

    def test_employees_use_last_known(self):
        """If timeline available, use last known value."""
        engine = InterpolationEngine()
        timeline = [
            {"year": 2022, "employees": 50},
            {"year": 2024, "employees": 100},
        ]
        employees, is_interpolated = engine.interpolate_employees(
            employee_timeline=timeline,
            current_employees=None,
            revenue=None,
        )
        assert employees == 100  # Last known
        assert is_interpolated is True

    def test_employees_estimate_from_revenue(self):
        """If no timeline, estimate from revenue."""
        engine = InterpolationEngine()
        employees, is_interpolated = engine.interpolate_employees(
            employee_timeline=None,
            current_employees=None,
            revenue=450000.0,  # €450M (in thousands)
        )
        # 450 * 0.0003 = 135
        assert employees == 135
        assert is_interpolated is True

    def test_employees_no_data(self):
        """If no timeline and no revenue, return None."""
        engine = InterpolationEngine()
        employees, is_interpolated = engine.interpolate_employees(
            employee_timeline=None,
            current_employees=None,
            revenue=None,
        )
        assert employees is None
        assert is_interpolated is False

    def test_validate_non_interpolated(self):
        """Non-interpolated values should always be valid."""
        engine = InterpolationEngine()
        assert engine.validate_interpolation(100.0, 100.0, False) is True

    def test_validate_negative_interpolated(self):
        """Negative interpolated values should be invalid."""
        engine = InterpolationEngine()
        assert engine.validate_interpolation(None, -10.0, True) is False

    def test_validate_null_interpolated(self):
        """NULL interpolated values should be invalid."""
        engine = InterpolationEngine()
        assert engine.validate_interpolation(None, None, True) is False

    def test_scenario_revenue_interpolation(self):
        """Scenario: Interpolate revenue from timeline."""
        engine = InterpolationEngine()
        timeline = [
            {"year": 2022, "revenue": 10.0},
            {"year": 2024, "revenue": 15.0},
        ]
        revenue, is_interpolated = engine.interpolate_revenue(
            revenue_timeline=timeline,
            current_revenue=None,
        )
        assert is_interpolated is True
        assert 12.0 <= revenue <= 12.5

    def test_scenario_growth_calculation(self):
        """Scenario: Calculate growth from revenue timeline."""
        engine = InterpolationEngine()
        timeline = [
            {"year": 2022, "revenue": 10.0},
            {"year": 2024, "revenue": 15.0},
        ]
        growth, is_interpolated = engine.interpolate_growth_rate(
            revenue_timeline=timeline,
            current_growth=None,
        )
        assert is_interpolated is True
        assert 22.0 <= growth <= 23.0

    def test_scenario_employee_estimation(self):
        """Scenario: Estimate employees from revenue."""
        engine = InterpolationEngine()
        employees, is_interpolated = engine.interpolate_employees(
            employee_timeline=None,
            current_employees=None,
            revenue=450000.0,  # €450M (in thousands)
        )
        assert is_interpolated is True
        assert employees == 135

    def test_global_instance(self):
        """Global interpolation_engine instance should exist."""
        from solstein.data.interpolation import interpolation_engine
        assert interpolation_engine is not None
        assert isinstance(interpolation_engine, InterpolationEngine)
