"""
Optimal Power Configuration for AI Data Center Loads

This module defines the optimal power architecture to meet AI customer demands,
specifically addressing:
1. Extreme load swings (25-75%, second-by-second to millisecond-scale)
2. Load management and smoothing (NOT generation capacity)
3. Hardware stress reduction and equipment wear prevention
4. Second-by-second availability measurement (99.9%+ uptime)
5. Real-time performance requirements

Key Insight: The problem is LOAD MANAGEMENT AND SMOOTHING, not generation capacity.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import json


class PowerSourceType(Enum):
    """Types of power generation and storage sources"""
    # Energy Storage (Load Smoothing)
    LITHIUM_ION_BATTERY = "lithium_ion_battery"
    ULTRA_CAPACITOR = "ultra_capacitor"
    FLOW_BATTERY = "flow_battery"
    HYDROGEN_STORAGE = "hydrogen_storage"

    # Base Load Generation (Efficiency)
    COMBINED_CYCLE_GAS = "combined_cycle_gas"
    NUCLEAR = "nuclear"
    GEOTHERMAL = "geothermal"

    # Peak/Fast Response (Speed)
    SIMPLE_CYCLE_GAS = "simple_cycle_gas"
    AERODERIVATIVE_TURBINE = "aeroderivative_turbine"
    RECIPROCATING_ENGINE = "reciprocating_engine"

    # Renewable (Sustainability)
    SOLAR_PV = "solar_pv"
    WIND = "wind"

    # Grid Connection
    GRID_UTILITY = "grid_utility"


class AvailabilityTier(Enum):
    """Availability tiers for contract requirements"""
    THREE_NINES = "99.9"      # 8.76 hours downtime/year
    FOUR_NINES = "99.99"      # 52.56 minutes downtime/year
    FIVE_NINES = "99.999"     # 5.26 minutes downtime/year
    SIX_NINES = "99.9999"     # 31.5 seconds downtime/year


class LoadProfile(Enum):
    """AI workload load profiles"""
    TRAINING = "training"              # High sustained load with occasional spikes
    INFERENCE = "inference"            # Bursty, highly variable load
    MIXED = "mixed"                    # Combination of training and inference
    BATCH = "batch"                    # Scheduled batch jobs with predictable patterns


@dataclass
class PowerSource:
    """Individual power source configuration"""
    source_type: PowerSourceType
    capacity_mw: float
    ramp_rate_mw_per_sec: float        # How fast it can change output
    response_time_ms: int               # Time to start responding
    duration_hours: Optional[float] = None  # For storage: hours at full capacity
    efficiency_percent: float = 100.0
    availability_percent: float = 99.0
    capex_per_kw: Optional[float] = None
    opex_per_kwh: Optional[float] = None
    carbon_intensity_kg_co2_per_mwh: float = 0.0
    maintenance_interval_hours: int = 8760  # Default: annual

    def can_handle_swing(self, swing_mw: float, swing_duration_sec: float) -> bool:
        """Check if this source can handle a given load swing"""
        max_swing = self.ramp_rate_mw_per_sec * swing_duration_sec
        return max_swing >= swing_mw and self.capacity_mw >= swing_mw


@dataclass
class LoadSmoothingConfig:
    """Configuration for load smoothing and management system"""
    # Primary load buffer (millisecond to second scale)
    ultra_capacitor_mw: float = 50.0
    ultra_capacitor_duration_sec: float = 30.0

    # Secondary load buffer (second to minute scale)
    fast_battery_mw: float = 200.0
    fast_battery_duration_hours: float = 0.5  # 30 minutes

    # Tertiary load buffer (minute to hour scale)
    energy_battery_mw: float = 300.0
    energy_battery_duration_hours: float = 4.0

    # Control system parameters
    prediction_horizon_sec: int = 60
    control_loop_frequency_hz: int = 10  # 10 Hz = 100ms updates
    max_allowed_ramp_rate_mw_per_sec: float = 10.0

    # Safety margins
    reserve_margin_percent: float = 20.0
    n_minus_1_redundancy: bool = True  # System works with one component failure


@dataclass
class AvailabilityConfig:
    """Configuration for availability monitoring and guarantees"""
    target_tier: AvailabilityTier = AvailabilityTier.FOUR_NINES
    measurement_interval_sec: int = 1  # Second-by-second measurement
    max_outage_duration_sec: int = 10
    liquidated_damages_per_sec: float = 1000.0  # $/second for outages

    # Redundancy configuration
    redundant_power_paths: int = 2  # N+1 redundancy
    redundant_cooling_paths: int = 2
    redundant_network_paths: int = 2

    # Monitoring
    telemetry_frequency_hz: int = 100  # 100 Hz monitoring
    alert_threshold_sec: float = 0.1   # Alert if power quality degrades >100ms


@dataclass
class OptimalPowerConfig:
    """
    Optimal power configuration for AI data center loads.

    This configuration addresses the core challenge: LOAD MANAGEMENT AND SMOOTHING
    for AI workloads with extreme, fast load swings (25-75%, second-by-second to
    millisecond-scale).

    Architecture Philosophy:
    1. SMOOTHING FIRST: Multi-tier energy storage to absorb rapid load swings
    2. EFFICIENCY SECOND: Base load from efficient combined-cycle or other efficient sources
    3. RELIABILITY THIRD: Redundancy and fast failover for availability guarantees
    4. SUSTAINABILITY: Integrate renewables where possible without compromising stability
    """

    # Basic parameters
    name: str
    total_it_load_mw: float
    expected_load_swing_percent: float = 50.0  # 25-75% = 50% swing
    load_profile: LoadProfile = LoadProfile.MIXED
    availability_tier: AvailabilityTier = AvailabilityTier.FOUR_NINES

    # Load smoothing configuration (MOST CRITICAL)
    load_smoothing: LoadSmoothingConfig = field(default_factory=LoadSmoothingConfig)

    # Power sources
    power_sources: List[PowerSource] = field(default_factory=list)

    # Availability configuration
    availability: AvailabilityConfig = field(default_factory=AvailabilityConfig)

    # Grid integration
    grid_connected: bool = True
    grid_capacity_mw: float = 0.0
    can_sell_to_grid: bool = False
    can_provide_frequency_regulation: bool = True

    # Operating parameters
    target_pue: float = 1.2  # Power Usage Effectiveness
    cooling_overhead_percent: float = 20.0

    def __post_init__(self):
        """Validate and auto-configure based on IT load"""
        self.availability.target_tier = self.availability_tier

        # Auto-configure load smoothing if not set
        if not self.power_sources:
            self._auto_configure_power_sources()

    def _auto_configure_power_sources(self):
        """Automatically configure optimal power sources based on IT load"""
        # Calculate total power need including cooling
        total_power_mw = self.total_it_load_mw * (1 + self.cooling_overhead_percent / 100)
        max_swing_mw = total_power_mw * (self.expected_load_swing_percent / 100)

        # 1. LOAD SMOOTHING LAYER (MOST CRITICAL)
        # Ultra-capacitors for millisecond-scale smoothing (10% of max swing)
        self.power_sources.append(PowerSource(
            source_type=PowerSourceType.ULTRA_CAPACITOR,
            capacity_mw=max_swing_mw * 0.1,
            ramp_rate_mw_per_sec=max_swing_mw * 0.1 / 0.001,  # Full capacity in 1ms
            response_time_ms=1,
            duration_hours=30 / 3600,  # 30 seconds
            efficiency_percent=95.0,
            availability_percent=99.99,
            capex_per_kw=500,
            opex_per_kwh=0.001
        ))

        # Fast Li-ion batteries for second-scale smoothing (50% of max swing)
        self.power_sources.append(PowerSource(
            source_type=PowerSourceType.LITHIUM_ION_BATTERY,
            capacity_mw=max_swing_mw * 0.5,
            ramp_rate_mw_per_sec=max_swing_mw * 0.5 / 0.1,  # Full capacity in 100ms
            response_time_ms=10,
            duration_hours=0.5,  # 30 minutes
            efficiency_percent=92.0,
            availability_percent=99.9,
            capex_per_kw=800,
            opex_per_kwh=0.01
        ))

        # Energy Li-ion batteries for minute-scale smoothing (75% of total load)
        self.power_sources.append(PowerSource(
            source_type=PowerSourceType.LITHIUM_ION_BATTERY,
            capacity_mw=total_power_mw * 0.75,
            ramp_rate_mw_per_sec=total_power_mw * 0.75 / 1.0,  # Full capacity in 1 second
            response_time_ms=50,
            duration_hours=4.0,
            efficiency_percent=90.0,
            availability_percent=99.9,
            capex_per_kw=600,
            opex_per_kwh=0.015
        ))

        # 2. BASE LOAD GENERATION (EFFICIENCY)
        # Combined-cycle gas turbine for efficient base load (60% of average load)
        avg_load_mw = total_power_mw * (1 - self.expected_load_swing_percent / 200)
        self.power_sources.append(PowerSource(
            source_type=PowerSourceType.COMBINED_CYCLE_GAS,
            capacity_mw=avg_load_mw * 0.6,
            ramp_rate_mw_per_sec=avg_load_mw * 0.6 / 600,  # 10 minutes to full
            response_time_ms=60000,  # 1 minute
            efficiency_percent=60.0,  # 60% thermal efficiency
            availability_percent=95.0,
            capex_per_kw=1200,
            opex_per_kwh=0.04,
            carbon_intensity_kg_co2_per_mwh=400,
            maintenance_interval_hours=4380  # Semi-annual
        ))

        # 3. PEAK/FAST RESPONSE GENERATION
        # Aeroderivative gas turbine for fast response (40% of total load)
        self.power_sources.append(PowerSource(
            source_type=PowerSourceType.AERODERIVATIVE_TURBINE,
            capacity_mw=total_power_mw * 0.4,
            ramp_rate_mw_per_sec=total_power_mw * 0.4 / 30,  # 30 seconds to full
            response_time_ms=5000,  # 5 seconds
            efficiency_percent=42.0,
            availability_percent=97.0,
            capex_per_kw=900,
            opex_per_kwh=0.06,
            carbon_intensity_kg_co2_per_mwh=500,
            maintenance_interval_hours=2190  # Quarterly
        ))

        # 4. GRID CONNECTION (if enabled)
        if self.grid_connected:
            self.grid_capacity_mw = total_power_mw * 0.5  # 50% grid capacity
            self.power_sources.append(PowerSource(
                source_type=PowerSourceType.GRID_UTILITY,
                capacity_mw=self.grid_capacity_mw,
                ramp_rate_mw_per_sec=self.grid_capacity_mw / 10,  # 10 second response
                response_time_ms=100,
                efficiency_percent=98.0,  # Transmission efficiency
                availability_percent=99.5,
                opex_per_kwh=0.08,  # Grid electricity cost
                carbon_intensity_kg_co2_per_mwh=450  # Average grid mix
            ))

    def get_total_capacity_mw(self) -> float:
        """Get total installed power capacity"""
        return sum(source.capacity_mw for source in self.power_sources)

    def get_total_storage_capacity_mwh(self) -> float:
        """Get total energy storage capacity in MWh"""
        storage_types = {
            PowerSourceType.LITHIUM_ION_BATTERY,
            PowerSourceType.ULTRA_CAPACITOR,
            PowerSourceType.FLOW_BATTERY,
            PowerSourceType.HYDROGEN_STORAGE
        }
        return sum(
            source.capacity_mw * (source.duration_hours or 0)
            for source in self.power_sources
            if source.source_type in storage_types
        )

    def get_fastest_response_time_ms(self) -> int:
        """Get fastest response time across all sources"""
        return min(source.response_time_ms for source in self.power_sources)

    def get_max_ramp_rate_mw_per_sec(self) -> float:
        """Get maximum ramp rate across all sources"""
        return sum(source.ramp_rate_mw_per_sec for source in self.power_sources)

    def can_handle_load_swing(self, swing_percent: float, duration_sec: float) -> bool:
        """Check if configuration can handle a given load swing"""
        swing_mw = self.total_it_load_mw * (swing_percent / 100)

        # Check if any combination of sources can handle the swing
        available_ramp = sum(
            source.ramp_rate_mw_per_sec * duration_sec
            for source in self.power_sources
            if source.response_time_ms / 1000 <= duration_sec
        )

        return available_ramp >= swing_mw

    def get_estimated_capex(self) -> float:
        """Get estimated capital expenditure in $"""
        return sum(
            (source.capex_per_kw or 0) * source.capacity_mw * 1000
            for source in self.power_sources
        )

    def get_estimated_annual_opex(self) -> float:
        """Get estimated annual operating expenditure in $ (rough estimate)"""
        # Assume 50% average utilization, 8760 hours/year
        return sum(
            (source.opex_per_kwh or 0) * source.capacity_mw * 1000 * 8760 * 0.5
            for source in self.power_sources
        )

    def get_carbon_intensity(self) -> float:
        """Get average carbon intensity in kg CO2/MWh"""
        total_capacity = self.get_total_capacity_mw()
        if total_capacity == 0:
            return 0.0

        weighted_carbon = sum(
            source.carbon_intensity_kg_co2_per_mwh * source.capacity_mw
            for source in self.power_sources
        )
        return weighted_carbon / total_capacity

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            'name': self.name,
            'total_it_load_mw': self.total_it_load_mw,
            'expected_load_swing_percent': self.expected_load_swing_percent,
            'load_profile': self.load_profile.value,
            'availability_tier': self.availability_tier.value,
            'grid_connected': self.grid_connected,
            'grid_capacity_mw': self.grid_capacity_mw,
            'target_pue': self.target_pue,
            'power_sources': [
                {
                    'type': source.source_type.value,
                    'capacity_mw': source.capacity_mw,
                    'ramp_rate_mw_per_sec': source.ramp_rate_mw_per_sec,
                    'response_time_ms': source.response_time_ms,
                    'duration_hours': source.duration_hours,
                    'efficiency_percent': source.efficiency_percent
                }
                for source in self.power_sources
            ],
            'metrics': {
                'total_capacity_mw': self.get_total_capacity_mw(),
                'total_storage_mwh': self.get_total_storage_capacity_mwh(),
                'fastest_response_ms': self.get_fastest_response_time_ms(),
                'max_ramp_rate_mw_per_sec': self.get_max_ramp_rate_mw_per_sec(),
                'estimated_capex': self.get_estimated_capex(),
                'estimated_annual_opex': self.get_estimated_annual_opex(),
                'carbon_intensity_kg_co2_per_mwh': self.get_carbon_intensity()
            }
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert configuration to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    def print_summary(self):
        """Print a human-readable summary of the configuration"""
        print(f"\n{'='*80}")
        print(f"OPTIMAL POWER CONFIGURATION: {self.name}")
        print(f"{'='*80}\n")

        print(f"IT Load: {self.total_it_load_mw:.1f} MW")
        print(f"Expected Load Swing: ±{self.expected_load_swing_percent}%")
        print(f"Load Profile: {self.load_profile.value}")
        print(f"Availability Tier: {self.availability_tier.value}% uptime")
        print(f"Target PUE: {self.target_pue}")

        print(f"\n{'-'*80}")
        print("POWER SOURCES")
        print(f"{'-'*80}\n")

        for i, source in enumerate(self.power_sources, 1):
            print(f"{i}. {source.source_type.value.replace('_', ' ').title()}")
            print(f"   Capacity: {source.capacity_mw:.1f} MW")
            print(f"   Ramp Rate: {source.ramp_rate_mw_per_sec:.2f} MW/sec")
            print(f"   Response Time: {source.response_time_ms} ms")
            if source.duration_hours:
                print(f"   Duration: {source.duration_hours:.2f} hours")
            print(f"   Efficiency: {source.efficiency_percent:.1f}%")
            print()

        print(f"{'-'*80}")
        print("SYSTEM METRICS")
        print(f"{'-'*80}\n")

        print(f"Total Capacity: {self.get_total_capacity_mw():.1f} MW")
        print(f"Total Storage: {self.get_total_storage_capacity_mwh():.1f} MWh")
        print(f"Fastest Response: {self.get_fastest_response_time_ms()} ms")
        print(f"Max Ramp Rate: {self.get_max_ramp_rate_mw_per_sec():.1f} MW/sec")

        print(f"\n{'-'*80}")
        print("FINANCIAL & ENVIRONMENTAL")
        print(f"{'-'*80}\n")

        capex = self.get_estimated_capex()
        opex = self.get_estimated_annual_opex()
        print(f"Estimated CapEx: ${capex/1e6:.1f}M")
        print(f"Estimated Annual OpEx: ${opex/1e6:.1f}M")
        print(f"Carbon Intensity: {self.get_carbon_intensity():.0f} kg CO₂/MWh")

        print(f"\n{'-'*80}")
        print("LOAD SWING CAPABILITY")
        print(f"{'-'*80}\n")

        test_cases = [
            (50, 0.001, "50% swing in 1ms"),
            (50, 0.1, "50% swing in 100ms"),
            (50, 1.0, "50% swing in 1 second"),
            (75, 1.0, "75% swing in 1 second"),
            (25, 0.01, "25% swing in 10ms")
        ]

        for swing_pct, duration, desc in test_cases:
            can_handle = self.can_handle_load_swing(swing_pct, duration)
            status = "✓ CAN HANDLE" if can_handle else "✗ CANNOT HANDLE"
            print(f"{status}: {desc}")

        print(f"\n{'='*80}\n")


def create_small_ai_config(name: str = "Small AI Datacenter (50 MW)") -> OptimalPowerConfig:
    """Create optimal config for small AI datacenter (50 MW IT load)"""
    return OptimalPowerConfig(
        name=name,
        total_it_load_mw=50.0,
        expected_load_swing_percent=50.0,
        load_profile=LoadProfile.MIXED,
        availability_tier=AvailabilityTier.FOUR_NINES,
        grid_connected=True,
        target_pue=1.15
    )


def create_medium_ai_config(name: str = "Medium AI Datacenter (200 MW)") -> OptimalPowerConfig:
    """Create optimal config for medium AI datacenter (200 MW IT load)"""
    return OptimalPowerConfig(
        name=name,
        total_it_load_mw=200.0,
        expected_load_swing_percent=50.0,
        load_profile=LoadProfile.TRAINING,
        availability_tier=AvailabilityTier.FOUR_NINES,
        grid_connected=True,
        target_pue=1.12
    )


def create_large_ai_config(name: str = "Large AI Datacenter (500 MW)") -> OptimalPowerConfig:
    """Create optimal config for large AI datacenter (500 MW IT load)"""
    return OptimalPowerConfig(
        name=name,
        total_it_load_mw=500.0,
        expected_load_swing_percent=50.0,
        load_profile=LoadProfile.MIXED,
        availability_tier=AvailabilityTier.FIVE_NINES,
        grid_connected=True,
        target_pue=1.10
    )


def create_hyperscale_ai_config(name: str = "Hyperscale AI Datacenter (1000 MW)") -> OptimalPowerConfig:
    """Create optimal config for hyperscale AI datacenter (1 GW IT load)"""
    return OptimalPowerConfig(
        name=name,
        total_it_load_mw=1000.0,
        expected_load_swing_percent=40.0,  # Slightly lower swing due to diversity
        load_profile=LoadProfile.MIXED,
        availability_tier=AvailabilityTier.FIVE_NINES,
        grid_connected=True,
        can_sell_to_grid=True,
        can_provide_frequency_regulation=True,
        target_pue=1.08
    )


if __name__ == "__main__":
    # Example: Create and display optimal configurations for different scales

    print("\n" + "="*80)
    print("OPTIMAL POWER CONFIGURATIONS FOR AI DATA CENTERS")
    print("="*80)
    print("\nKey Principle: LOAD MANAGEMENT AND SMOOTHING > Generation Capacity")
    print("\nThese configurations address:")
    print("  • Extreme load swings (25-75%, second-by-second to millisecond-scale)")
    print("  • Equipment stress and wear prevention")
    print("  • Second-by-second availability measurement")
    print("  • Real-time performance requirements")
    print("="*80)

    # Small datacenter
    small_config = create_small_ai_config()
    small_config.print_summary()

    # Medium datacenter
    medium_config = create_medium_ai_config()
    medium_config.print_summary()

    # Large datacenter
    large_config = create_large_ai_config()
    large_config.print_summary()

    # Hyperscale datacenter
    hyperscale_config = create_hyperscale_ai_config()
    hyperscale_config.print_summary()

    # Export example configuration to JSON
    print("\nExample JSON Export (Medium Config):")
    print("="*80)
    print(medium_config.to_json())
